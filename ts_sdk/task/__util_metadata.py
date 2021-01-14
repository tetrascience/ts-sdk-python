# These should be kept in sync with S3MetadataFields.js in ts-lib-shared-schema
FIELDS = {
    'VERSION': 'ts_version',
    'INTEGRATION_TYPE': 'ts_integration_type',
    'INTEGRATION_NAME': 'ts_integration_name',
    'INTEGRATION_ID': 'ts_integration_id', # TODO new?

    'FILE_ID': 'ts_file_id',
    'FILE_TYPE': 'ts_processed_file_type',
    'FILE_PATH': 'ts_file_path', # how to specify this?
    'FILE_NAME': 'ts_file_name',

    'SOURCE_TYPE': 'ts_source_type',
    'SOURCE_NAME': 'ts_source_name',

    'RAW_FILE_ID': 'ts_source_file_id',
    'RAW_FILE_VERSION': 'ts_raw_file_version',

    'IDS': 'ts_ids',
    'IDS_NAMESPACE': 'ts_ids_namespace',
    'IDS_TYPE': 'ts_ids_type',
    'IDS_VERSION': 'ts_ids_type_version',

    'CUSTOM_METADATA': 'ts_integration_metadata',
    'CUSTOM_TAGS': 'ts_integration_tags',

    'PIPELINE_ID': 'ts_pipeline_id',
    'PIPELINE_MASTER_SCRIPT': 'ts_master_script',
    'PIPELINE_TASK_SCRIPT': 'ts_task_script',
    'PIPELINE_TASK_SLUG': 'ts_task_slug',
    'PIPELINE_TASK_EXECUTION_ID': 'ts_task_execution_id',
    'PIPELINE_WORKFLOW_ID': 'ts_workflow_id',

    'TRACE_ID': 'ts_trace_id'
}
