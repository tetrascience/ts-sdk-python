import sys
import json
import importlib
import argparse
import os
import base64

from .__task_script_runner import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--func', help='function slug', required=True)
    parser.add_argument('--correlation-id', help='correlation id')
    parser.add_argument('--input', help='input string', default='')
    parser.add_argument('--context', help='context', default='')
    parser.add_argument('--func-dir', help='function dir', default='./func')
    args = parser.parse_args()
    params = {
        'input': json.loads(base64.standard_b64decode(args.input)),
        'context_from_arg': json.loads(base64.standard_b64decode(args.context)),
        'func': args.func,
        'correlation_id': args.correlation_id,
        'func_dir': args.func_dir,
        'storage_type': os.environ.get('TASK_STORAGE_TYPE'),
        'storage_bucket': os.environ.get('TASK_STORAGE_S3FILE_BUCKET'),
        'storage_file_key': os.environ.get('TASK_STORAGE_S3FILE_FILE_KEY'),
        'storage_endpoint': os.environ.get('TASK_STORAGE_S3FILE_ENDPOINT'),
        'artifact_bucket': os.environ.get('ARTIFACT_S3FILE_BUCKET'),
        'artifact_prefix': os.environ.get('ARTIFACT_S3FILE_PREFIX'),
        'artifact_endpoint': os.environ.get('ARTIFACT_S3FILE_ENDPOINT'),
        'artifact_file_key': os.environ.get('ARTIFACT_IDS_SCHEMA_S3FILE_FILE_KEY'),
        'artifact_bucket_private': os.environ.get('ARTIFACT_S3FILE_BUCKET_PRIVATE'),
        'artifact_prefix_private': os.environ.get('ARTIFACT_S3FILE_PREFIX_PRIVATE'),
        'artifact_endpoint_private': os.environ.get('ARTIFACT_S3FILE_ENDPOINT_PRIVATE'),
        'command_endpoint': os.environ.get('COMMAND_ENDPOINT')
    }
    sys.path.append(params['func_dir'])

    run(**params)
