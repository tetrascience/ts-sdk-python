import os
import sys
import json
import jsonschema
from importlib import import_module
from pytest import fixture
import ts_sdk.schemas as s

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

@fixture
def config():
    with open("./config.json") as f:
        return json.load(f)


@fixture
def protocol():
    with open("../master-script/protocol.json") as f:
        return json.load(f)


def test_config_schema(config):
    jsonschema.validate(config, s.config)


def test_funcs(config):
    for fn in config["functions"]:
        qname = fn["function"]
        mod, func = qname.split(".")
        assert hasattr(import_module(mod), func), f"unable to find function {qname}"
        assert func == fn["slug"]


def test_protocol_schema(protocol):
    jsonschema.validate(protocol, s.protocol)
