import json
import os
import sys
from main import convert, decorate


def test_basic(shared_datadir):
    with (shared_datadir / "input.json").open() as input_file:
        result = convert(input_file)
    with (shared_datadir / "expected.json").open() as expected_file:
        expected = json.load(expected_file)
    assert result == expected


def test_decorate():
    assert decorate({"a": "1"}, "label") == {"a": "1", "label": "label"}
