import json
import os
import io
import zipfile
import argparse
import re
from time import sleep, time

from .__api import upload_artifact, get_task_script_build_info, get_task_script_build_logs
from .__utils import sizeof_fmt, zipdir

def init_cmd_args(parser: argparse.ArgumentParser):
    parser.set_defaults(func=__cmd)

def __cmd(args):
    raise Exception('Not implemented yet!')