import os
import json
import time
import traceback
from datetime import datetime
from requests import request
from requests.exceptions import RequestException


url = os.environ.get('ORCHESTRATOR_ENDPOINT')
platform_props_hash = os.environ.get('PLATFORM_PROPS_HASH')
task_group_hash = os.environ.get('TASK_GROUP_HASH')
container_id = os.environ.get('CONTAINER_ID')

class ContainerStoppedException(Exception): ...
class TaskUpdateConflictException(Exception): ...

def poll_task():
  try:
    poll_url = url + '/task/poll'
    response = request(
      'POST', 
      poll_url,
      json={
        'platformPropsHash' : platform_props_hash,
        'taskGroupHash' : task_group_hash,
        'containerId' : container_id
      },
      verify=False
    )
    if response.status_code >= 400:
      message = f'Got {response.status_code} for {poll_url}'
      print({ 'level': 'error', 'message': message })
      if response.status_code == 409:
        raise ContainerStoppedException(message)
      time.sleep(2)
      return None
    return generate_task_from_reponse(response.json())
  except RequestException:
      print({ 'level': 'error', 'message': traceback.format_exc() })

def update_task_status(task, result):
  try:
    task_id = task.get('id')
    update_url = url + f'/task/{task_id}/update-status'
    response = request(
      'POST', 
      update_url,
      json=result,
      verify=False
    )
    if response.status_code >= 400:
      message = f'Got {response.status_code} for {update_url}'
      print({ 'level': 'error', 'message': message })
  except RequestException:
      print({ 'level': 'error', 'message': traceback.format_exc() })

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

    response = request(
      'POST', 
      extend_timeout_url,
      json={},
      verify=False
    )
    if response.status_code >= 400:
      message = f'Got {response.status_code} for {extend_timeout_url}'
      print({ 'level': 'error', 'message': message })
      if response.status_code == 409:
        raise TaskUpdateConflictException(message)
    print({ 'level': 'debug', 'message': f'EXTENDING: {task_id}' })
  except RequestException:
      print({ 'level': 'error', 'message': traceback.format_exc() })
