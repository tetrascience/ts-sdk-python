import json
import os
import sys
import re
import time
import traceback
import requests
from datetime import datetime

__type_to_url = {
  'ids': 'ids',
  'master-script': 'master-scripts',
  'protocol': 'master-scripts',
  'task-script': 'task-scripts'
}

__ignore_ssl = False

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

def set_ignore_ssl(v: bool):
    global __ignore_ssl
    __ignore_ssl = v

def upload_artifact(cfg, artifact_bytes):
    url = f'{__get_env("TS_API_URL")}/artifact/{__type_to_url[cfg.type]}/{cfg.namespace}/{cfg.slug}/{cfg.version}'
    r = requests.post(
        url, 
        headers=__get_headers(),
        params={'force': 'true'} if cfg.force else {},
        data=artifact_bytes,
        verify=not __ignore_ssl
    )
    if r.status_code < 400:
        return r.json()
    else:
        print(r.json(), file=sys.stderr, flush=True)
        raise Exception(f'HTTP status: {r.status_code}, url: {r.url}')

def get_task_script_build_info(id: str):
    url = f'{__get_env("TS_API_URL")}/artifact/builds/{id}'
    r = requests.get(
        url, 
        headers=__get_headers(),
        verify=not __ignore_ssl
    )
    if r.status_code < 400:
        return r.json()
    else:
        print(r.json(), file=sys.stderr, flush=True)
        raise Exception(f'HTTP status: {r.status_code}, url: {r.url}')

def get_task_script_build_logs(id: str, params):
    url = f'{__get_env("TS_API_URL")}/artifact/build-logs/{id}'
    r = requests.get(
        url, 
        headers=__get_headers(),
        params={k:v for k,v in params.items() if v is not None},
        verify=not __ignore_ssl
        )
    if r.status_code < 400:
        return r.json()
    else:
        print(r.json(), file=sys.stderr, flush=True)
        raise Exception(f'HTTP status: {r.status_code}, url: {r.url}')