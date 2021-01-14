import typing as t


def merge_arrays(base="", additions: t.Iterable[str] = []) -> str:
    tags = set(base.split(","))
    for tag in additions:
        if tag in tags:
            raise ValueError(f"Custom tag {tag} is specified multiple times")
        tags.add(tag)
    additions_str = ",".join(additions)
    return _join(base, additions_str, ",")


def merge_objects(base="", additions: t.Mapping[str, str] = {}):
    keys = set(kv.split("=")[0] for kv in base.split("&"))
    for key in additions.keys():
        if key in keys:
            raise ValueError(f"Custom metadata key {key} is already specified")
        keys.add(key)
    additions_str = "&".join(f"{key}={value}" for (key, value) in additions.items())
    return _join(base, additions_str, "&")


def _join(a: str, b: str, sep: str) -> str:
    if a == "":
        return b
    elif b == "":
        return a
    else:
        return a + sep + b

