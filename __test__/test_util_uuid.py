import sys
import os
import pytest

from ts_sdk.task.__util_uuid import generate_uuid, get_next_uuid


def test_expected_behaviour():
    uuid = get_next_uuid()
    assert uuid
    assert get_next_uuid() == uuid
    assert generate_uuid() == uuid
    assert get_next_uuid() != uuid
    assert generate_uuid() != uuid