import logging
import os
from typing import List, Dict, Any
from urllib.request import urlopen
from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from jutil.modelfields import SafeCharField, SafeTextField
from jutil.parse import parse_datetime
from jutil.xml import xml_to_dict
from jsanctions.helpers import dict_filter_attributes


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
EU_XML_INT_TAGS: List[str] = [
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
        response = urlopen(url)
        body = response.read()
        plain_filename = os.path.basename(filename)
        file = self.create(**kwargs)
        file.file.save(plain_filename, ContentFile(body))
        return file


class SanctionListObject(models.Model):
    pass


class SanctionsListFile(SanctionListObject):
    objects = SanctionsListFileManager()  # type: ignore
    created = models.DateTimeField(verbose_name=_('created'), default=now, blank=True, editable=False, db_index=True)
    imported = models.DateTimeField(verbose_name=_('imported'), default=None, null=True, blank=True, editable=False, db_index=True)
    generation_date = models.DateField(verbose_name=_('generation date'), default=None, blank=True, null=True, editable=False, db_index=True)
    file = models.FileField(verbose_name=_('file'), upload_to='uploads', validators=[FileExtensionValidator(['xml'])])

    class Meta:
        verbose_name = _('sanction list')
        verbose_name_plural = _('sanction lists')

    def __str__(self):
        return '{}'.format(os.path.basename(self.file.name))

    @property
    def full_path(self):
        return os.path.join(settings.MEDIA_ROOT, self.file.name)


class EuCombinedSanctionsList(SanctionsListFile):
    objects = SanctionsListFileManager()  # type: ignore
    global_file_id = SafeCharField(verbose_name=_('global file id'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore

    class Meta:
        verbose_name = _('EU combined sanction list')
        verbose_name_plural = _('EU combined sanction lists')

    def __str__(self):
        return '{}'.format(os.path.basename(self.file.name))

    def load_xml_as_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        with open(self.full_path, 'rb') as fp:
            data = xml_to_dict(fp.read(), array_tags=EU_XML_ARRAY_TAGS, int_tags=EU_XML_INT_TAGS)
            data = dict_filter_attributes(data, self._xml_filter_attributes)
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
    text = SafeTextField(verbose_name=_('text'), blank=True)

    class Meta:
        verbose_name = _('remark')
        verbose_name_plural = _('remarks')

    def __str__(self) -> str:
        return str(self.text)

    @property
    def text_brief(self) -> str:
        return self.text if len(self.text) < REMARK_BRIEF_LENGTH else self.text[:REMARK_BRIEF_LENGTH] + '...'


class SubjectType(SanctionListObject):
    code = SafeCharField(verbose_name=_('code'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    classification_code = SafeCharField(verbose_name=_('classification code'), **DEFAULT_CODE_TYPE)  # type: ignore

    class Meta:
        verbose_name = _('subject type')
        verbose_name_plural = _('subject types')

    def __str__(self) -> str:
        return str(self.code)


class Regulation(SanctionListObject):
    sanction = models.ForeignKey('SanctionEntity', verbose_name=_('sanction entity'), on_delete=models.CASCADE)
    regulation_type = SafeCharField(verbose_name=_('regulation type'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    organisation_type = SafeCharField(verbose_name=_('organization type'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    publication_date = models.DateField(verbose_name=_('publication date'), **DEFAULT_DATE_TYPE)  # type: ignore
    publication_url = models.URLField(verbose_name=_('url'), blank=True, default='')
    entry_into_force_date = models.DateField(verbose_name=_('entry into force date'), **DEFAULT_DATE_TYPE)  # type: ignore
    number_title = SafeCharField(verbose_name=_('number title'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    programme = SafeCharField(verbose_name=_('programmer'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    logical_id = models.BigIntegerField(verbose_name=_('logical id'), blank=True, null=True, default=None)

    class Meta:
        verbose_name = _('regulation')
        verbose_name_plural = _('regulations')


class RegulationSummary(SanctionListObject):
    regulation_type = SafeCharField(verbose_name=_('regulation type'), **DEFAULT_CODE_TYPE)  # type: ignore
    number_title = SafeCharField(verbose_name=_('number title'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    publication_date = models.DateField(verbose_name=_('publication date'), **DEFAULT_DATE_TYPE)  # type: ignore
    publication_url = models.URLField(verbose_name=_('url'), blank=True, default='')

    class Meta:
        verbose_name = _('regulation summary')
        verbose_name_plural = _('regulation summaries')

    def __str__(self) -> str:
        return '{} {}'.format(self.regulation_type, self.number_title)


class NameAlias(SanctionListObject):
    sanction = models.ForeignKey('SanctionEntity', verbose_name=_('sanction entity'), on_delete=models.CASCADE)
    first_name = SafeCharField(verbose_name=_('first name'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    middle_name = SafeCharField(verbose_name=_('middle name'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    last_name = SafeCharField(verbose_name=_('last name'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    whole_name = SafeCharField(verbose_name=_('whole name'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    name_language = SafeCharField(verbose_name=_('name language'), **LANGUAGE_CODE_TYPE)  # type: ignore
    function = SafeCharField(verbose_name=_('function'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    title = SafeCharField(verbose_name=_('title'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    regulation_language = SafeCharField(verbose_name=_('regulation language'), **LANGUAGE_CODE_TYPE)  # type: ignore
    logical_id = models.BigIntegerField(verbose_name=_('logical id'), blank=True, null=True, default=None)
    regulation_summary = models.ForeignKey(RegulationSummary, **REGULATION_SUMMARY_TYPE)  # type: ignore

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
    diplomatic = models.BooleanField(verbose_name=_('diplomatic'), **DEFAULT_BOOLEAN_TYPE)  # type: ignore
    known_expired = models.BooleanField(verbose_name=_('known expired'), **DEFAULT_BOOLEAN_TYPE)  # type: ignore
    known_false = models.BooleanField(verbose_name=_('known false'), **DEFAULT_BOOLEAN_TYPE)  # type: ignore
    reported_lost = models.BooleanField(verbose_name=_('reported lost'), **DEFAULT_BOOLEAN_TYPE)  # type: ignore
    revoked_by_issuer = models.BooleanField(verbose_name=_('revoked by issuer'), **DEFAULT_BOOLEAN_TYPE)  # type: ignore
    issued_by = SafeCharField(verbose_name=_('issued by'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    latin_number = SafeCharField(verbose_name=_('latin number'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    name_on_document = SafeCharField(verbose_name=_('name on document'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    number = SafeCharField(verbose_name=_('number'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    region = SafeCharField(verbose_name=_('region'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    country_iso2_code = SafeCharField(verbose_name=_('issued by'), **COUNTRY_CODE_TYPE)  # type: ignore
    country_description = SafeCharField(verbose_name=_('country description'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    identification_type_code = SafeCharField(verbose_name=_('identification type code'), **DEFAULT_CODE_TYPE)  # type: ignore
    identification_type_description = SafeCharField(verbose_name=_('identification type code'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    regulation_language = SafeCharField(verbose_name=_('regional language'), **LANGUAGE_CODE_TYPE)  # type: ignore
    logical_id = models.BigIntegerField(verbose_name=_('logical id'), blank=True, null=True, default=None)
    regulation_summary = models.ForeignKey(RegulationSummary, **REGULATION_SUMMARY_TYPE)  # type: ignore

    class Meta:
        verbose_name = _('identification')
        verbose_name_plural = _('identifications')


class BirthDate(SanctionListObject):
    sanction = models.ForeignKey('SanctionEntity', verbose_name=_('sanction entity'), on_delete=models.CASCADE)
    circa = models.BooleanField(verbose_name=_('circa'), **DEFAULT_BOOLEAN_TYPE)  # type: ignore
    calendar_type = SafeCharField(verbose_name=_('calendar type'), **DEFAULT_CODE_TYPE)  # type: ignore
    city = SafeCharField(verbose_name=_('city'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    zip_code = SafeCharField(verbose_name=_('zip code'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    birth_date = models.DateField(verbose_name=_('birth date'), **DEFAULT_DATE_TYPE)  # type: ignore
    day_of_month = models.IntegerField(verbose_name=_('day of month'), **DEFAULT_INT_TYPE)  # type: ignore
    month_of_year = models.IntegerField(verbose_name=_('month of year'), **DEFAULT_INT_TYPE)  # type: ignore
    year = models.IntegerField(verbose_name=_('year'), **DEFAULT_INT_TYPE)  # type: ignore
    region = SafeCharField(verbose_name=_('region'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    place = SafeCharField(verbose_name=_('place'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    country_iso2_code = SafeCharField(verbose_name=_('country'), **COUNTRY_CODE_TYPE)  # type: ignore
    country_description = SafeCharField(verbose_name=_('country description'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    regulation_language = SafeCharField(verbose_name=_('regional language'), **LANGUAGE_CODE_TYPE)  # type: ignore
    logical_id = models.BigIntegerField(verbose_name=_('logical id'), blank=True, null=True, default=None)

    class Meta:
        verbose_name = _('birth date')
        verbose_name_plural = _('birth dates')


class Citizenship(SanctionListObject):
    sanction = models.ForeignKey('SanctionEntity', verbose_name=_('sanction entity'), on_delete=models.CASCADE)
    region = SafeCharField(verbose_name=_('region'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    country_iso2_code = SafeCharField(verbose_name=_('country'), **COUNTRY_CODE_TYPE)  # type: ignore
    country_description = SafeCharField(verbose_name=_('country description'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    regulation_language = SafeCharField(verbose_name=_('regional language'), **LANGUAGE_CODE_TYPE)  # type: ignore
    logical_id = models.BigIntegerField(verbose_name=_('logical id'), blank=True, null=True, default=None)
    regulation_summary = models.ForeignKey(RegulationSummary, **REGULATION_SUMMARY_TYPE)  # type: ignore

    class Meta:
        verbose_name = _('citizenship')
        verbose_name_plural = _('citizenships')


class Address(SanctionListObject):
    sanction = models.ForeignKey('SanctionEntity', verbose_name=_('sanction entity'), on_delete=models.CASCADE)
    city = SafeCharField(verbose_name=_('city'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    street = SafeCharField(verbose_name=_('street'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    po_box = SafeCharField(verbose_name=_('p.o. box'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    zip_code = SafeCharField(verbose_name=_('zip code'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    as_at_listing_time = models.BooleanField(_('as at listing time'), **DEFAULT_BOOLEAN_TYPE)  # type: ignore
    place = SafeCharField(verbose_name=_('place'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    region = SafeCharField(verbose_name=_('region'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    country_iso2_code = SafeCharField(verbose_name=_('country'), **COUNTRY_CODE_TYPE)  # type: ignore
    country_description = SafeCharField(verbose_name=_('country description'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    regulation_language = SafeCharField(verbose_name=_('regional language'), **LANGUAGE_CODE_TYPE)  # type: ignore
    logical_id = models.BigIntegerField(verbose_name=_('logical id'), blank=True, null=True, default=None)
    regulation_summary = models.ForeignKey(RegulationSummary, **REGULATION_SUMMARY_TYPE)  # type: ignore

    class Meta:
        verbose_name = _('address')
        verbose_name_plural = _('addresses')


class SanctionEntity(SanctionListObject):
    source = models.ForeignKey(EuCombinedSanctionsList, verbose_name=_('source'), on_delete=models.CASCADE)
    designation_details = SafeCharField(verbose_name=_('designation details'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    united_nation_id = SafeCharField(verbose_name=_('United Nation identifier'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    eu_reference_number = SafeCharField(verbose_name=_('EU reference number'), **DEFAULT_DESCRIPTION_TYPE)  # type: ignore
    logical_id = models.BigIntegerField(verbose_name=_('logical id'), blank=True, null=True, default=None)
    subject_type = models.ForeignKey(SubjectType, verbose_name=_('subject type'), on_delete=models.PROTECT, null=True, default=None, blank=True)

    class Meta:
        verbose_name = _('sanction entity')
        verbose_name_plural = _('sanction entities')
