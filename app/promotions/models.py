from django.db import models
from django.utils.translation import gettext_lazy as _

from app.users.models import TelegramUser


class Promotion(models.Model):
    name = models.CharField(_("Название"), max_length=100)
    description = models.TextField(_("Описание"))
    mask = models.CharField(_("Начальные символы (маска)"))
    start_date = models.DateField(_("Дата начала"))
    end_date = models.DateField(_("Дата окончания"))
    is_active = models.BooleanField(_("Активна"), default=True)
    conditions = models.TextField(_("Условия"))

    class Meta:
        verbose_name = _("Промо-акция")
        verbose_name_plural = _("Промо-акции")

    def __str__(self):
        return self.name

    # def clean(self):
    #     existing_promotion = Promotion.objects.filter(
    #         start_date__lte=self.end_date,
    #         end_date__gte=self.start_date,
    #     ).exclude(pk=self.pk)
    #
    #     if existing_promotion.exists():
    #         raise ValidationError(
    #             {'start_date': _('Для указанного периода уже существует активная акция.')}
    #         )


class PromotionCode(models.Model):
    promotion = models.ForeignKey(Promotion, on_delete=models.CASCADE, verbose_name=_("Промо-акция"))
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, verbose_name=_("Пользователь"))
    code = models.CharField(_("Код промо-акции"), max_length=50, unique=True, db_index=True)
    created_at = models.DateTimeField(verbose_name=_("Дата создания"), auto_now_add=True)

    class Meta:
        verbose_name = _("Код промо-акции")
        verbose_name_plural = _("Коды промо-акции")

    def __str__(self):
        return self.code
