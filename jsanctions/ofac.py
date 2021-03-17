import logging
import re
from datetime import date
from time import strptime
from typing import Dict, Any, Tuple, Optional
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import translation
from django.utils.timezone import now
from django.utils.translation import gettext as _
from jutil.admin import admin_log
from jutil.format import choices_label
from jutil.xml import xml_to_dict
from jsanctions.models import (
    SanctionsListFile,
    SanctionEntity,
    NameAlias,
    SubjectType,
    BirthDate,
    Address,
    Identification,
    Remark,
)

logger = logging.getLogger(__name__)

OFAC_LIST_TYPE = "OFAC"

OFAC_XML_ARRAY_TAGS = ["sdnEntry", "program", "aka", "dateOfBirthItem", "placeOfBirthItem", "address", "id"]


def load_ofac_sanction_list_as_dict(filename: str) -> Dict[str, Any]:
    with open(filename, "rb") as fp:
        data: Dict[str, Any] = xml_to_dict(fp.read(), array_tags=OFAC_XML_ARRAY_TAGS)
    return data


def parse_ofac_date(v: str) -> date:
    st = strptime(v, "%m/%d/%Y")
    if not st:
        raise ValidationError(_("Invalid date value {}").format(v))
    return date(st.tm_year, st.tm_mon, st.tm_mday)


def parse_ofac_dob(v: str) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    if re.fullmatch(r"\d{4}", v):
        return int(v), None, None
    if re.fullmatch(r"\d{1,2}/\d{1,2}/\d{4}", v):
        st = strptime(v, "%m/%d/%Y")
        return st.tm_year, st.tm_mon, st.tm_mday
    if re.fullmatch(r"\d{1,2} \w{3} \d{4}", v):
        with translation.override("en_US"):
            st = strptime(v, "%d %b %Y")
            return st.tm_year, st.tm_mon, st.tm_mday
    return None, None, None


def get_opt_ofac_str(data: Dict[str, Any], key: str) -> str:
    return data.get(key, "") or ""


def get_ofac_subject_type(data: Dict[str, Any]) -> SubjectType:
    sdn_type = data["sdnType"]
    if sdn_type == "Entity":
        obj, created = SubjectType.objects.get_or_create(classification_code=SubjectType.ENTERPRISE)
    elif sdn_type == "Individual":
        obj, created = SubjectType.objects.get_or_create(classification_code=SubjectType.PERSON)
    elif sdn_type == "Vessel":
        obj, created = SubjectType.objects.get_or_create(classification_code=SubjectType.VESSEL)
    elif sdn_type == "Aircraft":
        obj, created = SubjectType.objects.get_or_create(classification_code=SubjectType.AIRCRAFT)
    else:
        logger.warning("Unknown sdnType: %s", sdn_type)
        obj, created = SubjectType.objects.get_or_create(classification_code=sdn_type, code=sdn_type)
    assert isinstance(obj, SubjectType)
    if created:
        obj.code = choices_label(SubjectType.CLASSIFICATION_CODES, obj.classification_code)
        obj.save(update_fields=["code"])
    return obj


def parse_ofac_uid(data: Dict[str, Any]) -> int:
    uid = data.get("uid")
    if uid is None:
        raise ValidationError(_("UID missing"))
    return int(uid)


def create_ofac_alias(se: SanctionEntity, **kwargs) -> NameAlias:
    first_name = kwargs.get("firstName") or ""
    last_name = kwargs.get("lastName") or ""
    uid = parse_ofac_uid(kwargs)
    whole_name = (first_name + " " + last_name).strip()
    alias = NameAlias(sanction=se, first_name=first_name, last_name=last_name, whole_name=whole_name, logical_id=uid)
    alias.full_clean()
    alias.save()
    return alias


def create_ofac_dob(se: SanctionEntity, **kwargs) -> BirthDate:
    dob = BirthDate(sanction=se)
    dob.logical_id = parse_ofac_uid(kwargs)
    dob.birth_date_description = kwargs.get("dateOfBirth") or ""
    year, month_of_year, day_of_month = parse_ofac_dob(dob.birth_date_description)
    dob.year = year  # type: ignore
    dob.month_of_year = month_of_year  # type: ignore
    dob.day_of_month = day_of_month  # type: ignore
    if year and month_of_year and day_of_month:
        dob.birth_date = date(year, month_of_year, day_of_month)
    dob.full_clean()
    dob.save()
    return dob


def create_ofac_place_of_birth(se: SanctionEntity, **kwargs) -> BirthDate:
    dob = BirthDate.objects.all().filter(sanction=se, place="").order_by("id").first()
    if dob is None:
        dob = BirthDate(sanction=se, logical_id=parse_ofac_uid(kwargs))
    dob.place = get_opt_ofac_str(kwargs, "placeOfBirth")
    dob.full_clean()
    dob.save()
    return dob


def create_ofac_address(se: SanctionEntity, **kwargs) -> Address:
    address = Address(sanction=se)
    address.logical_id = parse_ofac_uid(kwargs)
    address.region = get_opt_ofac_str(kwargs, "stateOrProvince")
    address.city = get_opt_ofac_str(kwargs, "city")
    address.zip_code = get_opt_ofac_str(kwargs, "postalCode")
    address.country_description = get_opt_ofac_str(kwargs, "country")
    street = ""
    for n in range(1, 5):
        k = "address{}".format(n)
        if k in kwargs:
            street = street + "\n" + str(kwargs.get(k))
        else:
            break
    address.street = street.strip()
    address.full_clean()
    address.save()
    return address


def create_ofac_id(se: SanctionEntity, **kwargs) -> Identification:
    id_obj = Identification(sanction=se)
    id_obj.logical_id = parse_ofac_uid(kwargs)
    id_obj.number = kwargs.get("idNumber") or ""
    id_obj.identification_type_description = kwargs.get("idType") or ""
    id_obj.country_description = kwargs.get("idCountry") or ""
    id_obj.full_clean()
    id_obj.save()
    return id_obj


def set_ofac_members(  # noqa
    se: SanctionEntity,
    data: Dict[str, Any],
    verbose: bool = False,
    padding: int = 0,
):
    # uid
    se.logical_id = parse_ofac_uid(data)

    # firstName, lastName
    first_name, last_name = get_opt_ofac_str(data, "firstName"), get_opt_ofac_str(data, "lastName")
    if first_name or last_name:
        create_ofac_alias(se, **data)

    # sdnType
    se.subject_type = get_ofac_subject_type(data)

    # remarks
    remarks = data.get("remarks") or ""
    if remarks:
        remark_obj = Remark(container=se, text=remarks)
        remark_obj.full_clean()
        remark_obj.save()

    # programList
    for program in data.get("programList", {}).get("program", []) or []:
        if program:
            remark_obj = Remark(container=se, text="program={}".format(program))
            remark_obj.full_clean()
            remark_obj.save()

    # akaList
    for e_data in data.get("akaList", {}).get("aka", []) or []:
        create_ofac_alias(se, **e_data)

    # dateOfBirthList
    for e_data in data.get("dateOfBirthList", {}).get("dateOfBirthItem", []) or []:
        create_ofac_dob(se, **e_data)

    # placeOfBirthList
    for e_data in data.get("placeOfBirthList", {}).get("placeOfBirthItem", []) or []:
        create_ofac_place_of_birth(se, **e_data)

    # addressList
    for e_data in data.get("addressList", {}).get("address", []) or []:
        create_ofac_address(se, **e_data)

    # idList
    for e_data in data.get("idList", {}).get("id", []) or []:
        create_ofac_id(se, **e_data)

    se.full_clean()
    se.save()
    if verbose:
        logger.info("%sSaved %s", padding * " ", se)


def import_ofac_sanctions(source: SanctionsListFile, verbose: bool = False):
    data = load_ofac_sanction_list_as_dict(source.full_path)
    source.generation_date = parse_ofac_date(data["publshInformation"]["Publish_Date"])

    t0 = now()
    entities_list = data.get("sdnEntry", [])
    for se_data in entities_list:
        assert isinstance(se_data, dict)
        if verbose:
            logger.info("  sdnEntry uid %s", se_data.get("uid"))
        with transaction.atomic():
            se = SanctionEntity.objects.create(source=source, data=se_data)
            set_ofac_members(se, se_data, verbose=verbose, padding=4)

    source.imported = now()
    source.save()
    msg = "Imported {} sanction entities from {} in {}".format(
        len(entities_list), source.full_path, source.imported - t0
    )
    logger.info(msg)
    admin_log([source], msg)
