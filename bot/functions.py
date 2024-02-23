from dataclasses import dataclass

from aiogram.types import Message
from django.utils.translation import gettext_lazy as _
from app.promotions.models import PromotionCode
from bot.utils.kbs import menu_kb
from bot.validators import validate_code
from app.users.models import TelegramUser as User


@dataclass
class RegisterPromo:
    CREATED = 1
    REGISTERED = 2
    ERROR = 3
    NO_PROMOTION = 4


async def register_promo(message, code, promo_id=None):
    if promo_id is None:  # Checking validated
        is_valid, promo_id = await validate_code(message, code)
    else:
        is_valid = True
    if is_valid:
        promo, created = await PromotionCode.objects.aget_or_create(
            code=code,
            defaults={
                "user_id": message.from_user.id,
                "promotion_id": promo_id})
        if created:
            return RegisterPromo.CREATED
        return RegisterPromo.REGISTERED
    return RegisterPromo.ERROR


async def send_registered_message(message: Message, promo, lang='ru', promo_id=None):
    created = await register_promo(message, promo, promo_id)
    if created == RegisterPromo.CREATED:
        await message.answer(
            str(_("Ваш промокод успешно зарегистрирован!")),
            reply_markup=menu_kb(lang)
        )
    elif created == RegisterPromo.REGISTERED:
        await message.answer(
            str(_("Ваш промокод уже имеется в нашей базе!")),
            reply_markup=menu_kb(lang)
        )
    elif created == RegisterPromo.ERROR:
        await message.answer(str(_("Неправильное значение промо кода. \n"
                                   "Пожалуйста, перепроверьте введенный промо-код и введите значение заново.")),
                             reply_markup=menu_kb(lang))
    else:
        await message.answer(str(_("Не найдена активная акция на сегодня")), reply_markup=menu_kb(lang))


async def get_all_user_promocodes(user: User):
    codes = []
    async for code in PromotionCode.objects.filter(user=user).select_related("promotion"):
        codes.append(code)
    return codes
