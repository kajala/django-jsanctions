import os
from django.conf import settings
from django.test import TestCase
from jsanctions.eu import import_eu_sanctions
from jsanctions.models import SanctionEntity, SanctionsListFile
from jsanctions.ofac import import_ofac_sanctions
from jsanctions.un import import_un_sanctions


class Tests(TestCase):
    def test_eu_sanctions_import(self):
        filename = os.path.join(settings.BASE_DIR, "data/eu/2021-03-05.xml")
        source = SanctionsListFile.objects.create_from_filename(filename)
        assert isinstance(source, SanctionsListFile)
        import_eu_sanctions(source, verbose=False)
        print("EU count =", SanctionEntity.objects.all().filter(source=source).count())
        self.assertEqual(SanctionEntity.objects.all().filter(source=source).count(), 2269)

    def test_ofac_sanctions_import(self):
        filename = os.path.join(settings.BASE_DIR, "data/ofac/sdn.xml")
        source = SanctionsListFile.objects.create_from_filename(filename)
        assert isinstance(source, SanctionsListFile)
        import_ofac_sanctions(source, verbose=False)
        print("OFAC count =", SanctionEntity.objects.all().filter(source=source).count())
        self.assertEqual(SanctionEntity.objects.all().filter(source=source).count(), 8832)

    def test_un_sanctions_import(self):
        filename = os.path.join(settings.BASE_DIR, "data/un/consolidated.xml")
        source = SanctionsListFile.objects.create_from_filename(filename)
        assert isinstance(source, SanctionsListFile)
        import_un_sanctions(source, verbose=False)
        print("UN count =", SanctionEntity.objects.all().filter(source=source).count())
        self.assertEqual(SanctionEntity.objects.all().filter(source=source).count(), 711 + 293)
