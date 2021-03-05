import logging
import os
from typing import Optional

from django.core.management.base import CommandParser
from django.utils.timezone import now
from jsanctions.eu_combined import import_eu_combined_sanctions_list, EU_LIST_TYPE
from jutil.command import SafeCommand
from jsanctions.models import SanctionsListFile

logger = logging.getLogger(__name__)


class Command(SafeCommand):
    help = "Imports EU combined sanction lists"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--url", type=str)
        parser.add_argument("--file", type=str)
        parser.add_argument("--delete-old", action="store_true")
        parser.add_argument("--source", type=int)
        parser.add_argument("--new", action="store_true")
        parser.add_argument("--verbose", action="store_true")

    def do(self, *args, **options):
        verbose = options["verbose"]
        source: Optional[SanctionsListFile] = None
        if options["url"]:
            filename = options["file"] if options["file"] else "EU-combined-{}.xml".format(now().date().isoformat())
            source = SanctionsListFile.objects.create_from_url(options["url"], filename, list_type=EU_LIST_TYPE)
        elif options["file"]:
            source = SanctionsListFile.objects.create_from_filename(options["file"], list_type=EU_LIST_TYPE)
        elif options["source"]:
            source = SanctionsListFile.objects.get(id=options["source"])
        elif options["new"]:
            source = SanctionsListFile.objects.filter(imported=None).order_by("id").first()
        if not source:
            print("Nothing to import")
            return

        assert isinstance(source, SanctionsListFile)
        import_eu_combined_sanctions_list(source, verbose=verbose)

        if options["delete_old"]:
            for e in SanctionsListFile.objects.all().filters(list_type=EU_LIST_TYPE).exclude(id=source.id):
                assert isinstance(e, SanctionsListFile)
                logger.info("Deleting %s", e)
                if os.path.isfile(e.full_path):
                    os.unlink(e.full_path)
                e.delete()
                logger.info("%s deleted", e)
