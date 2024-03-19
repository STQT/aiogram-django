from modeltranslation.translator import translator, TranslationOptions

from .models import Notification


class NotificationTranslationOptions(TranslationOptions):
    fields = ['description']


translator.register(Notification, NotificationTranslationOptions)
