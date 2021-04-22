import sys
import os
import datetime
import pytest
from unittest import TestCase
from unittest.mock import MagicMock

from ts_sdk.task.__task_script_runner import Context

class LogMock:
    def log(self, data):
        print(data)


class ContextMethodsTest(TestCase):
    def setUp(self):
        os.environ['TASK_SCRIPTS_CONTAINERS_MODE'] = 'ecs'
        os.environ['TS_SECRET_password'] = 'secretvalue'

        self.logMock = LogMock()
    
        self.datalakeMock = MagicMock()
        self.datalakeMock.get_file_name = MagicMock(return_value='filename')
        self.datalakeMock.get_presigned_url = MagicMock(return_value='presigned_url')

        self.idsMock = {
            'get_ids': MagicMock(return_value={}),
            'validate_ids': MagicMock(return_value=True)
        }

        self.commandMock = MagicMock()
        self.fileinfoMock = MagicMock()

        self.input_file = {
            'type': 's3',
            'bucket': 'bucket',
            'fileKey': 'some/fileKey',
            'fileId': '11111111-eeee-4444-bbbb-222222222222'
        }

        self.pipeline_config = {
            'ts_secret_name_password': 'some/kms/path'
        }

        Context.log = self.logMock
        self.ctx = Context(
            {
                'inputFile': self.input_file,
                'pipelineConfig': self.pipeline_config
            },
            self.datalakeMock,
            self.idsMock,
            self.logMock,
            self.commandMock,
            self.fileinfoMock
        )

    def tearDown(self):
        pass

    def test_read_file(self):
        self.ctx.read_file(self.input_file)
        self.datalakeMock.read_file.assert_called_once()

    def test_write_file(self):
        self.ctx.write_file('content', 'file_name', 'RAW')
        self.datalakeMock.write_file.assert_called_once()

    def test_get_ids(self):
        r = self.ctx.get_ids('namespace', 'slug', 'version')
        assert r == {}

    def test_validate_ids(self):
        r = self.ctx.validate_ids('data', 'namespace', 'slug', 'version')
        assert r == True

    def test_write_ids(self):
        self.ctx.write_ids('content', 'file_suffix')
        self.datalakeMock.write_ids.assert_called_once()

    def test_get_file_name(self):
        r = self.ctx.get_file_name(self.input_file)
        assert r == 'filename'

    def test_get_logger(self):
        self.ctx.get_logger()
        assert self.ctx.get_logger() == self.logMock

    def test_get_secret_config_value(self):
        r = self.ctx.get_secret_config_value('password')
        assert r == 'secretvalue'

    def test_get_presigned_url(self):
        r = self.ctx.get_presigned_url(self.input_file)
        assert r == 'presigned_url'

    def test_update_metadata_tags(self):
        self.ctx.update_metadata_tags(self.input_file, {'meta1': 'v1'}, ['t1', 't2'])
        self.datalakeMock.update_metadata_tags.assert_called_once()

    def test_run_command(self):
        self.ctx.run_command('org_slug', 'target_id', 'action', {'meta1': 'v1'}, 'payload')
        self.commandMock.run_command.assert_called_once()

    def test_add_labels(self):
        self.ctx.add_labels(self.input_file, [{'name': 'label1', 'value': 'label-value-1'}])
        self.fileinfoMock.add_labels.assert_called_once()

    def test_get_labels(self):
        self.ctx.get_labels(self.input_file)
        self.fileinfoMock.get_labels.assert_called_once()

    def test_delete_labels(self):
        self.ctx.delete_labels(self.input_file, [1,2,3])
        self.fileinfoMock.delete_labels.assert_called_once()

    def test_add_attributes_labels_only(self):
        self.ctx.add_attributes(
            self.input_file,
            labels=[{'name': 'label-name', 'value': 'label-value'}]
        )
        self.fileinfoMock.add_labels.assert_called_once()
        self.datalakeMock.create_labels_file.assert_not_called()
        self.datalakeMock.update_metadata_tags.assert_not_called()

    def test_add_attributes_all_attrs(self):
        self.ctx.add_attributes(
            self.input_file, 
            custom_meta={'m1': 'v1'},
            custom_tags=['t1'],
            labels=[{'name': 'label-name', 'value': 'label-value'}]
        )
        self.fileinfoMock.add_labels.assert_not_called()
        self.datalakeMock.update_metadata_tags.assert_called_once()
        self.datalakeMock.create_labels_file.assert_called_once()
        create_labels_file_arg = self.datalakeMock.create_labels_file.call_args[1]['target_file']
        update_metadata_tags_options_arg = self.datalakeMock.update_metadata_tags.call_args[1]['options']
        assert create_labels_file_arg['fileId'] == update_metadata_tags_options_arg['new_file_id']