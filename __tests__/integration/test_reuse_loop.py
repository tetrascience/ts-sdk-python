import sys
import os
import json
import datetime
import pytest
from unittest import TestCase
from unittest.mock import MagicMock

import boto3
import responses


class ReuseLoopTest(TestCase):

    def setUp(self):
        s3_endpoint = 'http://localhost:4569/'
        datalake_bucket = 'datalake_bucket'

        self.input_file = {
            'bucket': datalake_bucket,
            'fileKey': 'test/abc/RAW/input.json'
        }

        self.s3 = boto3.client(
            's3', 
            endpoint_url=s3_endpoint,
            aws_access_key_id='123', 
            aws_secret_access_key='abc',
            region_name='us-east-2'
        )
        self.s3.put_object(
            Body=json.dumps({}),
            Bucket=datalake_bucket,
            Key=self.input_file['fileKey'],
            ContentType='application/json'
        )

        os.environ.update({
            'PLATFORM_PROPS_HASH': 'PLATFORM_PROPS_HASH',
            'TASK_GROUP_HASH': 'TASK_GROUP_HASH',
            'CONTAINER_ID': 'CONTAINER_ID',

            'ENV': 'test',
            'DISABLE_GZIP': 'true',

            'TASK_SCRIPTS_CONTAINERS_MODE': 'ecs',

            'TASK_STORAGE_TYPE': 's3file',
            'TASK_STORAGE_S3FILE_BUCKET': 'task_storage_bucket',
            'TASK_STORAGE_S3FILE_FILE_KEY': 'task_storage_file_key',
            'TASK_STORAGE_S3FILE_ENDPOINT': s3_endpoint,

            'ARTIFACT_S3FILE_BUCKET': 'artifact',
            'ARTIFACT_S3FILE_PREFIX': 'test_',
            'ARTIFACT_S3FILE_ENDPOINT': s3_endpoint,

            'ARTIFACT_IDS_SCHEMA_S3FILE_FILE_KEY': 'zzz',

            'ARTIFACT_S3FILE_BUCKET_PRIVATE': 'artifact_private',
            'ARTIFACT_S3FILE_PREFIX_PRIVATE': 'test_',
            'ARTIFACT_S3FILE_ENDPOINT_PRIVATE': s3_endpoint,

            'COMMAND_ENDPOINT': 'http://command.local',
            'FILEINFO_ENDPOINT': 'http://fileinfo.local',
            'ORCHESTRATOR_ENDPOINT': 'http://orchestrator.local',

            'SECRET_pass_word': 'secret-password-value',
        })

        self.tasks = [
            {
                'id': 'task_id',
                'data': {
                    'workflow_id': 'workflow_id',
                    'secrets': {},
                    'input': {
                        'inputFile': self.input_file,
                        'pass': {
                            'ssm': '/development/diagnostic/org-secrets/pass-word'
                        },
                        'newFileName': 'new_file_name'
                    },
                    'context': {
                        'taskId': 'task_id',
                        'orgSlug': 'test',
                        'inputFile': self.input_file,
                        'pipelineId': '1298e6a3-abc7-4c96-984f-376700c35f83',
                        'taskScript': 'common/test-task:v1.0.0',
                        'workflowId': '0b8a3a9c-299a-45ac-b877-05b262e6caf6',
                        'platformUrl': 'http://platform.test',
                        'masterScript': 'common/test:v1.0.0',
                        'protocolSlug': 'test-protocol',
                        'pipelineConfig': {},
                        'protocolVersion': 'v1.0.0',
                        'masterScriptSlug': 'test-protocol',
                        'masterScriptVersion': 'v1.0.0',
                        'masterScriptNamespace': 'common',
                    },
                    'funcDir': os.path.join(os.path.dirname(__file__), 'mocks'),
                    'func': 'test'
                }
            }
        ]

        from ts_sdk.task.run_reuse_loop import main
        self.mainFn = main

    def tearDown(self):
        pass

    def _poll_callback(self, r):
        if len(self.tasks):
            return 200, {}, json.dumps(self.tasks.pop())
        return 409, {}, '{}'
        
    @responses.activate
    def test_main_all_in_one(self):
        responses.add(
            responses.POST, 
            'http://orchestrator.local/task/task_id/update-status',
            json={},
            status=200
        )
        responses.add_callback(
            responses.POST, 
            'http://orchestrator.local/task/poll',
            callback=self._poll_callback
        )
        shared_dict = self.mainFn()
        assert shared_dict['result'] == {'status': 'completed', 'result': True}
        assert shared_dict['error'] == None
