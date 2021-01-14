import os
import sys
import json
import base64
import traceback
import datetime
from collections.abc import Mapping

timestamp_key = "timestamp"
org_slug_key = "orgSlug"
message_key = "message"
file_id_key = "fileId"
master_script_key = "masterScript"
task_script_key = "taskScript"
trace_id_key = "traceId"
container_id_key = "containerId"
level_key = "level"
error_type_key = "errorType"
exception_key = "exception"

class Log:
    def __init__(self, context):
        self._context = context
    
    def log(self, *args):        
        for arg in args:
          try:
            # Perform actual logging, that will be transported to Cloudwatch.
            __builtins__['default_print'](json.dumps(self.create_json_log_entry(arg)))
          except:
            __builtins__['default_print'](arg)
    
    def create_json_log_entry(self, input):
        log_entry = self.generate_default()

        if isinstance(input, str):
            log_entry = {**log_entry, message_key: input, level_key: 'info'}
        elif isinstance(input, Exception):
            log_entry = {**log_entry, **self.generate_error(input)}
        elif isinstance(input, Mapping):
            log_entry = {**log_entry, **input}
        else:
            log_entry = {**log_entry, message_key: input, level_key: 'info'}
        
        if not level_key in log_entry:
            log_entry[level_key] = "info"

        return log_entry

    def generate_default(self):
        try:
            # Lets add only the timestamp right now and add the rest as K8s labels
            
            # master_script_namespace = self._context["masterScriptNamespace"]
            # master_script_slug = self._context["masterScriptSlug"]
            # master_script_version = self._context["masterScriptVersion"]
            # master_script = f"{master_script_namespace}/{master_script_slug}:{master_script_version}"
            
            default_log = {
                timestamp_key: datetime.datetime.now().isoformat(),
                # org_slug_key: self._context["orgSlug"],
                # file_id_key: self._context["inputFile"]["meta"]["fileId"],
                # master_script_key: master_script,
                # task_script_key: self._context["taskScript"]
            }

            if 'CONTAINER_ID' in os.environ:
                default_log[container_id_key] = os.environ.get('CONTAINER_ID')

            if 'traceId' in self._context.get('inputFile', {}).get('meta', {}):
                default_log[trace_id_key] = self._context["inputFile"]["meta"]["traceId"]

            if 'taskId' in self._context:
                default_log['taskId'] = self._context.get('taskId')

            if 'workflowId' in self._context:
                default_log['workflowId'] = self._context.get('workflowId')
        except (AttributeError, KeyError) as e:
            __builtins__['default_print']("Error in default log")
            __builtins__['default_print'](e)
            default_log =  {}

        return default_log
    
    def generate_error(self, err):
        tb_lines = traceback.format_exception(err.__class__, err, err.__traceback__)
        tb_text = ''.join(tb_lines)
        error = { level_key: "error", error_type_key: str(type(err)), exception_key: tb_text }
        if hasattr(err, 'message'):
            error[message_key] = err.message
        else:
            error[message_key] = str(err)
        
        return error
