import logging
import os

from django.conf import settings
from django.core.management import CommandParser
from django.db import transaction
from django.utils.timezone import now
from jutil.admin import admin_log
from jutil.command import SafeCommand
from jsanctions.helpers import camel_case_to_underscore
from jsanctions.models import EuCombinedSanctionsList, SanctionEntity, RegulationSummary, BirthDate, Identification, \
    Remark, Address, Citizenship, NameAlias, Regulation, SubjectType


logger = logging.getLogger(__name__)


def eu_set_simple_members(obj, data: dict, commit: bool = True, verbose: bool = True, padding: int = 0, **kwargs):
    class_map = {
        'regulationSummary': RegulationSummary,
        'subjectType': SubjectType,
    }
    array_class_map = {
        'birthdate': BirthDate,
        'identification': Identification,
        'address': Address,
        'citizenship': Citizenship,
        'nameAlias': NameAlias,
        'regulation': Regulation,
    }

    padding_str = ' ' * padding
    obj.save()
    for k0, v0 in data.items():
        if k0[0] == '@':
            k = camel_case_to_underscore(k0[1:])
            if k == 'birthdate':
                k = 'birth_date'  # special case because class name same as attribute
            if hasattr(obj, k):
                setattr(obj, k, v0)
                if verbose:
                    logger.info('{}{}: {} = {}'.format(padding_str, obj, k, v0))
        elif k0 in class_map:
            k = camel_case_to_underscore(k0)
            if hasattr(obj, k):
                if k == 'subject_type':
                    obj2, created = SubjectType.objects.get_or_create(
                        code=v0.get('@code', ''),
                        classification_code=v0.get('@classificationCode', ''))
                elif k == 'regulation_summary':
                    obj2, created = RegulationSummary.objects.get_or_create(
                        regulation_type=v0.get('@regulationType', ''),
                        publication_date=v0.get('@publicationDate', None),
                        publication_url=v0.get('@publicationUrl', ''),
                        number_title=v0.get('@numberTitle', ''))
                else:
                    obj2 = class_map[k0]()
                    kwargs2 = {}
                    kwargs2[k] = obj2
                    for k2, v2 in kwargs.items():
                        setattr(obj2, k2, v2)
                        kwargs2[k2] = v2

                    eu_set_simple_members(obj2, v0, verbose=verbose, padding=padding+4, **kwargs2)

                setattr(obj, k, obj2)
        elif k0 in array_class_map:
            k = camel_case_to_underscore(k0)
            cls = array_class_map[k0]
            for v0_data in v0:
                obj2 = cls()
                kwargs2 = {}
                kwargs2[k] = obj2
                for k2, v2 in kwargs.items():
                    setattr(obj2, k2, v2)
                    kwargs2[k2] = v2
                obj2.clean()
                obj2.save()
                eu_set_simple_members(obj2, v0_data, verbose=verbose, padding=padding+4, **kwargs2)
        elif k0 == 'remark':
            for v0_str in v0:
                Remark.objects.create(text=v0_str, container=obj)

    if commit:
        if verbose:
            logger.info('Saving {}'.format(obj))
        obj.clean()
        obj.save()


def create_eu_sanctions(source: EuCombinedSanctionsList, verbose: bool = True):
    data = source.load_xml_as_dict()
    # if verbose:
    #     pprint(data)
    eu_set_simple_members(source, data, verbose=verbose)
    entities_list = data.get('sanctionEntity', [])
    logger.info('Importing {} sanction entities from {}'.format(len(entities_list), os.path.basename(source.file.name)))
    t0 = now()
    for se_data in entities_list:
        assert isinstance(se_data, dict)
        if verbose:
            logger.info('  sanctionEntity')
        with transaction.atomic():
            se = SanctionEntity.objects.create(source=source)
            eu_set_simple_members(se, se_data, verbose=verbose, padding=4, sanction=se)
    source.imported = now()
    source.save()
    msg = 'Imported {} sanction entities from {} in {}'.format(len(entities_list), os.path.basename(source.file.name), source.imported - t0)
    logger.info(msg)
    admin_log([source], msg)


class Command(SafeCommand):
    help = "Imports EU combined sanction lists and saves results to the DB"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument('--url', type=str)
        parser.add_argument('--file', type=str)
        parser.add_argument('--delete-old', action='store_true')
        parser.add_argument('--source', type=int)
        parser.add_argument('--new', action='store_true')
        parser.add_argument('--verbose', action='store_true')

    def do(self, *args, **options):
        verbose = options['verbose']
        source = None
        if options['url']:
            filename = options['file'] if options['file'] else 'EU-combined-{}.xml'.format(now().date().isoformat())
            source = EuCombinedSanctionsList.objects.create_from_url(options['url'], filename)
        elif options['file']:
            source = EuCombinedSanctionsList.objects.create_from_filename(options['file'])
        elif options['source']:
            source = EuCombinedSanctionsList.objects.get(id=options['source'])
        elif options['new']:
            source = EuCombinedSanctionsList.objects.filter(imported=None).order_by('id').first()

        if not source:
            return print('Nothing to import')

        if options['delete_old']:
            for e in EuCombinedSanctionsList.objects.all().exclude(id=source.id):
                logger.info('Deleting {}'.format(e))
                e.delete()

        assert isinstance(source, EuCombinedSanctionsList)
        create_eu_sanctions(source, verbose=verbose)
