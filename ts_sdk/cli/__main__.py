import argparse

from .__put_cmd import put_cmd_args
from .__init_cmd import init_cmd_args

def main():
    parser = argparse.ArgumentParser(prog='ts-tool')
    subparsers = parser.add_subparsers()

    init_cmd_args(subparsers.add_parser(
        'init', 
        help='generate new project from a template'
        ))

    put_cmd_args(subparsers.add_parser(
        'put', 
        help='puts artifact identified by namespace/slug:version'
        ))

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    main()
