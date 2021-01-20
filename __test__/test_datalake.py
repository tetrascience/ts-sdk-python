import sys
import os
import datetime
import pytest
from unittest.mock import MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ts_sdk"))
from task.__util_datalake import Datalake
from task.__util_metadata import FIELDS

def test_datalake_update_metadata_tags():
    d = Datalake('http://localhost:4569/')
    d.s3.head_object = MagicMock(return_value={
        'Metadata': {
            FIELDS['FILE_ID']: 'file_id',
            FIELDS['CUSTOM_METADATA']: 'meta_k_1=meta_v_1&meta_k_2=meta_v_2',
            FIELDS['CUSTOM_TAGS']: 'tag1,tag2'
        },
        'LastModified': datetime.datetime(2021, 1, 1),
        'ContentType': 'text/plain'
    })
    d.s3.copy_object = MagicMock(return_value={})
    f = {
        'bucket': 'test-bucket',
        'fileKey': 'test/file/key'
    }
    meta = {'meta_k_3': 'meta_v_3', 'meta_k_4': 'meta_v_4', 'meta_k_1': None}
    tags = ['tag3', 'tag4', 'tag4']
    d.update_metadata_tags(f, meta, tags)

    d.s3.copy_object.assert_called_once()
    args, kwargs = d.s3.copy_object.call_args
    assert kwargs['CopySource'] == '/test-bucket/test/file/key'
    assert kwargs['Metadata'][FIELDS['CUSTOM_METADATA']] == 'meta_k_2=meta_v_2&meta_k_3=meta_v_3&meta_k_4=meta_v_4'
    assert kwargs['Metadata'][FIELDS['CUSTOM_TAGS']] == 'tag1,tag2,tag3,tag4'
