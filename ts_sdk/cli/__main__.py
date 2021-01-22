import argparse
import re

from __put_cmd import put_cmd

def version_type(arg_value, pat=re.compile(r'^v')):
    if pat.match(arg_value):
        return f'{arg_value}'
    return f'v{arg_value}'


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('cmd', type=str, choices=['put'])
    parser.add_argument('type', type=str, choices=['ids', 'master-script', 'task-script'])
    parser.add_argument('namespace', type=str)
    parser.add_argument('slug', type=str)
    parser.add_argument('version', type=version_type)
    parser.add_argument('folder', type=str, help='path to uploaded artifact')
    args = parser.parse_args()

    if args.cmd == 'put':
        put_cmd(args)
    else:
        raise Exception(f'Unsupported command {args.cmd}')
