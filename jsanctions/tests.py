import os
from django.conf import settings
from django.test import TestCase
from jsanctions.management.commands.import_eu_sanctions import create_eu_sanctions
from jsanctions.models import EuCombinedSanctionsList, SanctionEntity


class Tests(TestCase):
    def test_eu_sanctions_import(self):
        print('test_eu_sanctions_import')
        filename = os.path.join(settings.BASE_DIR, 'data/eu/20190827-FULL-1_1.xml')
        source = EuCombinedSanctionsList.objects.create_from_filename(filename)
        assert isinstance(source, EuCombinedSanctionsList)
        create_eu_sanctions(source, verbose=False)
        self.assertEqual(SanctionEntity.objects.all().count(), 2200)
