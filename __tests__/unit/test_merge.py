import sys
import os
import pytest

from ts_sdk.task.__util_merge import merge_arrays, merge_objects


def test_merge_objects_handles_valid_inputs():
    assert merge_objects("foo=bar", {"some": "stuff"}) == "foo=bar&some=stuff"
    assert merge_objects("", {"foo": "bar"}) == "foo=bar"
    assert merge_objects("foo=bar", {}) == "foo=bar"
    assert merge_objects("", {}) == ""


def test_merge_objects_rejects_repeats():
    with pytest.raises(ValueError):
        merge_objects("foo=bar", {"foo": "bar"})
    with pytest.raises(ValueError):
        merge_objects("foo=bar", {"foo": "baz"})


def test_merge_arrays_handles_valid_inputs():
    assert merge_arrays("foo", ["bar"]) == "foo,bar"
    assert merge_arrays("", ["bar"]) == "bar"
    assert merge_arrays("foo", []) == "foo"
    assert merge_arrays("", []) == ""


def test_merge_arrays_rejects_repeats():
    with pytest.raises(ValueError):
        merge_arrays("foo", ["foo"])

