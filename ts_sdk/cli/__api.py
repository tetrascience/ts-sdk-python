import json
import os
import re
import time
import traceback
import requests
from datetime import datetime

type_to_url = {
  'ids': 'ids',
  'master-script': 'master-scripts',
  'task-script': 'task-scripts'
}

def __get_env(name: str):
    v = os.environ.get(name)
    if not v:
        raise Exception(f'{name} env is not set!')
    return v

def __get_headers():
    headers = {'x-org-slug': __get_env('TS_ORG')}
    ts_auth = __get_env('TS_AUTH_TOKEN')
    if re.compile(r'^([a-z0-9]+-)+[a-z0-9]+$').match(ts_auth, re.IGNORECASE):
        headers['x-api-key'] = ts_auth
    else:
        headers['ts-auth-token'] = ts_auth
    return headers

def upload_artifact(cfg, artifact_bytes):
    url = f'{__get_env("TS_API_URL")}/artifact/{type_to_url[cfg.type]}/{cfg.namespace}/{cfg.slug}/{cfg.version}'
    r = requests.post(
        url, 
        headers=__get_headers(),
        data=artifact_bytes)
    if r.status_code < 400:
        return r.json()
    else:
        raise Exception(f'Code: {r.status_code}, url: {url}')

def get_task_script_build_info(id: str):
    url = f'{__get_env("TS_API_URL")}/artifact/builds/{id}'
    r = requests.get(
        url, 
        headers=__get_headers())
    if r.status_code < 400:
        return r.json()
    else:
        raise Exception(f'Code: {r.status_code}, url: {url}')

def get_task_script_build_logs(id: str, params):
    url = f'{__get_env("TS_API_URL")}/artifact/build-logs/{id}'
    r = requests.get(
        url, 
        headers=__get_headers(),
        params={k:v for k,v in params.items() if v is not None}
        )
    if r.status_code < 400:
        return r.json()
    else:
        raise Exception(f'Code: {r.status_code}, url: {url}')