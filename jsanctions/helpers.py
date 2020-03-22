import re


def xml_dict_filter_attributes(data: dict, fn) -> dict:
    if isinstance(data, dict):
        for k, v in list(data.items()):
            if isinstance(v, dict):
                v = xml_dict_filter_attributes(v, fn)
            elif isinstance(v, list):
                v = [xml_dict_filter_attributes(e, fn) for e in v]
            elif k.startswith('@') and len(k) > 1 and isinstance(v, str):
                v = fn(k, v)
            data[k] = v
    return data


def camel_case_to_underscore(s: str) -> str:
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r'\1_\2', s)
    s = re.sub(r"([a-z\d])([A-Z])", r'\1_\2', s)
    s = s.replace("-", "_")
    return s.lower()
