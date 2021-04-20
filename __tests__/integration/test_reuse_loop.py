import sys
import os
import json
import datetime
import pytest
from unittest import TestCase
from unittest.mock import MagicMock

import responses


class ReuseLoopTest(TestCase):

    def setUp(self):
        s3_endpoint = 'http://localhost:4569/'
        os.environ.update({
            'PLATFORM_PROPS_HASH': 'PLATFORM_PROPS_HASH',
            'TASK_GROUP_HASH': 'TASK_GROUP_HASH',
            'CONTAINER_ID': 'CONTAINER_ID',

            'ENV': 'test',
            'AWS_REGION': 'test-region-2',
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
            'ORCHESTRATOR_ENDPOINT': 'http://orchestrator.local'
        })

        from ts_sdk.task.run_reuse_loop import main
        self.mainFn = main

    def tearDown(self):
        pass
        
    @responses.activate
    def test_main_should_exit_poll_409(self):
        responses.add(
            responses.POST, 
            'http://orchestrator.local/task/poll',
            json={}, 
            status=409
        )
        self.mainFn()

    @responses.activate
    def test_main_next(self):
        tasks = [
            {
                'id': 'task_id',
                'data': {
                    'workflow_id': 'workflow_id',
                    'secrets': {},
                    'input': {},
                    'context': {
                        'orgSlug': 'test',
                        'inputFile': {},
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
        responses.add(
            responses.POST, 
            'http://orchestrator.local/task/task_id/update-status',
            json={},
            status=200
        )
        responses.add_callback(
            responses.POST, 
            'http://orchestrator.local/task/poll',
            callback=lambda r: (200 if len(tasks) else 409, {}, json.dumps(tasks.pop() if len(tasks) else {}))
        )
        self.mainFn()
