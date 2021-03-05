import os
from django.conf import settings
from django.test import TestCase
from jsanctions.eu_combined import import_eu_combined_sanctions_list
from jsanctions.models import SanctionEntity, SanctionsListFile


class Tests(TestCase):
    def test_eu_combined_sanctions_list_import(self):
        filename = os.path.join(settings.BASE_DIR, "data/eu-combined/2021-03-05.xml")
        source = SanctionsListFile.objects.create_from_filename(filename)
        assert isinstance(source, SanctionsListFile)
        import_eu_combined_sanctions_list(source, verbose=False)
        self.assertEqual(SanctionEntity.objects.all().count(), 2269)
