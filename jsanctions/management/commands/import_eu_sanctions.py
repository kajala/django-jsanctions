import logging
from typing import Optional
from django.core.management.base import CommandParser
from django.utils.timezone import now
from jsanctions.eu import import_eu_sanctions, EU_LIST_TYPE
from jutil.command import SafeCommand
from jsanctions.services import delete_old_sanction_list_files
from jsanctions.models import SanctionsListFile

logger = logging.getLogger(__name__)


class Command(SafeCommand):
    help = "Imports EU consolidated sanction lists"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--url", type=str)
        parser.add_argument("--file", type=str)
        parser.add_argument("--delete-old", action="store_true")
        parser.add_argument("--source", type=int)
        parser.add_argument("--new", action="store_true")
        parser.add_argument("--verbose", action="store_true")

    def do(self, *args, **options):  # pylint: disable=too-many-branches
        list_type = EU_LIST_TYPE
        verbose = options["verbose"]
        source: Optional[SanctionsListFile] = None
        if options["url"]:
            url = options["url"]
            filename = options["file"] if options["file"] else "EU-consolidated-{}.xml".format(now().date().isoformat())
            source = SanctionsListFile.objects.create_from_url(url, filename, list_type=list_type)
        elif options["file"]:
            source = SanctionsListFile.objects.create_from_filename(options["file"], list_type=list_type)
        elif options["source"]:
            source = SanctionsListFile.objects.get(id=options["source"])
        elif options["new"]:
            source = SanctionsListFile.objects.filter(imported=None).order_by("id").first()
        if not source:
            print("Nothing to import")
            return

        assert isinstance(source, SanctionsListFile)
        import_eu_sanctions(source, verbose=verbose)

        if options["delete_old"]:
            delete_old_sanction_list_files(list_type, [source])
