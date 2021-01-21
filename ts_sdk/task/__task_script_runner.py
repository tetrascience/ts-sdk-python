import sys
import json
import importlib
import argparse
import os
import base64
import re
import typing as t
import typing_extensions as te
import uuid

from .types import FileCategory, File, ReadResult

from .__util_storage import Storage
from .__util_datalake import Datalake
from .__util_log import Log
from .__util_merge import merge_arrays, merge_objects
from .__util_metadata import FIELDS
from .__util_ids import create_ids_util
from .__util_command import Command

COMPLETED = 'completed'
FAILED = 'failed'

LOG_TAG_PRE_FUNCTION = 'pre_function_call'
LOG_TAG_POST_FUNCTION = 'post_function_call'
LOG_TAG_SCRIPT_STARTED = 'script_started'
LOG_TAG_SCRIPT_ENDED = 'script_ended'

if 'default_print' not in __builtins__:
  __builtins__['default_print'] = __builtins__['print']

def wrap_log(func_name):
    def return_wrapper(fn):
        def wrapper(*args, **kwargs):
            id = str(uuid.uuid4())
            Context.log.log({
                'level': 'debug',
                'tag': LOG_TAG_PRE_FUNCTION,
                'funcName': func_name,
                'id': id
            })
            result = fn(*args, **kwargs)
            Context.log.log({
                'level': 'debug',
                'tag': LOG_TAG_POST_FUNCTION,
                'funcName': func_name,
                'id': id
            })
            return result
        return wrapper
    return return_wrapper

def camel_to_snake(str) -> str:
    return ''.join(['_'+i.lower() if i.isupper() else i for i in str]).lstrip('_')

class Context:
    """A context object that is passed into
    the task script handler when running as part of a pipeline.
    """

    org_slug: str
    pipeline_id: str
    workflow_id: str

    master_script_namespace: str
    master_script_slug: str
    master_script_version: str

    input_file: File

    created_at: str
    task_id: str
    task_created_at: str

    pipeline_config: t.Dict[str, str]

    tmp_dir: str = '/tmp'


    def __init__(self, obj, datalake, ids_util, log, command):
        obj = { **obj, 'tmpDir': '/tmp' } # keys are later converted to snake case via "camel_to_snake"
        self._obj = obj
        for key in obj:
            setattr(self, camel_to_snake(key), obj[key])
        for key in ids_util:
            if callable(ids_util[key]):
                setattr(self, key, wrap_log(f'context.{key}')(ids_util[key]))
            else:
                setattr(self, key, ids_util[key])
        self.datalake = datalake
        self.log = log
        self.command = command

    @wrap_log('context.read_file')
    def read_file(self, file: File, form='body') -> ReadResult:
        """Reads a file from the data lake and returns its contents in one of
        three forms.

        If form='body' (the default), then result['body'] holds the contents of
        the file as a byte array. This approach cannot handle large files that
        don't fit in memory.

        If form='file_obj', then result['file_obj'] is a file-like object that
        can be used to access the body in a streaming manner. This object can
        be passed to Python libraries such as Pandas.

        If form='download', then result['download'] is the file name of a local
        file that has been downloaded from the specified data lake file. This
        is useful when the data needs to be processed by native code (e.g.
        SQLite) or an external utility program.

        >>> import json
        >>> import pandas as pd
        >>> import sqlite3
        >>> def task(input, context):
        ...     f = context.read_file(input, form='body')
        ...     json.loads(f['body'])
        ...
        ...     f = context.read_file(input, form='file_obj')
        ...     df = pd.read_csv(f['file_obj'])
        ...
        ...     f = context.read_file(input, form='download')
        ...     con = sqlite3.connect(f['download'])
        ...     df = pd.read_sql_query('SELECT * FROM foo', con)
        """

        return self.datalake.read_file(file, form)

    @wrap_log('context.update_metadata_tags')
    def update_metadata_tags(
        self,
        file: File,
        custom_meta: t.Dict[str, str] = {},
        custom_tags: t.Iterable[str] = []
    ) -> File:
        """Updates file's custom metadata and tags.
        Use 'None' to remove a meta entry.
        """
        return self.datalake.update_metadata_tags(file, custom_meta, custom_tags)

    @wrap_log('context.write_file')
    def write_file(
        self,
        content: t.Union[bytes, t.BinaryIO, str],
        file_name: str,
        file_category: FileCategory,
        ids: t.Optional[str] = None,
        custom_metadata: t.Mapping[str, str] = {},
        custom_tags: t.Iterable[str] = [],
        source_type: t.Optional[str] = None,
    ) -> File:
        """Writes an output file to the data lake
        """

        raw_file = self.input_file
        file_meta = {
            # in case custom_metadata & custom_tags are undefined in raw_file meta
            FIELDS['CUSTOM_METADATA']: '',
            FIELDS['CUSTOM_TAGS']: '',
            **self.datalake.get_file_meta(raw_file)
        }
        file_meta[FIELDS['CUSTOM_METADATA']] = merge_objects(
            file_meta.get(FIELDS['CUSTOM_METADATA'], ''), custom_metadata
        )
        file_meta[FIELDS['CUSTOM_TAGS']] = merge_arrays(
            file_meta.get(FIELDS['CUSTOM_TAGS'], ''), custom_tags,
        )
        return self.datalake.write_file(
            context=self._obj,
            content=content,
            file_name=file_name,
            file_category=file_category,
            raw_file=raw_file,
            file_meta=file_meta,
            ids=ids,
            source_type=source_type
        )

    @wrap_log('context.write_ids')
    def write_ids(
        self,
        content_obj,
        file_suffix: str,
        ids: t.Optional[str] = None,
        custom_metadata: t.Mapping[str, str] = {},
        custom_tags: t.Iterable[str] = [],
        source_type: t.Optional[str] = None
    ) -> File:
        raw_file = self.input_file
        file_meta = {
            # in case custom_metadata & custom_tags are undefined in raw_file meta
            FIELDS['CUSTOM_METADATA']: '',
            FIELDS['CUSTOM_TAGS']: '',
            **self.datalake.get_file_meta(raw_file)
        }
        file_meta[FIELDS['CUSTOM_METADATA']] = merge_objects(
            file_meta.get(FIELDS['CUSTOM_METADATA'], ''), custom_metadata
        )
        file_meta[FIELDS['CUSTOM_TAGS']] = merge_arrays(
            file_meta.get(FIELDS['CUSTOM_TAGS'], ''), custom_tags,
        )
        return self.datalake.write_ids(
            context=self._obj,
            content_obj=content_obj,
            file_suffix=file_suffix,
            raw_file=raw_file,
            file_meta=file_meta,
            ids=ids,
            source_type=source_type
        )

    def get_file_name(self, file: File) -> str:
        return self.datalake.get_file_name(file)

    def get_logger(self):
        """Returns the structured logger object.
        The input should be an object (eg. containing a message field, among others).

        ...     logger = context.get_logger()
        ...     logger.log({
        ...         "message": "Starting the main parser",
        ...         "level": "info"
        ...     })

        """
        return self.log

    def get_secret_config_value(self, secret_name: str, silent_on_error=True) -> str:
        """Returns the value of the secret.
        If secret is missing, empty string or throws error, depending on the second argument.
        """
        return get_secret_config_value(self._obj, secret_name, silent_on_error)

    def get_presigned_url(self, file: File, ttl_sec=300) -> str:
        return self.datalake.get_presigned_url(file, ttl_sec)

    def run_command(self, org_slug, target_id, action, metadata, payload, ttl_sec=300):
        return self.command.run_command(self._obj, org_slug, target_id, action, metadata, payload, ttl_sec)

def output_response(storage, response, correlation_id):
    storage.writeObject({**response, 'id': correlation_id})

def resolve_func(func_dir, func_slug):
    func_conf_file = os.path.join(func_dir, 'config.json')
    with open(func_conf_file, 'r') as file:
        func_conf = json.load(file)
    for f in func_conf['functions']:
        if (f['slug'] == func_slug):
            function = f['function']
            break
    else:
        raise Exception(f'function not found: {func_slug}')
    # print(function)
    func_module, _, func_name = function.rpartition('.')
    return func_module, func_name

def resolve_secrets_in_pipeline_config(context_from_arg):
    secrets = {}
    pipeline_config = context_from_arg.get('pipelineConfig')

    for key in pipeline_config:
      if key.startswith('ts_secret_name_'):
        secret_name = key.split("ts_secret_name_", 1)[1]
        secrets[secret_name] = get_secret_config_value(context_from_arg, key, True)

    return secrets

def get_secret_config_value(context_from_arg, secret_name, silent_on_error=True):
  pipeline_config = context_from_arg.get('pipelineConfig')

  if secret_name.startswith('ts_secret_name_'):
    secret_short_name = secret_name.split("ts_secret_name_", 1)[1]
    secret_full_key = secret_name
  else:
    secret_short_name = secret_name
    secret_full_key = 'ts_secret_name_' + secret_name

  if not secret_full_key in pipeline_config.keys() or pipeline_config.get(secret_full_key) is None:
    if silent_on_error:
      Context.log.log(f'Secret {secret_full_key} not found in the workflow config.')
      return ''
    else:
      raise Exception(f'Secret {secret_full_key} not found in the workflow config.')

  secret_ssm_name = pipeline_config.get(secret_full_key)

  k8s_secret_name_parts = secret_ssm_name.split('/')
  k8s_secret_name = k8s_secret_name_parts[len(k8s_secret_name_parts) - 1]

  try:
    if os.environ.get('TASK_SCRIPTS_CONTAINERS_MODE') == 'ecs':
      secret_value = os.environ.get('TS_SECRET_' + re.sub(r"[^a-z0-9]+", '_', secret_short_name, flags=re.IGNORECASE))
      if secret_value == None:
        raise Exception(f'Secret {secret_short_name} not found')
      return secret_value

    # legacy EKS: read from mounted volume
    secret_value_file = open(f'/etc/ts-secrets-volume/{k8s_secret_name}', 'r')
    secret_value = secret_value_file.read()
    secret_value_file.close()

    return secret_value
  except Exception as e:
    if silent_on_error:
      Context.log.log(e)
      return ''
    else:
      raise Exception(f'Could not resolve secret value for  {secret_full_key}') from e

def run(input, context_from_arg, func, correlation_id, func_dir,
        storage_type, storage_bucket, storage_file_key, storage_endpoint,
        artifact_bucket, artifact_prefix, artifact_endpoint, artifact_file_key,
        artifact_bucket_private, artifact_prefix_private, artifact_endpoint_private, command_endpoint,
        store_output=True):
    log = Log(context_from_arg)
    Context.log = log
    log.log({ 'level': 'debug', 'tag': LOG_TAG_SCRIPT_STARTED })
    if (storage_type != 's3file'):
        raise Exception(f'Invalid storage type: {storage_type}')

    context_from_arg['pipelineConfig'] = {
      **context_from_arg.get('pipelineConfig'),
      **resolve_secrets_in_pipeline_config(context_from_arg)
    }

    # override print function with our own, which decorates with workflow id and task id
    __builtins__['print'] = lambda *args, flush=False: log.log(*args)

    prefix = artifact_prefix if artifact_prefix else ''
    if not prefix and artifact_file_key:
        prefix = re.sub(r"ids/.*$", '', artifact_file_key)
    ids_util = create_ids_util([
        {
            'bucket': artifact_bucket,
            'prefix': prefix,
            'endpoint': artifact_endpoint,
            'namespacePattern': r"^(common|client-.*)$"
        },
        {
            'name': 'private',
            'bucket': artifact_bucket_private,
            'prefix': artifact_prefix_private if artifact_prefix_private else '',
            'endpoint': artifact_endpoint_private,
            'namespacePattern': r"^(private-.*)$"
        }
    ])
    storage = Storage(storage_bucket, storage_file_key, storage_endpoint)
    datalake = Datalake(storage_endpoint)
    command = Command(command_endpoint)
    context = Context(context_from_arg, datalake, ids_util, log, command)
    func_module, func_name = resolve_func(func_dir, func)
    try:
        log.log({ 'level': 'debug', 'tag': LOG_TAG_PRE_FUNCTION, 'funcName': f'{func_module}.{func_name}' })
        result = getattr(importlib.import_module(func_module), func_name)(input, context)
        log.log({ 'level': 'debug', 'tag': LOG_TAG_POST_FUNCTION, 'funcName': func_name })

        if store_output:
            output_response(storage, { 'type': COMPLETED, 'result': result }, correlation_id)

        taskResult = {
          'status': 'completed',
          'result': result or {}
        }
    except Exception as e:
        log.log(e)

        if store_output:
            output_response(storage, { 'type': FAILED, 'error': str(e) }, correlation_id)

        taskResult = {
          'status': 'failed',
          'result': {
            'error': str(e)
          }
        }
    log.log({ 'level': 'debug', 'tag': LOG_TAG_SCRIPT_ENDED })
    return taskResult
