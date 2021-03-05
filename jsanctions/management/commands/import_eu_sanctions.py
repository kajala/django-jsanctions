import logging
from django.core.management.base import CommandParser
from django.utils.timezone import now
from jsanctions.eu_combined import import_eu_combined_sanctions_list
from jutil.command import SafeCommand
from jsanctions.models import SanctionsListFile

logger = logging.getLogger(__name__)


class Command(SafeCommand):
    help = "Imports EU combined sanction lists and saves results to the DB"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--url", type=str)
        parser.add_argument("--file", type=str)
        parser.add_argument("--delete-old", action="store_true")
        parser.add_argument("--source", type=int)
        parser.add_argument("--new", action="store_true")
        parser.add_argument("--verbose", action="store_true")

    def do(self, *args, **options):
        verbose = options["verbose"]
        source = None
        if options["url"]:
            filename = options["file"] if options["file"] else "EU-combined-{}.xml".format(now().date().isoformat())
            source = SanctionsListFile.objects.create_from_url(options["url"], filename)
        elif options["file"]:
            source = SanctionsListFile.objects.create_from_filename(options["file"])
        elif options["source"]:
            source = SanctionsListFile.objects.get(id=options["source"])
        elif options["new"]:
            source = SanctionsListFile.objects.filter(imported=None).order_by("id").first()

        if not source:
            print("Nothing to import")
            return

        if options["delete_old"]:
            for e in SanctionsListFile.objects.all().exclude(id=source.id):
                logger.info("Deleting %s", e)
                e.delete()

        assert isinstance(source, SanctionsListFile)
        import_eu_combined_sanctions_list(source, verbose=verbose)
