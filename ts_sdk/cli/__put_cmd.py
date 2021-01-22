import json
import os
import io
import zipfile
from time import sleep, time

from .__api import upload_artifact, get_task_script_build_info, get_task_script_build_logs
from .__utils import sizeof_fmt, zipdir


def put_cmd(args):
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

        print('')

        if last_status == 'FAILED':
            raise Exception('Build failed.')
