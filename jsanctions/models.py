import logging
import os
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from jutil.parse import parse_datetime
from jutil.xml import xml_to_dict
from jsanctions.helpers import xml_dict_filter_attributes


logger = logging.getLogger(__name__)


REMARK_BRIEF_LENGTH = 128
DEFAULT_DESCRIPTION_TYPE = {'blank': True, 'max_length': 512, 'default': ''}
DEFAULT_REMARK_TYPE = {'verbose_name':_('remark'), 'null': True, 'default': None, 'blank': True, 'on_delete': models.SET_NULL}
DEFAULT_CODE_TYPE = {'blank': True, 'max_length': 32, 'default': ''}
DEFAULT_DATE_TYPE = {'blank': True, 'null': True, 'default': None}
LANGUAGE_CODE_TYPE = {'blank': True, 'default': '', 'max_length': 5}
COUNTRY_CODE_TYPE = {'blank': True, 'default': '', 'max_length': 3}
DEFAULT_BOOLEAN_TYPE = {'blank': True, 'default': None, 'null': True}
DEFAULT_INT_TYPE = {'blank': True, 'default': None, 'null': True}
REGULATION_SUMMARY_TYPE = {'verbose_name': _('regulation summary'), 'blank': True, 'default': None, 'null': True, 'on_delete': models.PROTECT}
EU_XML_ARRAY_TAGS = [
    'sanctionEntity',
    'nameAlias',
    'identification',
    'address',
    'birthdate',
    'citizenship',
    'regulation',
    'remark',
]
EU_XML_INT_TAGS = [
]
EU_XML_DATE_ATTRIBUTES = [
    '@birthdate',
]


class SanctionsListFileManager(models.Manager):
    def create_from_filename(self, filename: str, **kwargs):
        with open(filename, 'rb') as fp:
            plain_filename = os.path.basename(filename)
            file = self.create(**kwargs)
            file.file.save(plain_filename, File(fp))
            return file

    def create_from_url(self, url: str, filename: str, **kwargs):
        import urllib.request
        response = urllib.request.urlopen(url)
        body = response.read()
        plain_filename = os.path.basename(filename)
        file = self.create(**kwargs)
        file.file.save(plain_filename, ContentFile(body))
        return file


class SanctionListObject(models.Model):
    pass


class SanctionsListFile(SanctionListObject):
    objects = SanctionsListFileManager()
    created = models.DateTimeField(_('created'), default=now, blank=True, editable=False, db_index=True)
    imported = models.DateTimeField(_('imported'), default=None, null=True, blank=True, editable=False, db_index=True)
    generation_date = models.DateField(_('generation date'), default=None, blank=True, null=True, editable=False, db_index=True)
    file = models.FileField(_('file'), upload_to='uploads')

    class Meta:
        verbose_name = _('sanction list')
        verbose_name_plural = _('sanction lists')

    def __str__(self):
        return '{}'.format(os.path.basename(self.file.name))

    @property
    def full_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.file.name)


class EuCombinedSanctionsList(SanctionsListFile):
    objects = SanctionsListFileManager()
    global_file_id = models.CharField(_('global file id'), **DEFAULT_DESCRIPTION_TYPE)

    class Meta:
        verbose_name = _('EU combined sanction list')
        verbose_name_plural = _('EU combined sanction lists')

    def __str__(self):
        return '{}'.format(os.path.basename(self.file.name))

    def load_xml_as_dict(self) -> dict:
        with open(self.full_path, 'rb') as fp:
            data = xml_to_dict(fp.read(), array_tags=EU_XML_ARRAY_TAGS, int_tags=EU_XML_INT_TAGS)
            data = xml_dict_filter_attributes(data, self._xml_filter_attributes)
            return data

    @staticmethod
    def _xml_filter_attributes(k, v):
        if k.endswith('Date') or k in EU_XML_DATE_ATTRIBUTES:
            return parse_datetime(v).date()
        if k == '@logicalId':
            return int(v)
        if v == 'false':
            return False
        if v == 'true':
            return True
        return v


class Remark(models.Model):
    container = models.ForeignKey(SanctionListObject, on_delete=models.CASCADE)
    text = models.TextField(_('text'), blank=True)

    class Meta:
        verbose_name = _('remark')
        verbose_name_plural = _('remarks')

    def __str__(self) -> str:
        return str(self.text)

    @property
    def text_brief(self) -> str:
        return self.text if len(self.text) < REMARK_BRIEF_LENGTH else self.text[:REMARK_BRIEF_LENGTH] + '...'


class SubjectType(SanctionListObject):
    code = models.CharField(_('code'), **DEFAULT_DESCRIPTION_TYPE)
    classification_code = models.CharField(_('classification code'), **DEFAULT_CODE_TYPE)

    class Meta:
        verbose_name = _('subject type')
        verbose_name_plural = _('subject types')

    def __str__(self) -> str:
        return str(self.code)


class Regulation(SanctionListObject):
    sanction = models.ForeignKey('SanctionEntity', verbose_name=_('sanction entity'), on_delete=models.CASCADE)
    regulation_type = models.CharField(_('regulation type'), **DEFAULT_DESCRIPTION_TYPE)
    organisation_type = models.CharField(_('organization type'), **DEFAULT_DESCRIPTION_TYPE)
    publication_date = models.DateField(_('publication date'), **DEFAULT_DATE_TYPE)
    publication_url = models.URLField(_('url'), blank=True, default='')
    entry_into_force_date = models.DateField(_('entry into force date'), **DEFAULT_DATE_TYPE)
    number_title = models.CharField(_('number title'), **DEFAULT_DESCRIPTION_TYPE)
    programme = models.CharField(_('programmer'), **DEFAULT_DESCRIPTION_TYPE)
    logical_id = models.BigIntegerField(_('logical id'), blank=True, null=True, default=None)

    class Meta:
        verbose_name = _('regulation')
        verbose_name_plural = _('regulations')


class RegulationSummary(SanctionListObject):
    regulation_type = models.CharField(_('regulation type'), **DEFAULT_CODE_TYPE)
    number_title = models.CharField(_('number title'), **DEFAULT_DESCRIPTION_TYPE)
    publication_date = models.DateField(_('publication date'), **DEFAULT_DATE_TYPE)
    publication_url = models.URLField(_('url'), blank=True, default='')

    class Meta:
        verbose_name = _('regulation summary')
        verbose_name_plural = _('regulation summaries')

    def __str__(self) -> str:
        return '{} {}'.format(self.regulation_type, self.number_title)


class NameAlias(SanctionListObject):
    sanction = models.ForeignKey('SanctionEntity', verbose_name=_('sanction entity'), on_delete=models.CASCADE)
    first_name = models.CharField(_('first name'), **DEFAULT_DESCRIPTION_TYPE)
    middle_name = models.CharField(_('middle name'), **DEFAULT_DESCRIPTION_TYPE)
    last_name = models.CharField(_('last name'), **DEFAULT_DESCRIPTION_TYPE)
    whole_name = models.CharField(_('whole name'), **DEFAULT_DESCRIPTION_TYPE)
    name_language = models.CharField(_('name language'), **LANGUAGE_CODE_TYPE)
    function = models.CharField(_('function'), **DEFAULT_DESCRIPTION_TYPE)
    title = models.CharField(_('title'), **DEFAULT_DESCRIPTION_TYPE)
    regulation_language = models.CharField(_('regulation language'), **LANGUAGE_CODE_TYPE)
    logical_id = models.BigIntegerField(_('logical id'), blank=True, null=True, default=None)
    regulation_summary = models.ForeignKey(RegulationSummary, **REGULATION_SUMMARY_TYPE)

    class Meta:
        verbose_name = _('name alias')
        verbose_name_plural = _('name aliases')

    def __str__(self) -> str:
        return str(self.whole_name)

    def clean(self):
        if len(self.function) > 256:
            self.function = self.function[:256]


class Identification(SanctionListObject):
    sanction = models.ForeignKey('SanctionEntity', verbose_name=_('sanction entity'), on_delete=models.CASCADE)
    diplomatic = models.BooleanField(_('diplomatic'), **DEFAULT_BOOLEAN_TYPE)
    known_expired = models.BooleanField(_('known expired'), **DEFAULT_BOOLEAN_TYPE)
    known_false = models.BooleanField(_('known false'), **DEFAULT_BOOLEAN_TYPE)
    reported_lost = models.BooleanField(_('reported lost'), **DEFAULT_BOOLEAN_TYPE)
    revoked_by_issuer = models.BooleanField(_('revoked by issuer'), **DEFAULT_BOOLEAN_TYPE)
    issued_by = models.CharField(_('issued by'), **DEFAULT_DESCRIPTION_TYPE)
    latin_number = models.CharField(_('latin number'), **DEFAULT_DESCRIPTION_TYPE)
    name_on_document = models.CharField(_('name on document'), **DEFAULT_DESCRIPTION_TYPE)
    number = models.CharField(_('number'), **DEFAULT_DESCRIPTION_TYPE)
    region = models.CharField(_('region'), **DEFAULT_DESCRIPTION_TYPE)
    country_iso2_code = models.CharField(_('issued by'), **COUNTRY_CODE_TYPE)
    country_description = models.CharField(_('country description'), **DEFAULT_DESCRIPTION_TYPE)
    identification_type_code = models.CharField(_('identification type code'), **DEFAULT_CODE_TYPE)
    identification_type_description = models.CharField(_('identification type code'), **DEFAULT_DESCRIPTION_TYPE)
    regulation_language = models.CharField(_('regional language'), **LANGUAGE_CODE_TYPE)
    logical_id = models.BigIntegerField(_('logical id'), blank=True, null=True, default=None)
    regulation_summary = models.ForeignKey(RegulationSummary, **REGULATION_SUMMARY_TYPE)

    class Meta:
        verbose_name = _('identification')
        verbose_name_plural = _('identifications')


class BirthDate(SanctionListObject):
    sanction = models.ForeignKey('SanctionEntity', verbose_name=_('sanction entity'), on_delete=models.CASCADE)
    circa = models.BooleanField(_('circa'), **DEFAULT_BOOLEAN_TYPE)
    calendar_type = models.CharField(_('calendar type'), **DEFAULT_CODE_TYPE)
    city = models.CharField(_('city'), **DEFAULT_DESCRIPTION_TYPE)
    zip_code = models.CharField(_('zip code'), **DEFAULT_DESCRIPTION_TYPE)
    birth_date = models.DateField(_('birth date'), **DEFAULT_DATE_TYPE)
    day_of_month = models.IntegerField(_('day of month'), **DEFAULT_INT_TYPE)
    month_of_year = models.IntegerField(_('month of year'), **DEFAULT_INT_TYPE)
    year = models.IntegerField(_('year'), **DEFAULT_INT_TYPE)
    region = models.CharField(_('region'), **DEFAULT_DESCRIPTION_TYPE)
    place = models.CharField(_('place'), **DEFAULT_DESCRIPTION_TYPE)
    country_iso2_code = models.CharField(_('country'), **COUNTRY_CODE_TYPE)
    country_description = models.CharField(_('country description'), **DEFAULT_DESCRIPTION_TYPE)
    regulation_language = models.CharField(_('regional language'), **LANGUAGE_CODE_TYPE)
    logical_id = models.BigIntegerField(_('logical id'), blank=True, null=True, default=None)

    class Meta:
        verbose_name = _('birth date')
        verbose_name_plural = _('birth dates')


class Citizenship(SanctionListObject):
    sanction = models.ForeignKey('SanctionEntity', verbose_name=_('sanction entity'), on_delete=models.CASCADE)
    region = models.CharField(_('region'), **DEFAULT_DESCRIPTION_TYPE)
    country_iso2_code = models.CharField(_('country'), **COUNTRY_CODE_TYPE)
    country_description = models.CharField(_('country description'), **DEFAULT_DESCRIPTION_TYPE)
    regulation_language = models.CharField(_('regional language'), **LANGUAGE_CODE_TYPE)
    logical_id = models.BigIntegerField(_('logical id'), blank=True, null=True, default=None)
    regulation_summary = models.ForeignKey(RegulationSummary, **REGULATION_SUMMARY_TYPE)

    class Meta:
        verbose_name = _('citizenship')
        verbose_name_plural = _('citizenships')


class Address(SanctionListObject):
    sanction = models.ForeignKey('SanctionEntity', verbose_name=_('sanction entity'), on_delete=models.CASCADE)
    city = models.CharField(_('city'), **DEFAULT_DESCRIPTION_TYPE)
    street = models.CharField(_('street'), **DEFAULT_DESCRIPTION_TYPE)
    po_box = models.CharField(_('p.o. box'), **DEFAULT_DESCRIPTION_TYPE)
    zip_code = models.CharField(_('zip code'), **DEFAULT_DESCRIPTION_TYPE)
    as_at_listing_time = models.BooleanField(_('as at listing time'), **DEFAULT_BOOLEAN_TYPE)
    place = models.CharField(_('place'), **DEFAULT_DESCRIPTION_TYPE)
    region = models.CharField(_('region'), **DEFAULT_DESCRIPTION_TYPE)
    country_iso2_code = models.CharField(_('country'), **COUNTRY_CODE_TYPE)
    country_description = models.CharField(_('country description'), **DEFAULT_DESCRIPTION_TYPE)
    regulation_language = models.CharField(_('regional language'), **LANGUAGE_CODE_TYPE)
    logical_id = models.BigIntegerField(_('logical id'), blank=True, null=True, default=None)
    regulation_summary = models.ForeignKey(RegulationSummary, **REGULATION_SUMMARY_TYPE)

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')


class SanctionEntity(SanctionListObject):
    source = models.ForeignKey(EuCombinedSanctionsList, verbose_name=_('source'), on_delete=models.CASCADE)
    designation_details = models.CharField(_('designation details'), **DEFAULT_DESCRIPTION_TYPE)
    united_nation_id = models.CharField(_('United Nation identifier'), **DEFAULT_DESCRIPTION_TYPE)
    eu_reference_number = models.CharField(_('EU reference number'), **DEFAULT_DESCRIPTION_TYPE)
    logical_id = models.BigIntegerField(_('logical id'), blank=True, null=True, default=None)
    subject_type = models.ForeignKey(SubjectType, verbose_name=_('subject type'), on_delete=models.PROTECT, null=True, default=None, blank=True)

    class Meta:
        verbose_name = _('sanction entity')
        verbose_name_plural = _('sanction entities')
