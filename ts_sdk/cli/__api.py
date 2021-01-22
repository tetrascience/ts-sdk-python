import json
import os
import ssl
import time
import traceback
import requests
from datetime import datetime

def ensure_env(name: str):
    v = os.environ.get(name)
    if not v:
        raise Exception(f'{name} env is not set!')
    return v

TS_AUTH = ensure_env('TS_AUTH')
TS_ORG = ensure_env('TS_ORG')
TS_API_URL = ensure_env('TS_API_URL')

type_to_url = {
  'ids': 'ids',
  'master-script': 'master-scripts',
  'task-script': 'task-scripts'
}

def get_headers():
    return {'ts-auth-token': TS_AUTH, 'x-org-slug': TS_ORG}

def upload_artifact(cfg, artifact_bytes):
    url = f'{TS_API_URL}/artifact/{type_to_url[cfg.type]}/{cfg.namespace}/{cfg.slug}/{cfg.version}'
    r = requests.post(
        url, 
        headers=get_headers(),
        data=artifact_bytes)
    if r.status_code < 400:
        return r.json()
    else:
        raise Exception(f'Code: {r.status_code}, url: {url}')

def get_task_script_build_info(id: str):
    url = f'{TS_API_URL}/artifact/builds/{id}'
    r = requests.get(
        url, 
        headers=get_headers())
    if r.status_code < 400:
        return r.json()
    else:
        raise Exception(f'Code: {r.status_code}, url: {url}')

def get_task_script_build_logs(id: str, params):
    url = f'{TS_API_URL}/artifact/build-logs/{id}'
    r = requests.get(
        url, 
        headers=get_headers(),
        params={k:v for k,v in params.items() if v is not None}
        )
    if r.status_code < 400:
        return r.json()
    else:
        raise Exception(f'Code: {r.status_code}, url: {url}')