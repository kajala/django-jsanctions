from typing import List, Dict
from jsanctions.helpers import dict_filter_attributes
from jutil.parse import parse_datetime
from jutil.xml import xml_to_dict
import logging
import os
from typing import Any
from django.db import transaction
from django.utils.timezone import now
from jutil.admin import admin_log
from jsanctions.models import (
    SanctionsListFile,
    SanctionEntity,
    RegulationSummary,
    BirthDate,
    Identification,
    Remark,
    Address,
    Citizenship,
    NameAlias,
    Regulation,
    SubjectType,
)
from jutil.format import camel_case_to_underscore

logger = logging.getLogger(__name__)

EU_LIST_TYPE = "EU"

EU_XML_ARRAY_TAGS = [
    "sanctionEntity",
    "nameAlias",
    "identification",
    "address",
    "birthdate",
    "citizenship",
    "regulation",
    "remark",
]

EU_XML_INT_TAGS: List[str] = []

EU_XML_DATE_ATTRIBUTES = [
    "@birthdate",
]


def eu_sanction_list_xml_attr_filter(k: str, v: Any) -> Any:
    if k.endswith("Date") or k in EU_XML_DATE_ATTRIBUTES:
        return parse_datetime(v).date()
    if k == "@logicalId":
        return int(v)
    if v == "false":
        return False
    if v == "true":
        return True
    return v


def load_eu_sanction_list_as_dict(filename: str) -> Dict[str, Any]:
    with open(filename, "rb") as fp:
        data: Dict[str, Any] = xml_to_dict(fp.read(), array_tags=EU_XML_ARRAY_TAGS, int_tags=EU_XML_INT_TAGS)
        data = dict_filter_attributes(data, eu_sanction_list_xml_attr_filter)
    return data


def set_eu_object_attr(obj, k: str, v, max_length: int = 512):
    if v and isinstance(v, str) and len(v) > max_length:
        logger.warning("'%s' truncated to [%s]: '%s...'", k, max_length, v[:64])
        v = v[: max_length - 3] + "..."
    setattr(obj, k, v)


def set_eu_members(obj: Any, data: Dict[str, Any], verbose: bool = False, padding: int = 0, **kwargs):  # noqa
    class_map = {
        "regulationSummary": RegulationSummary,
        "subjectType": SubjectType,
    }
    array_class_map = {
        "birthdate": BirthDate,
        "identification": Identification,
        "address": Address,
        "citizenship": Citizenship,
        "nameAlias": NameAlias,
        "regulation": Regulation,
    }

    padding_str = " " * padding
    obj.save()
    obj2: Any
    for k0, v0 in data.items():
        if k0[0] == "@":
            k = camel_case_to_underscore(k0[1:])
            if k == "birthdate":
                k = "birth_date"  # special case because class name same as attribute
            if hasattr(obj, k):
                set_eu_object_attr(obj, k, v0)
                if verbose:
                    logger.info("%s%s: %s = %s", padding_str, obj, k, v0)
        elif k0 in class_map:
            k = camel_case_to_underscore(k0)
            if hasattr(obj, k):
                if k == "subject_type":
                    obj2 = SubjectType.objects.get_or_create(
                        code=v0.get("@code", ""), classification_code=v0.get("@classificationCode", "")
                    )[0]
                elif k == "regulation_summary":
                    obj2 = RegulationSummary.objects.get_or_create(
                        regulation_type=v0.get("@regulationType", ""),
                        publication_date=v0.get("@publicationDate", None),
                        publication_url=v0.get("@publicationUrl", ""),
                        number_title=v0.get("@numberTitle", ""),
                    )[0]
                else:
                    obj2 = class_map[k0]()
                    kwargs2 = {}
                    kwargs2[k] = obj2
                    for k2, v2 in kwargs.items():
                        set_eu_object_attr(obj2, k2, v2)
                        kwargs2[k2] = v2

                    set_eu_members(obj2, v0, verbose=verbose, padding=padding + 4, **kwargs2)

                set_eu_object_attr(obj, k, obj2)
        elif k0 in array_class_map:
            k = camel_case_to_underscore(k0)
            cls = array_class_map[k0]
            for v0_data in v0:
                obj2 = cls()
                kwargs2 = {}
                kwargs2[k] = obj2
                for k2, v2 in kwargs.items():
                    set_eu_object_attr(obj2, k2, v2)
                    kwargs2[k2] = v2
                obj2.clean()
                obj2.save()
                set_eu_members(obj2, v0_data, verbose=verbose, padding=padding + 4, **kwargs2)
        elif k0 == "remark":
            for v0_str in v0:
                Remark.objects.create(text=v0_str, container=obj)

    obj.clean()
    obj.save()
    if verbose:
        logger.info("%sSaved %s", padding * " ", obj)


def import_eu_sanctions(source: SanctionsListFile, verbose: bool = False):
    data = load_eu_sanction_list_as_dict(source.full_path)
    set_eu_members(source, data, verbose=verbose)
    entities_list = data.get("sanctionEntity", [])
    logger.info("Importing %s sanction entities from %s", len(entities_list), os.path.basename(source.file.name))
    t0 = now()
    for se_data in entities_list:
        assert isinstance(se_data, dict)
        if verbose:
            logger.info("  sanctionEntity")
        with transaction.atomic():
            se = SanctionEntity.objects.create(source=source, data=se_data)
            set_eu_members(se, se_data, verbose=verbose, padding=4, sanction=se)
    source.imported = now()
    source.save()
    msg = "Imported {} sanction entities from {} in {}".format(
        len(entities_list), source.full_path, source.imported - t0
    )
    logger.info(msg)
    admin_log([source], msg)
