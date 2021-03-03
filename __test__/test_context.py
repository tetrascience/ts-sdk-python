import sys
import os
import datetime
import pytest
from unittest.mock import MagicMock

from ts_sdk.task.__task_script_runner import Context

class LogMock:
    def log(self, data):
        print(data)

class DatalakeMock:
    def read_file(self, *args, **kwargs):
        return {'_func': 'datalake.read_file'}

    def write_file(self, *args, **kwargs):
        return {'_func': 'datalake.write_file'}

    def write_ids(self, *args, **kwargs):
        return {'_func': 'datalake.write_ids'}

    def get_file_meta(self, file):
        return {'_func': 'datalake.get_file_meta'}

    def get_file_name(self, file):
        return 'filename'

    def get_presigned_url(self, *args, **kwargs):
        return 'presigned_url'

    def update_metadata_tags(self, *args, **kwargs):
        return {'_func': 'datalake.update_metadata_tags'}

idsMock = {
    'get_ids': lambda *args, **kwargs: {},
    'validate_ids': lambda *args, **kwargs: True
}

class CommandMock:
    def run_command(self, *args, **kwarg):
        return {'_func': 'command.run_commands'}

class FileinfoMock:
    def add_labels(self, *args, **kwarg):
        return {'_func': 'fileinfo.add_labels'}
    def get_labels(self, *args, **kwarg):
        return {'_func': 'fileinfo.get_labels'}
    def delete_labels(self, *args, **kwarg):
        return {'_func': 'fileinfo.delete_labels'}

def test_context_public_interface():
    os.environ['TASK_SCRIPTS_CONTAINERS_MODE'] = 'ecs'
    os.environ['TS_SECRET_password'] = 'secretvalue'

    log = LogMock()

    input_file = {
        'type': 's3',
        'bucket': 'bucket',
        'fileKey': 'some/fileKey'
    }

    pipeline_config = {
        'ts_secret_name_password': 'some/kms/path'
    }

    Context.log = log
    c = Context(
        {
            'inputFile': input_file,
            'pipelineConfig': pipeline_config
        },
        DatalakeMock(),
        idsMock,
        log,
        CommandMock(),
        FileinfoMock()
    )

    r = c.read_file(input_file)
    assert r == {'_func': 'datalake.read_file'}

    r = c.write_file('content', 'file_name', 'RAW')
    assert r == {'_func': 'datalake.write_file'}

    r = c.get_ids('namespace', 'slug', 'version')
    assert r == {}

    r = c.validate_ids('data', 'namespace', 'slug', 'version')
    assert r == True

    r = c.write_ids('content', 'file_suffix')
    assert r == {'_func': 'datalake.write_ids'}

    r = c.get_file_name(input_file)
    assert r == 'filename'

    r = c.get_logger()
    assert r == log

    r = c.get_secret_config_value('password')
    assert r == 'secretvalue'

    r = c.get_presigned_url(input_file)
    assert r == 'presigned_url'

    r = c.update_metadata_tags(input_file, {'meta1': 'v1'}, ['t1', 't2'])
    assert r == {'_func': 'datalake.update_metadata_tags'}

    r = c.run_command('org_slug', 'target_id', 'action', {'meta1': 'v1'}, 'payload')
    assert r == {'_func': 'command.run_commands'}

    label_file = {}
    r = c.add_labels(label_file, [{'meta1': 'v1'}])
    assert r == {'_func': 'fileinfo.add_labels'}

    r = c.get_labels(label_file)
    assert r == {'_func': 'fileinfo.get_labels'}

    r = c.delete_labels(label_file, [1,2,3])
    assert r == {'_func': 'fileinfo.delete_labels'}
