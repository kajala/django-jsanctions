from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class JsanctionsConfig(AppConfig):
    name = "jsanctions"
    verbose_name = _("Sanction Lists")
    default_auto_field = "django.db.models.AutoField"
