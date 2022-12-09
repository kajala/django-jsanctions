import logging
import os
from typing import List
from jsanctions.models import SanctionsListFile, SanctionEntity

logger = logging.getLogger(__name__)


def delete_old_sanction_list_files(list_type: str, exclude: List[SanctionsListFile]):
    exclude_ids = [ex.id for ex in exclude]
    qs = SanctionsListFile.objects.all().filter(list_type=list_type).exclude(id__in=exclude_ids)
    for e in qs:
        assert isinstance(e, SanctionsListFile)
        logger.info("Deleting SanctionsListFile id=%s", e.id)
        if os.path.isfile(e.full_path) and not any(ex.full_path == e.full_path for ex in exclude):
            os.unlink(e.full_path)
            logger.info("%s deleted", e.full_path)
        SanctionEntity.objects.all().filter(source=e).delete()
        e.delete()
