from argparse import ArgumentParser

from .__put_cmd import put_cmd_args
from .__init_cmd import init_cmd_args

def main():
    parser = ArgumentParser(prog='ts-sdk')
    subparsers = parser.add_subparsers()

    init_cmd_args(subparsers.add_parser(
        'init', 
        help='initialize master and task script from a template'
        ))

    put_cmd_args(subparsers.add_parser(
        'put', 
        help='puts artifact identified by namespace/slug:version'
        ))

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
