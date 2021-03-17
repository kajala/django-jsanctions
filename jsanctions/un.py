import logging
from typing import Any, Dict, List, Optional
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.dateparse import parse_date
from django.utils.timezone import now
from django.utils.translation import gettext as _
from jutil.admin import admin_log
from jutil.format import choices_label
from jutil.parse import parse_datetime
from jutil.xml import xml_to_dict

from jsanctions.helpers import get_country_iso2_code
from jsanctions.models import (
    SanctionsListFile,
    SanctionEntity,
    NameAlias,
    Remark,
    Address,
    Identification,
    SanctionListObject,
    SubjectType,
)

logger = logging.getLogger(__name__)

UN_LIST_TYPE = "UN"

UN_XML_ARRAY_TAGS = [
    "VALUE",
    "INDIVIDUAL",
    "INDIVIDUAL_ALIAS",
    "INDIVIDUAL_ADDRESS",
    "INDIVIDUAL_DATE_OF_BIRTH",
    "INDIVIDUAL_PLACE_OF_BIRTH",
    "INDIVIDUAL_DOCUMENT",
    "ENTITY",
    "ENTITY_ALIAS",
    "ENTITY_ADDRESS",
]

UN_NAME_FIELDS = ["FIRST_NAME", "SECOND_NAME", "THIRD_NAME", "FOURTH_NAME", "FIFTH_NAME", "SIXTH_NAME"]


def load_un_sanction_list_as_dict(filename: str) -> Dict[str, Any]:
    with open(filename, "rb") as fp:
        data: Dict[str, Any] = xml_to_dict(fp.read(), array_tags=UN_XML_ARRAY_TAGS)
    return data


def parse_un_data_id(data: Dict[str, Any]) -> int:
    uid = data.get("DATAID")
    if uid is None:
        raise ValidationError(_("DATAID missing"))
    return int(uid)


def create_un_alias(se: SanctionEntity, **kwargs) -> Optional[NameAlias]:
    names = []
    for k in UN_NAME_FIELDS:
        if k in kwargs and kwargs[k]:
            names.append(kwargs[k])
    if not names:
        logger.warning("No names: %s", kwargs)
        return None

    alias = NameAlias(sanction=se, logical_id=parse_un_data_id(kwargs))
    alias.title = kwargs.get("TITLE") or ""
    alias.last_name = names.pop() or ""
    alias.first_name = " ".join(names).strip()
    alias.full_clean()
    alias.save()
    return alias


def create_un_comments(se: SanctionEntity, **kwargs) -> List[Remark]:
    out: List[Remark] = []
    for n in range(1, 10):
        k = "COMMENTS{}".format(n)
        if k in kwargs and kwargs[k]:
            obj_out = Remark(container=se, text=kwargs.get(k) or "")  # type: ignore
            obj_out.full_clean()
            obj_out.save()
            out.append(obj_out)
        else:
            break
    return out


def create_un_note(obj: SanctionListObject, note: Any):
    if note:
        remark = Remark(container=obj, text=str(note))
        remark.full_clean()
        remark.save()


def create_un_address(se: SanctionEntity, **kwargs) -> Address:
    # {'STATE_PROVINCE', 'NOTE', 'COUNTRY', 'STREET', 'CITY', 'ZIP_CODE'}
    address = Address(sanction=se)
    address.region = kwargs.get("STATE_PROVINCE") or ""
    address.city = kwargs.get("CITY") or ""
    address.zip_code = kwargs.get("ZIP_CODE") or ""
    address.country_description = kwargs.get("COUNTRY") or ""
    address.street = kwargs.get("STREET") or ""
    for k, v in kwargs.items():
        if hasattr(address, k):
            setattr(address, k, v)
    address.full_clean()
    address.save()
    create_un_note(address, kwargs.get("NOTE"))
    return address


def create_un_document(se: SanctionEntity, **kwargs) -> Identification:
    # {'DATE_OF_ISSUE', 'NUMBER', 'NOTE', 'ISSUING_COUNTRY', 'CITY_OF_ISSUE', 'COUNTRY_OF_ISSUE',
    # 'TYPE_OF_DOCUMENT', 'TYPE_OF_DOCUMENT2'}
    id_obj = Identification(sanction=se)
    id_obj.identification_type_description = kwargs.get("TYPE_OF_DOCUMENT") or kwargs.get("TYPE_OF_DOCUMENT2") or ""
    id_obj.issue_date = parse_date(str(kwargs.get("DATE_OF_ISSUE"))) if kwargs.get("DATE_OF_ISSUE") else None  # type: ignore
    id_obj.latin_number = kwargs.get("NUMBER") or ""
    id_obj.issued_by = "{} {} {}".format(
        kwargs.get("CITY_OF_ISSUE") or "", kwargs.get("COUNTRY_OF_ISSUE") or "", kwargs.get("ISSUING_COUNTRY") or ""
    ).strip()
    id_obj.country_description = kwargs.get("COUNTRY_OF_ISSUE") or kwargs.get("ISSUING_COUNTRY") or ""
    id_obj.full_clean()
    id_obj.save()
    create_un_note(id_obj, kwargs.get("NOTE"))
    return id_obj


def set_un_members(  # noqa
    se: SanctionEntity,
    data: Dict[str, Any],
    verbose: bool = False,
    padding: int = 0,
):
    # DATAID
    se.logical_id = parse_un_data_id(data)

    # FIRST_NAME, ...
    create_un_alias(se, **data)

    # COMMENTSx
    create_un_comments(se, **data)

    # INVIDUAL_ADDRESS / ENTITY_ADDRESS
    address_list = data.get("INVIDUAL_ADDRESS", []) or data.get("ENTITY_ADDRESS", [])
    addresses: List[Address] = []
    if address_list:
        for e_data in address_list:
            if e_data:
                addresses.append(create_un_address(se, **e_data))

    # try to fill address information from UN list name
    if not addresses:
        un_list_type = data.get("UN_LIST_TYPE")
        if un_list_type:
            country_code = get_country_iso2_code(un_list_type)
            if country_code:
                create_un_address(se, country_description=un_list_type, country_code=country_code)

    # INDIVIDUAL_DOCUMENT
    docs = data.get("INDIVIDUAL_DOCUMENT")
    if docs:
        for e_data in docs:
            if e_data:
                create_un_document(se, **e_data)

    se.full_clean()
    se.save()
    if verbose:
        logger.info("%sSaved %s", padding * " ", se)


def import_un_sanctions(source: SanctionsListFile, verbose: bool = False):
    data = load_un_sanction_list_as_dict(source.full_path)
    source.generation_date = parse_datetime(data["@dateGenerated"]).date()

    enterprise, created = SubjectType.objects.get_or_create(classification_code=SubjectType.ENTERPRISE)
    assert isinstance(enterprise, SubjectType)
    if created or not enterprise.code:
        enterprise.code = choices_label(SubjectType.CLASSIFICATION_CODES, enterprise.classification_code)
        enterprise.save()
    person, created = SubjectType.objects.get_or_create(classification_code=SubjectType.PERSON)
    assert isinstance(person, SubjectType)
    if created or not person.code:
        person.code = choices_label(SubjectType.CLASSIFICATION_CODES, person.classification_code)
        person.save()

    t0 = now()
    individuals_list = data.get("INDIVIDUALS", {}).get("INDIVIDUAL")
    for se_data in individuals_list:
        assert isinstance(se_data, dict)
        if verbose:
            logger.info("  sdnEntry uid %s", se_data.get("uid"))
        with transaction.atomic():
            se = SanctionEntity.objects.create(source=source, data=se_data, subject_type=person)
            set_un_members(se, se_data, verbose=verbose, padding=4)

    entities_list = data.get("ENTITIES", {}).get("ENTITY")
    for se_data in entities_list:
        assert isinstance(se_data, dict)
        if verbose:
            logger.info("  sdnEntry uid %s", se_data.get("uid"))
        with transaction.atomic():
            se = SanctionEntity.objects.create(source=source, data=se_data, subject_type=enterprise)
            set_un_members(se, se_data, verbose=verbose, padding=4)

    source.imported = now()
    source.save()
    msg = "Imported {} sanction entities and {} individuals from {} in {}".format(
        len(entities_list), len(individuals_list), source.full_path, source.imported - t0
    )
    logger.info(msg)
    admin_log([source], msg)
