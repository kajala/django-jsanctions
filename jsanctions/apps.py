from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SanctionsConfig(AppConfig):
    name = 'jsanctions'
    verbose_name = _('Sanction Lists')
