import json
import time
import requests
from urllib.parse import unquote

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync

from aiogram.types import ReplyKeyboardRemove
from aiogram.exceptions import TelegramForbiddenError
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey

from celery import shared_task
from celery.utils.log import get_task_logger
from django.conf import settings
from django.db.models import F

from app.users.models import TelegramUser, Notification, PeriodicallyNotification
from bot.utils.storage import DjangoRedisStorage
from bot.filters.states import Registration
from bot.misc import bot, bot_session
from bot.utils.kbs import contact_kb, language_kb

User = get_user_model()


@shared_task()
def get_users_count():
    """A pointless Celery task to demonstrate usage."""
    return User.objects.count()


async def return_hello():
    current_time = timezone.now()
    lang = TelegramUser.objects.filter(language__isnull=True)
    phone = TelegramUser.objects.filter(phone__isnull=True)
    fullname = TelegramUser.objects.filter(fullname__isnull=True)
    all_active_users = lang | phone | fullname
    all_active_users = all_active_users.filter(
        is_active=True).filter(updated_at__lt=current_time - timezone.timedelta(hours=1))
    async for user in all_active_users:
        storage_key = StorageKey(
            user_id=user.id,
            chat_id=user.id,
            bot_id=bot.id,
            destiny='default'
        )
        state = FSMContext(DjangoRedisStorage(bot),
                           key=storage_key)
        try:
            if not user.language:
                await state.set_state(Registration.language)
                await bot.send_message(user.id,
                                       str(_("Завершите регистрацию, чтобы участвовать в розыгрыше. \n"
                                             "Это займет всего несколько минут.")),
                                       reply_markup=language_kb())
            elif not user.fullname:
                await state.set_state(Registration.fio)
                await bot.send_message(user.id,
                                       str(_("Вы забыли указать Ваше имя! \n"
                                             "Пожалуйста, заполните его для продолжения регистрации.")),
                                       reply_markup=ReplyKeyboardRemove())
            elif not user.phone:
                await state.set_state(Registration.phone)
                await bot.send_message(user.id,
                                       str(_("Остался всего один шаг! \n"
                                             "Введите номер телефона, чтобы завершить регистрацию и ввести "
                                             "промо-код для участия в розыгрыше.")),
                                       reply_markup=contact_kb())
        except TelegramForbiddenError:
            user.is_active = False
            await user.asave()
    await bot_session.close()
    return 'hello'


@shared_task()
def sync_task():
    async_to_sync(return_hello)()


api_token = settings.BOT_TOKEN
base_url = f'https://api.telegram.org/bot{api_token}'
SEND_MEDIA_GROUP = f"https://api.telegram.org/bot{api_token}/sendMediaGroup"

logger = get_task_logger(__name__)


def send_media_group(text, chat_id, media):
    files = {}
    media_list = []
    for i, img_path_encoded in enumerate(media):
        img_path = unquote(img_path_encoded)
        try:
            with open(img_path, "rb") as img:
                files[f'photo{i}'] = img.read()
                media_list.append({'type': 'photo', 'media': f'attach://photo{i}'})
        except FileNotFoundError:
            print(f"File not found: {img_path}. Skipping...")
            continue
    if not media_list:
        print("No valid files found. Aborting send_media_group.")
        return None
    media_list[0]['caption'] = text
    media_list[0]['parse_mode'] = 'HTML'

    payload = {'chat_id': chat_id, 'media': json.dumps(media_list)}
    resp = requests.post(SEND_MEDIA_GROUP, data=payload, files=files)
    return resp.status_code


def send_notifications_text(text, chat_id, media=None):
    url = f'https://api.telegram.org/bot{api_token}/sendMessage'
    data = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    response = requests.post(url, data=data)
    return response.status_code


@shared_task()
def send_notifications_task(notification_id, text, media, offset, chunk_size, is_notification=True):
    chunk_chats = TelegramUser.objects.filter(is_active=True).order_by('id')[offset:offset + chunk_size]
    text = text.replace("<br />", "\n")
    for chat in chunk_chats:
        send_notification_bound = send_media_group if media else send_notifications_text
        response = send_notification_bound(text=text, chat_id=chat.id, media=media)
        time.sleep(0.035)
        if response != 200:
            chat.is_active = False  # Reset is_stopped flag if the message was sent successfully
            chat.save()
    if is_notification:
        Notification.objects.filter(id=notification_id).update(
            all_chats=F('all_chats') + chunk_chats.count(),
            status=Notification.NotificationStatus.SENDED
        )


# @shared_task()
# def scheduled_send_periodically_notification():
#     periodically_notification = PeriodicallyNotification.objects.filter(is_current=True)
#     if periodically_notification.exists():
#         periodically_notification = periodically_notification.first()
#         media = []
#         cache_path = settings.MEDIA_ROOT
#         for i in periodically_notification.periodic_shots.all():
#             compressed_image = i.image_compress.url
#             compressed_image_path = cache_path + compressed_image[len(settings.MEDIA_URL):]
#             media.append(compressed_image_path)
#         chunk_size = 200
#         offset = 0
#
#         first_task = None
#
#         while True:
#             chunk_chats = TelegramUser.objects.filter(is_active=True).order_by('id')[offset:offset + chunk_size]
#
#             if not chunk_chats:
#                 break
#
#             task = send_notifications_task.signature(
#                 (periodically_notification.pk,
#                  periodically_notification.description,
#                  media,
#                  offset,
#                  chunk_size,
#                  False),
#                 immutable=True)
#
#             if first_task:
#                 first_task |= task
#             else:
#                 first_task = task
#
#             offset += chunk_size
#         first_task.apply_async()
#         return {"message": "Periodically notifications task was started"}
#     return {"message": "No periodically notifications"}
