import os
import sys
from threading import Timer
import traceback
from datetime import datetime, timedelta
from time import sleep, time

from .__task_script_runner import run
from .__util_log import Log
from .__util_thread import ThreadWithTrace
from .__util_task import (extend_task_timeout, poll_task, update_task_status)


def get_run_params(task):
  params = {
    'input': task.get('input'),
    'context_from_arg': task.get('context'),
    'func': task.get('func'),
    'correlation_id': task.get('correlation_id'),
    'func_dir': task.get('func_dir'),
    'store_output': False,
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

  return params

log = Log({})

last_run = {'result': None, 'error': None}
run_state = {'task_worker': None, 'task': None}

def healtcheck_worker():
  task = run_state['task']
  task_worker = run_state['task_worker']

  if task and task_worker:
    task_id = task.get('id')
    try:
      extend_task_timeout(task)
    except Exception as e:
      log.log(f'Error during timeout extension -> killing task {task_id}')
      task_worker.kill()

  Timer(60.0, healtcheck_worker).start()


def task_worker(task):
  run_params = get_run_params(task)
  sys.path.append(run_params.get('func_dir'))
  try:
    last_run['result'] = run(**run_params)
  except Exception as e:
    log.log(log.generate_error(e))
    last_run['error'] = traceback.format_exc()
  sys.path.remove(run_params.get('func_dir'))


if __name__ == '__main__':
  healtcheck_worker()
  
  while True:
    task = poll_task()
    if task:
      task_id = task.get('id')
      log.log(f'Got new task {task_id}')

      last_run['result'] = None
      last_run['error'] = None

      run_state['task'] = task
      task_thread = ThreadWithTrace(name=f'task-{task_id}', target=task_worker, args=(task,))
      run_state['task_worker'] = task_thread
      task_thread.start()
      task_thread.join()

      log.log(f'Task {task_id} thread is completed')

      run_state['task_worker'] = None
      run_state['task'] = None

      if last_run['result'] != None:
        update_task_status(task, last_run['result'])
      else:
        update_task_status(task, {
          'status': 'failed',
          'result': {
            'error': last_run['error'] if last_run['error'] else 'No content returned by worker'
          }
        })
