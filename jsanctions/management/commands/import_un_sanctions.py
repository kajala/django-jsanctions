import logging
import os
from typing import Optional
from django.core.management.base import CommandParser
from django.utils.timezone import now
from jutil.command import SafeCommand
from jsanctions.services import delete_old_sanction_list_files
from jsanctions.models import SanctionsListFile
from jsanctions.un import UN_LIST_TYPE, import_un_sanctions

logger = logging.getLogger(__name__)


class Command(SafeCommand):
    help = "Imports U consolidated sanction lists"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--url", type=str)
        parser.add_argument("--file", type=str)
        parser.add_argument("--delete-old", action="store_true")
        parser.add_argument("--source", type=int)
        parser.add_argument("--new", action="store_true")
        parser.add_argument("--verbose", action="store_true")
        parser.add_argument("--url-defaults", action="store_true")

    def do(self, *args, **options):  # pylint: disable=too-many-branches
        verbose = options["verbose"]
        source: Optional[SanctionsListFile] = None
        list_type = UN_LIST_TYPE
        if options["url"]:
            url = options["url"]
            filename = options["file"] if options["file"] else "{}-{}-{}.xml".format(list_type, os.path.basename(url)[:-4], now().date().isoformat())
            source = SanctionsListFile.objects.create_from_url(url, filename, list_type=list_type)
        elif options["file"]:
            source = SanctionsListFile.objects.create_from_filename(options["file"], list_type=list_type)
        elif options["source"]:
            source = SanctionsListFile.objects.get(id=options["source"])
        elif options["new"]:
            source = SanctionsListFile.objects.filter(imported=None).order_by("id").first()
        if options["url_defaults"]:
            url = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"
            filename = "{}-{}-{}.xml".format(list_type, os.path.basename(url)[:-4], now().date().isoformat())
            source = SanctionsListFile.objects.create_from_url(url, filename, legacy_ssl=True, list_type=list_type)
        if not source:
            print("Nothing to import")
            return

        assert isinstance(source, SanctionsListFile)
        import_un_sanctions(source, verbose=verbose)

        if options["delete_old"]:
            delete_old_sanction_list_files(list_type, [source])
