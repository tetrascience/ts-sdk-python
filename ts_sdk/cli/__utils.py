import os
from pathlib import Path
import time
import zipfile
import requests
import xml.etree.ElementTree as ET
from colorama import Fore


def get_latest_version():
    try:
        r = requests.get('https://pypi.org/rss/project/ts-sdk/releases.xml', timeout=5)
        root = ET.fromstring(r.content)
        return root.findall('channel/item/title')[0].text
    except:
        return '0.0.0'

def check_update_required(current_version):
    try:
        latest_version_path = Path.home() / '.ts-sdk.latest'
        latest_version = '0.0.0'

        # refresh saved latest version once per day
        if latest_version_path.is_file() and time.time() - latest_version_path.stat().st_mtime < 24 * 3600:
            latest_version = latest_version_path.read_text()
        else:
            latest_version = get_latest_version()
            latest_version_path.write_text(latest_version)

        if latest_version and check_versions_for_update(current_version, latest_version):
            print(f'\n{Fore.YELLOW}Please upgrade ts-sdk (local: {current_version}, latest: {latest_version}){Fore.RESET}')
            print(f'{Fore.YELLOW}Use: pip3 install ts-sdk --upgrade{Fore.RESET}\n')

    except Exception as ex:
        # print(ex)
        pass

def check_versions_for_update(current: str, latest: str):
    current_major, current_minor, *rest = current.split('.')
    latest_major, latest_minor, *rest = latest.split('.')
    if int(current_major) < int(latest_major):
        return True
    if int(current_minor) < int(latest_minor):
        return True
    return False

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)

def zipdir(path: str, z: zipfile.ZipFile):
    for root, dirs, files in os.walk(path):
        for file in files:
            local_path = os.path.join(root, file)
            zip_path = os.path.relpath(os.path.join(root, file), os.path.join(path))
            z.write(local_path, zip_path)
