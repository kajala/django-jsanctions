import logging
from typing import Dict, Any, Callable, Optional
import pytz

logger = logging.getLogger(__name__)


def get_country_iso2_code(country_description: str) -> str:
    country = country_description.lower()
    for k, v in pytz.country_names.items():
        if v.lower() == country:
            return k
    return ""


def dict_filter_attributes(data: Dict[str, Any], fn: Optional[Callable[[str, Any], Any]] = None) -> Dict[str, Any]:
    if isinstance(data, dict):
        for k, v in list(data.items()):
            if isinstance(v, dict):
                v = dict_filter_attributes(v, fn)
            elif isinstance(v, list):
                v = [dict_filter_attributes(e, fn) for e in v]
            elif k.startswith("@") and len(k) > 1 and isinstance(v, str):
                if fn is not None:
                    v = fn(k, v)
            data[k] = v
    return data
