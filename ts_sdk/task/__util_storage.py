import logging
import boto3
import json

class Storage:
    def __init__(self, bucket, file_key, endpoint):
        self.bucket = bucket
        self.file_key = file_key
        if endpoint:
            self.s3 = boto3.client(
                's3', endpoint_url=endpoint,
                aws_access_key_id='123', aws_secret_access_key='abc')
        else:
            self.s3 = boto3.client('s3')

    def writeObject(self, obj):
        full_file_key = self.file_key.format(**obj)
        response = self.s3.put_object(
            Bucket=self.bucket, Key=full_file_key, Body=json.dumps(obj))
        logging.info(response)
