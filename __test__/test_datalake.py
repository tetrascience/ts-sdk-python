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
            FIELDS['CUSTOM_METADATA']: 'meta_k_1=meta_v_1&meta_k_2=meta_v_2'
        },
        'LastModified': datetime.datetime(2021, 1, 1, 22, 24, 8),
        'ContentType': 'text/plain'
    })
    d.s3.copy_object = MagicMock(return_value={})
    f = {
        'bucket': 'test-bucket',
        'fileKey': 'test/file/key'
    }
    meta = {'meta_k_3': 'meta_v_4', 'meta_k_5': 'meta_v_5', 'meta_k_1': None}
    tags = ['tag1', 'tag2']
    d.update_metadata_tags(f, meta, tags)

    d.s3.copy_object.assert_called_once()
    kwargs = d.s3.copy_object.call_args.kwargs
    assert kwargs['CopySource'] == '/test-bucket/test/file/key'
    assert kwargs['Metadata'][FIELDS['CUSTOM_METADATA']] == 'meta_k_2=meta_v_2&meta_k_3=meta_v_4&meta_k_5=meta_v_5'
    assert kwargs['Metadata'][FIELDS['CUSTOM_TAGS']] == 'tag1,tag2'
