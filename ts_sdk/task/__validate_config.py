import importlib
import sys
import pathlib
import json


def main(func_dir):
    sys.path.append(func_dir)
    with (pathlib.Path(func_dir) / "config.json").open() as f:
        func_conf = json.load(f)
    slugs = set()
    for func in func_conf["functions"]:
        slug = func["slug"]
        if slug in slugs:
            sys.exit(f"Duplicate function slug {slug}")
        slugs.add(slug)

        func_module, _, func_name = func["function"].rpartition(".")
        if not hasattr(importlib.import_module(func_module), func_name):
            sys.exit(f"Unable to resolve function {func_name} in module {func_module}")


if __name__ == "__main__":
    main(sys.argv[1])
