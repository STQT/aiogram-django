from django.conf import settings
from django.urls import reverse


def get_webhook_url():
    host: str = settings.HOST
    if host.endswith("/"):
        host = host[:-1]
    return host + reverse(settings.BOT_WEBHOOK_PATH, args=(settings.BOT_TOKEN,))


def format_phone_number(phone_number):
    phone_number = phone_number.strip().replace(" ", "")
    if phone_number.startswith('+'):
        return phone_number
    else:
        if len(phone_number) == 9:
            return "+998" + phone_number
        return '+' + phone_number
