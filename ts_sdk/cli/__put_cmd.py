import json
import os
import io
import zipfile
import argparse
import re
from time import sleep, time

from .__api import upload_artifact, get_task_script_build_info, get_task_script_build_logs
from .__utils import sizeof_fmt, zipdir

def put_cmd_args(parser: argparse.ArgumentParser):
    parser.add_argument('type', type=str, choices=['ids', 'master-script', 'task-script'])
    parser.add_argument('namespace', type=str)
    parser.add_argument('slug', type=str)
    parser.add_argument('version', type=__version_type)
    parser.add_argument('folder', type=__folder_type, help='path to folder to be uploaded')
    parser.set_defaults(func=__cmd)

def __version_type(arg_value, pat=re.compile(r'^v')):
    if pat.match(arg_value):
        return arg_value
    return f'v{arg_value}'

def __folder_type(arg_value):
    if os.path.isdir(arg_value):
        return arg_value
    raise argparse.ArgumentTypeError('Not valid folder path provided!')

def __cmd(args):
    print('Compressing...', flush=True)
    zip_buffer = io.BytesIO()
    zipf = zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False)
    zipdir(args.folder, zipf)
    zipf.close()
    zip_bytes = zip_buffer.getvalue()

    print(f'Uploading {sizeof_fmt(len(zip_bytes))}...', flush=True)
    r = upload_artifact(args, zip_bytes)

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
            build_info = get_task_script_build_info(build_id)
            build_complete = build_info.get('build', {}).get('buildComplete')
            build_status = build_info.get('build', {}).get('buildStatus')

            sleep(3)

            logs_resp = get_task_script_build_logs(
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
