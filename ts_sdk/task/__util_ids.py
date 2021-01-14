import os
import json
import boto3
import jsonschema
import re

def create_ids_util(locations):

    def get_location(namespace):
        for location in locations:
            if re.search(location['namespacePattern'], namespace):
                return location
        raise Exception(f'Invalid namespace: {namespace}')

    def get_ids(namespace, slug, version):
        location = get_location(namespace)
        bucket = location['bucket']
        prefix = location['prefix']
        endpoint = location['endpoint']
        if endpoint:
            s3 = boto3.client(
                's3', endpoint_url=endpoint,
                aws_access_key_id='123', aws_secret_access_key='abc')
        else:
            s3 = boto3.client('s3')

        file_key = os.path.join(prefix, 'ids', namespace, slug, version, 'schema.json')
        print(f'downloading ids, {bucket}, {file_key}')
        try:
            read_response = s3.get_object(Bucket=bucket, Key=file_key)
            status_code = read_response.get('ResponseMetadata', {}).get('HTTPStatusCode')
            body = read_response.get('Body').read().decode('utf-8')
            return json.loads(body)
        except Exception as e:
            raise Exception(f'Failed to get IDS, {namespace}/{slug}:{version} from bucket: {bucket}, file_key: {file_key}.') from e

    def validate_ids(data, namespace, slug, version):
        ids = get_ids(namespace, slug, version)
        
        validator = jsonschema.Draft7Validator(ids)
        has_error = False
        
        # https://python-jsonschema.readthedocs.io/en/stable/validate/#jsonschema.IValidator.iter_errors
        for error in sorted(validator.iter_errors(data), key=str):
            has_error = True
            print('error: ' + error.message + ' at path: ' + str(list(error.schema_path)))

        if has_error:
            raise Exception(f'Failed validation against IDS: {namespace}/{slug}:{version}')


    return { 'get_ids': get_ids, 'validate_ids': validate_ids }
