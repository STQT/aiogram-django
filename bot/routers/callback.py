from aiogram import Router, types, F
from django.utils.translation import gettext_lazy as _

from app.promotions.models import Promotion

router = Router()


@router.callback_query(F.data.startswith("about_"))
async def get_about_id(callback: types.CallbackQuery):
    _about, promo_id = callback.data.split("about_")
    promotion = await Promotion.objects.filter(pk=promo_id).afirst()
    if promotion:
        await callback.answer(promotion.name)
        await callback.message.answer(promotion.conditions)
    else:
        await callback.answer(str(_("Отсутствует")))
    await callback.message.delete()
