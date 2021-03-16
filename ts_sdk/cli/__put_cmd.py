import json
import os
import io
import zipfile
import argparse
import re
from time import sleep, time

from .__api import TsApi
from .__utils import sizeof_fmt, zipdir

def put_cmd_args(parser: argparse.ArgumentParser):
    parser.add_argument('type', type=str, choices=['ids', 'protocol', 'master-script', 'task-script'], help='artifact type')
    parser.add_argument('namespace', type=str)
    parser.add_argument('slug', type=str)
    parser.add_argument('version', type=__version_type)
    parser.add_argument('folder', type=__folder_type, help='path to folder to be uploaded')
    parser.add_argument(
        '--force', '-f', action='store_true', help='force overwrite of an existing artifact'
    )
    parser.add_argument(
        '--ignore-ssl', '-i', action='store_true', help='ignore the SSL certificate verification'
    )
    
    parser.add_argument('--org', help='org slug', type=str)
    parser.add_argument('--api-url', help='platform API URL', type=str)
    parser.add_argument('--auth-token', help='authorization token', type=str)
    
    parser.add_argument(
        '--config', '-c', help='JSON file with configuration', type=argparse.FileType('r')
    )
    
    parser.set_defaults(func=__cmd)

def __version_type(arg_value, pat=re.compile(r'^v')):
    if pat.match(arg_value):
        return arg_value
    return f'v{arg_value}'

def __folder_type(arg_value):
    if os.path.isdir(arg_value):
        return arg_value
    raise argparse.ArgumentTypeError('Not valid folder path provided!')

def __ensure_args(args: argparse.Namespace):
    # from env
    env_prefix = 'TS_'
    for k, v in os.environ.items():
        if k.startswith(env_prefix):
            arg_key = k.replace(env_prefix, '').lower()
            if getattr(args, arg_key, None) is None:
                setattr(args, arg_key, v)

    # from config
    if args.config:
        parsed_config = json.load(args.config)
        for k, v in parsed_config.items():
            if getattr(args, k, None) is None:
                setattr(args, k, v)


def __cmd(args):
    __ensure_args(args)
    print('Config:')
    keys_to_show = ['api_url', 'org', 'auth_token', 'ignore_ssl']
    config_to_show = { key_to_show: args.__dict__[key_to_show] for key_to_show in keys_to_show }
    if isinstance(config_to_show.get('auth_token'), str):
        config_to_show.update({'auth_token': f'{config_to_show["auth_token"][0:7]}...'})
    print(json.dumps(config_to_show, indent=4, sort_keys=True))

    ts_api = TsApi(**args.__dict__)

    print('Compressing...', flush=True)
    zip_buffer = io.BytesIO()
    zipf = zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False)
    zipdir(args.folder, zipf)
    zipf.close()
    zip_bytes = zip_buffer.getvalue()

    print(f'Uploading {sizeof_fmt(len(zip_bytes))}...', flush=True)

    r = ts_api.upload_artifact(args, zip_bytes)

    print(json.dumps(r, indent=4, sort_keys=True), flush=True)

    if args.type == 'task-script':
        build_id = r.get('build', {}).get('id', None)

        if not build_id: 
            raise Exception('No build ID found in upload response!')

        print('Build started', flush=True)
        print("Note: A local script interruption doesn't stop a remote build!", flush=True)

        last_status = None
        prev_next_token = ''

        while True:
            build_info = ts_api.get_task_script_build_info(build_id)
            build_complete = build_info.get('build', {}).get('buildComplete')
            build_status = build_info.get('build', {}).get('buildStatus')

            sleep(3)

            logs_resp = ts_api.get_task_script_build_logs(
                build_id,
                {'nextToken': prev_next_token}
            )
            prev_next_token = logs_resp.get('nextToken', None)
            events = logs_resp.get('events', [])

            if len(events) > 0:
                print('\r', end='', flush=True)
            elif not build_complete:
                print('.', end='', flush=True)

            for event in events:
                msg_text = event.get('message', '').strip()
                if msg_text:
                    print(msg_text, flush=True)

            if build_complete:
                last_status = build_status
                break

        print('', flush=True)

        if last_status == 'FAILED':
            raise Exception('Build failed.')
