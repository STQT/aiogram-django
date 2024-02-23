from modeltranslation.translator import translator, TranslationOptions

from .models import Promotion


class PromotionTranslationOptions(TranslationOptions):
    fields = ['name', 'description', 'conditions']


translator.register(Promotion, PromotionTranslationOptions)
