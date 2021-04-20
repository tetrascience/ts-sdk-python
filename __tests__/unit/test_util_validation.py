import sys
import os
import pytest

from ts_sdk.task.__util_validation import validate_file_meta, validate_file_tags, validate_file_labels


def test_validate_file_meta():
    assert validate_file_meta(None)
    assert validate_file_meta({'some': 'stuff,-_ hello', 'bool': True, 'int': 123})
    with pytest.raises(ValueError):
        validate_file_meta({'some-bad': 'stuff'})
        validate_file_meta({'some': 'stuff@'})

def validate_file_tags():
    assert validate_file_tags(['some', 'stuff', 123, True, {}])
    with pytest.raises(ValueError):
        validate_file_tags(['some@', 'stuff'])
        validate_file_tags(['some', 'stuff$'])
    
def test_validate_file_labels():
    assert validate_file_labels(None)
    assert validate_file_labels([
        {'name': 'some', 'value': 'stuff'}, 
        {'name': 'bool', 'value': False},
        {'name': 'int', 'value': 123}
    ])
    with pytest.raises(ValueError):
        validate_file_labels([{'name': 'some-bad', 'value': 'stuff'}])
        validate_file_labels([{'name': 'some', 'value': 'stuff@'}])

