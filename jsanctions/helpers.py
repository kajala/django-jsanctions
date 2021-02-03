from typing import Dict, Any


def dict_filter_attributes(data: Dict[str, Any], fn) -> Dict[str, Any]:
    if isinstance(data, dict):
        for k, v in list(data.items()):
            if isinstance(v, dict):
                v = dict_filter_attributes(v, fn)
            elif isinstance(v, list):
                v = [dict_filter_attributes(e, fn) for e in v]
            elif k.startswith("@") and len(k) > 1 and isinstance(v, str):
                v = fn(k, v)
            data[k] = v
    return data
