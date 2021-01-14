import os
import json
import time
import urllib.request
import urllib.parse
import urllib.error
import ssl
import traceback

from datetime import datetime

url = os.environ.get('ORCHESTRATOR_ENDPOINT')
platform_props_hash = os.environ.get('PLATFORM_PROPS_HASH')
task_group_hash = os.environ.get('TASK_GROUP_HASH')
container_id = os.environ.get('CONTAINER_ID')

def poll_task():
  try:
    data = json.dumps({
      'platformPropsHash' : platform_props_hash,
      'taskGroupHash' : task_group_hash,
      'containerId' : container_id
    }).encode('utf8')
    poll_url = url + '/task/poll'
    req = urllib.request.Request(poll_url, data, headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req, context=ssl._create_unverified_context())
    return generate_task_from_reponse(json.load(response))
  except urllib.error.HTTPError as e:
      print(f'HTTPError: {e.code} for {poll_url}')
  except urllib.error.URLError as e:
      print(f'URLError: {e.code} for {poll_url}')
  except Exception as e:
      print(traceback.format_exc())

def update_task_status(task, result):
  try: 
    data = json.dumps(result).encode('utf8')
    task_id = task.get('id')
    update_url = url + f'/task/{task_id}/update-status'
    req = urllib.request.Request(update_url, data, headers={'content-type': 'application/json'})
    urllib.request.urlopen(req, context=ssl._create_unverified_context())
  except urllib.error.HTTPError as e:
      print(f'HTTPError: {e.code} for {update_url}')
  except urllib.error.URLError as e:
      print(f'URLError: {e.code} for {update_url}')
  except Exception as e:
      print(traceback.format_exc())

def generate_task_from_reponse(body):
  if body:
    data = body.get('data')
    return {
      'id': body.get('id'),
      'context': data.get('context', {}) or {},
      'input': data.get('input', {}) or {},
      'secrets': data.get('secrets', {}) or {},
      'func': data.get('func'),
      'workflow_id': data.get('workflowId'),
      'correlation_id': body.get('correlationId') or body.get('id'),
      'func_dir': data.get('funcDir', './func') or './func'
    }
  
  return {}

def extend_task_timeout(task):
  try:
    task_id = task.get('id')
    extend_timeout_url = url + f'/task/{task_id}/extend-timeout'
    req = urllib.request.Request(extend_timeout_url, {}, headers={'content-type': 'application/json'})
    urllib.request.urlopen(req, context=ssl._create_unverified_context())
    print("EXTENDING: " + task.get('id'))
  except urllib.error.HTTPError as e:
      print(f'HTTPError: {e.code} for {extend_timeout_url}')
      if e.code == 409:
        raise
  except urllib.error.URLError as e:
      print(f'URLError: {e.code} for {extend_timeout_url}')
  except Exception as e:
      print(traceback.format_exc())
