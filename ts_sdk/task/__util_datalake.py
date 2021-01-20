import os
import logging
import boto3
from botocore.client import Config
import gzip
import re
from uuid import uuid4
import json
import query_string
import smart_open.s3
import shutil
import tempfile
import io
from urllib.parse import urlencode

from .__util_versioned_ref import VersionedRef
from .__util_metadata import FIELDS

DISABLE_GZIP = os.environ.get('DISABLE_GZIP')
ENV = os.environ.get('ENV')
AWS_REGION = os.environ.get('AWS_REGION')
MULTIPART_SIZE = 100 * 1024 * 1024 # don't use multipart if file size is smaller than 100MB

def get_kms_key_name(org_slug):
    return f'alias/customer-key-{ENV}-{org_slug}'

def lowerMetadataKeys(metadata):
    m = {}
    for key, value in metadata.items():
        m[key.lower()] = value
    return m

def resolveCustomMetadataAndTags(metadata):
    custom_metadata_str = metadata.get(FIELDS["CUSTOM_METADATA"], "") or ""
    custom_tags_str = metadata.get(FIELDS["CUSTOM_TAGS"], "") or ""
    if not custom_tags_str:
        custom_tags = []
    else:
        custom_tags = custom_tags_str.split(",")

    return {
        'custom_metadata': query_string.parse(custom_metadata_str),
        'custom_tags': custom_tags
    }

def getOrEmptyString(dic, key, default=''):
    val = dic.get(key, default)
    if val is None:
        return default
    return val

class S3FileobjUploader:
    def __init__(self, s3, fileobj, params, options={'disable_gzip': False}):
        self.s3 = s3
        self.fileobj = fileobj
        self.params = params
        self.disable_gzip = options.get('disable_gzip', False)
        self.stream = io.BytesIO()
        self.partCount = 0
        self.multipart = None
        self.parts = []
        if not self.disable_gzip:
            self.compressor = gzip.GzipFile(fileobj=self.stream, mode='w')

    def _uploadPart(self):
        print(f'upload multipart {self.partCount}')
        if self.partCount == 0:
            self.multipart = self.s3.create_multipart_upload(**self.params)
        self.partCount += 1
        self.stream.seek(0)
        part = self.s3.upload_part(
            Body=self.stream,
            Bucket=self.multipart['Bucket'],
            Key=self.multipart['Key'],
            PartNumber=self.partCount,
            UploadId=self.multipart['UploadId'])
        self.parts.append({ **part, 'PartNumber': self.partCount })
        self.stream.seek(0)
        self.stream.truncate()

    def _uploadLastPart(self):
        if self.partCount == 0:
            self.stream.seek(0)
            return self.s3.put_object(
                Body=self.stream,
                **self.params)
        else:
            self._uploadPart()
            parts = []
            for part in self.parts:
                parts.append({
                    'ETag': part['ETag'],
                    'PartNumber': part['PartNumber']
                })
            return self.s3.complete_multipart_upload(
                Bucket=self.multipart['Bucket'],
                Key=self.multipart['Key'],
                UploadId=self.multipart['UploadId'],
                MultipartUpload={ 'Parts': parts })

    def upload(self):
        while True:
            chunk = self.fileobj.read(1024 * 1024)
            if not chunk:
                if not self.disable_gzip:
                    self.compressor.close()
                return self._uploadLastPart()
            if self.disable_gzip:
                self.stream.write(chunk)
            else:
                self.compressor.write(chunk)
            if self.stream.tell() >= MULTIPART_SIZE:
                self._uploadPart()

class Datalake:
    def __init__(self, endpoint):
        if endpoint:
            self.s3 = boto3.client(
                's3', endpoint_url=endpoint,
                aws_access_key_id='123', aws_secret_access_key='abc',
                region_name=AWS_REGION, config=Config(signature_version='s3v4'))
            self.resource_kwargs = { 'endpoint_url': endpoint }
        else:
            self.s3 = boto3.client('s3', region_name=AWS_REGION, config=Config(signature_version='s3v4'))
            self.resource_kwargs = None

    def get_s3_head(self, file):
        bucket = file['bucket']
        file_key = file['fileKey']
        if 'version' in file:
            file_version = file['version']
            head = self.s3.head_object(Bucket=bucket, Key=file_key, VersionId=file_version)
        else:
            head = self.s3.head_object(Bucket = bucket, Key = file_key)
            
        return head

    def get_file_meta(self, file):
        head = self.get_s3_head(file)
        return lowerMetadataKeys(head.get('Metadata'))

    def read_file(self, file, form='body'):
        bucket = file['bucket']
        file_key = file['fileKey']
        if 'version' in file:
            kwargs = {'VersionId': file['version']}
        else:
            kwargs = {}

        if form == 'body':
            response = self.s3.get_object(Bucket=bucket, Key=file_key, **kwargs)
        elif form in ['file_obj', 'download']:
            response = self.s3.head_object(Bucket=bucket, Key=file_key, **kwargs)
        else:
            raise ValueError(f'Invalid form={form}; supported values are body, file_obj and download')

        status_code = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
        if not status_code == 200:
            logging.error(response)
            raise Exception('Invalid response code')

        meta = lowerMetadataKeys(response.get('Metadata'))
        result = { 'metadata': meta, **resolveCustomMetadataAndTags(meta) }

        if form == 'body':
            content = response.get('Body').read()
            if response.get('ContentEncoding') == 'gzip':
                result['body'] = gzip.decompress(content)
            else:
                result['body'] = content
        else:
            file_obj = smart_open.s3.open(bucket, file_key, 'rb', file.get('version'), resource_kwargs=self.resource_kwargs)
            if response.get('ContentEncoding') == 'gzip':
                file_obj = gzip.open(file_obj)

            if form == 'download':
                with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tf:
                    shutil.copyfileobj(file_obj, tf)
                    result['download'] = tf.name
                file_obj.close()
            else:
                result['file_obj'] = file_obj

        return result

    def write_file(self, context, content, file_name, file_category, raw_file, file_meta, ids = None, source_type = None):
        bucket = raw_file['bucket']
        raw_file_key = raw_file['fileKey']
        if file_category == 'IDS' and ids is None:
            raise Exception(f'ids can not be None when file_category is IDS')
        ids_obj = VersionedRef(composite=ids)
        pattern = '(.*?)/(.*?)/(?:.*?)/(.*)'
        match = re.match(pattern, raw_file_key)
        if not match:
            raise Exception(f'Raw file key {raw_file_key} does not match "{pattern}"')

        if source_type is not None:
            source_type_match = re.match('^[-a-z0-9]+$', source_type)
            if not source_type_match:
                raise Exception(f'Source type "{source_type}" contains invalid character or upper case letter')
        else:
            source_type = getOrEmptyString(file_meta, FIELDS['SOURCE_TYPE'], 'unknown')

        org_slug, source_id, raw_file_path = match.groups()
        file_key = os.path.join(org_slug, source_id, file_category, raw_file_path, file_name)
        file_id = str(uuid4())
        pipelineConfig = context.get('pipelineConfig', {})
        meta = {
            # constant
            FIELDS['INTEGRATION_TYPE']: 'datapipeline',
            FIELDS['VERSION']: '2',

            # generated
            FIELDS['FILE_ID']: file_id,

            # from raw file
            FIELDS['RAW_FILE_ID']: getOrEmptyString(file_meta, FIELDS['FILE_ID']),
            FIELDS['CUSTOM_METADATA']: getOrEmptyString(file_meta, FIELDS['CUSTOM_METADATA']),
            FIELDS['CUSTOM_TAGS']: getOrEmptyString(file_meta, FIELDS['CUSTOM_TAGS']),
            FIELDS['SOURCE_NAME']: getOrEmptyString(file_meta, FIELDS['SOURCE_NAME']),
            FIELDS['SOURCE_TYPE']: source_type,
            FIELDS['TRACE_ID']: getOrEmptyString(file_meta, FIELDS['TRACE_ID']),

            # IDS
            **({
                FIELDS['IDS']: ids_obj.composite,
                FIELDS['IDS_TYPE']: ids_obj.name,
                FIELDS['IDS_VERSION']: ids_obj.version,
            } if file_category == 'IDS' else {}),

            # from pipeline context
            FIELDS['INTEGRATION_ID']: getOrEmptyString(context, 'pipelineId'), # pipeline id
            # https://github.com/tetrascience/ts-service-pipeline/blob/development/src/models/create-workflow-command.js#L171
            FIELDS['INTEGRATION_NAME']: getOrEmptyString(pipelineConfig, 'pipelineName'),
            FIELDS['PIPELINE_ID']: getOrEmptyString(context, 'pipelineId'),
            FIELDS['PIPELINE_WORKFLOW_ID']: getOrEmptyString(context, 'workflowId'),
            FIELDS['PIPELINE_MASTER_SCRIPT']: f"{context.get('masterScriptNamespace', '')}/{context.get('masterScriptSlug', '')}:{context.get('masterScriptVersion', '')}",
            FIELDS['PIPELINE_TASK_EXECUTION_ID']: getOrEmptyString(context, 'taskId'),
            FIELDS['PIPELINE_TASK_SCRIPT']: getOrEmptyString(context, 'taskScript'),
            FIELDS['PIPELINE_TASK_SLUG']: getOrEmptyString(context, 'taskSlug')
        }

        params = {
            'Bucket': bucket,
            'Key': file_key,
            'Metadata': meta,
            'ServerSideEncryption': 'aws:kms',
            'SSEKMSKeyId': get_kms_key_name(org_slug),
            'ContentEncoding': 'gzip'
        }

        if hasattr(content, 'read'):
            response = S3FileobjUploader(
                self.s3, content, params, { 'disable_gzip': DISABLE_GZIP }).upload()
        else:
            if not DISABLE_GZIP:
                if (isinstance(content, str)):
                    content = content.encode()
                content = gzip.compress(content)
            response = self.s3.put_object(Body=content, **params)
        logging.info(response)
        return {
            'type': 's3file',
            'bucket': bucket,
            'fileKey': file_key,
            'fileId': file_id,
            # fakeS3 does not return VersionId, so use '' to avoid an exception
            'version': response.get('VersionId', '')
        }

    def update_metadata_tags(self, file, custom_meta, custom_tags):
        bucket = file['bucket']
        file_key = file['fileKey']

        head = self.get_s3_head(file)
        current_meta = lowerMetadataKeys(head.get('Metadata'))

        if not FIELDS['FILE_ID'] in current_meta:
            raise Exception('no FILE_ID in meta!')

        if (not custom_meta) and (not custom_tags):
            raise Exception('No metadata or tags provided')

        isASCII = lambda s: s and isinstance(s, str) and bool(re.match(r'^[\x00-\x7F]*$', s))
        
        custom_meta_str = current_meta.get(FIELDS['CUSTOM_METADATA'], '') or ''
        current_custom_meta = query_string.parse(custom_meta_str)
        if custom_meta:
            custom_meta_merged = {**current_custom_meta, **custom_meta}
            custom_meta_merged = {k:v for k,v in custom_meta_merged.items() if v is not None}
            for k,v in custom_meta_merged.items():
                if not isASCII(k):
                    raise Exception(f'Metadata key {k} contains non-ASCII character') 
                if not isASCII(v):
                    raise Exception(f'Metadata value {v} contains non-ASCII character')
            custom_meta_str = urlencode(custom_meta_merged)

        custom_tags_str = current_meta.get(FIELDS['CUSTOM_TAGS'], '')
        if custom_tags:
            for t in custom_tags:
                if not isASCII(t):
                    raise Exception(f'Tag {t} contains non-ASCII character') 
            new_custom_tags = list(set(custom_tags_str.split(',') + custom_tags))
            new_custom_tags.sort()
            custom_tags_str = ','.join(new_custom_tags)

        if len(custom_meta_str) + len(custom_tags_str) >= 1024 * 1.5:
            raise Exception('Metadata and tags length larger than 1.5KB') 
        
        params = {
            'Bucket': bucket,
            'CopySource': f'/{bucket}/{file_key}',
            # 'CopySourceIfUnmodifiedSince': head['LastModified'], # ensure no conflict?
            'Key': file_key,
            'ContentEncoding': head.get('ContentEncoding', None),
            'ContentType': head['ContentType'],
            'Metadata': {
                **current_meta,
                FIELDS['CUSTOM_METADATA']: custom_meta_str,
                FIELDS['CUSTOM_TAGS']: custom_tags_str
            },
            'MetadataDirective': 'REPLACE',
            'ServerSideEncryption': 'aws:kms',
            'SSEKMSKeyId': head.get('SSEKMSKeyId', None),
        }

        params = {k:v for k,v in params.items() if v is not None}
        response = self.s3.copy_object(**params)

        return {
            'type': 's3file',
            'bucket': bucket,
            'fileKey': file_key,
            'fileId': current_meta[FIELDS['FILE_ID']],
            # fakeS3 does not return VersionId, so use '' to avoid an exception
            'version': response.get('VersionId', '')
        }

    def write_ids(self, context, content_obj, file_suffix, raw_file, file_meta, ids, source_type):
        ids_obj = VersionedRef(composite=ids)
        file_name = f'{ids_obj.name}_{ids_obj.version}_{file_suffix}'
        result = self.write_file(context, json.dumps(content_obj, indent=4), file_name, 'IDS', raw_file, file_meta, ids, source_type)
        return result

    def get_file_name(self, file):
        file_key = file['fileKey']
        return os.path.basename(file_key)

    def get_presigned_url(self, file, ttl_sec):
        if ttl_sec == None or ttl_sec < 0 or ttl_sec > 900:
            raise Exception(f'Cannot generate pre-signed S3 URL, expiration in seconds must be between 0 and 900, and specified value is {ttl_sec}')

        bucket = file['bucket']
        key = file['fileKey']

        if 'version' in file:
            kwargs = {'VersionId': file['version']}
        else:
            kwargs = {}
        
        try:
            return self.s3.generate_presigned_url('get_object', Params={
                'Bucket': bucket,
                'Key': key,
                **kwargs
            }, ExpiresIn=ttl_sec)
        except Error as e:
            print(e)
        
        return None
