import json
import sys
import re
import time
import traceback
import requests
from datetime import datetime

from .__utils import tcolors


def validate_dict_key(d, k):
    if d.get(k) is None:
        print(f'{tcolors.FAIL}{k} is not set!{tcolors.ENDC}', file=sys.stderr, flush=True)
        return False
    return True

class TsApi:

    def __init__(self, **kwargs):
        res = validate_dict_key(kwargs, 'org')
        res &= validate_dict_key(kwargs, 'api_url')
        res &= validate_dict_key(kwargs, 'auth_token')
        if not res:
            sys.exit(1)
        self.opts = kwargs

    @property
    def __api_url(self):
        return self.opts.get('api_url')

    @property
    def __request_defaults(self):
        return {
            'verify': self.opts.get('ignore_ssl') != True,
            'headers': self.__get_headers()
        }

    def __get_headers(self):
        headers = {'x-org-slug': self.opts.get('org')}
        ts_auth = self.opts.get('auth_token')
        if re.compile(r'^([a-z0-9]+-)+[a-z0-9]+$').match(ts_auth, re.IGNORECASE):
            headers['x-api-key'] = ts_auth
        else:
            headers['ts-auth-token'] = ts_auth
        return headers

    def upload_artifact(self, cfg, artifact_bytes):
        type_to_url = {
            'ids': 'ids',
            'master-script': 'master-scripts',
            'protocol': 'master-scripts',
            'task-script': 'task-scripts'
        }
        url = f'{self.__api_url}/artifact/{type_to_url[cfg.type]}/{cfg.namespace}/{cfg.slug}/{cfg.version}'
        r = requests.post(
            url,
            **self.__request_defaults,
            params={'force': 'true'} if cfg.force else {},
            data=artifact_bytes
        )
        if r.status_code < 400:
            return r.json()
        else:
            print(r.json(), file=sys.stderr, flush=True)
            raise Exception(f'HTTP status: {r.status_code}, url: {r.url}')

    def get_task_script_build_info(self, id: str):
        url = f'{self.__api_url}/artifact/builds/{id}'
        r = requests.get(
            url,
            **self.__request_defaults
        )
        if r.status_code < 400:
            return r.json()
        else:
            print(r.json(), file=sys.stderr, flush=True)
            raise Exception(f'HTTP status: {r.status_code}, url: {r.url}')

    def get_task_script_build_logs(self, id: str, params):
        url = f'{self.__api_url}/artifact/build-logs/{id}'
        r = requests.get(
            url,
            **self.__request_defaults,
            params={k:v for k,v in params.items() if v is not None}
        )
        if r.status_code < 400:
            return r.json()
        else:
            print(r.json(), file=sys.stderr, flush=True)
            raise Exception(f'HTTP status: {r.status_code}, url: {r.url}')
