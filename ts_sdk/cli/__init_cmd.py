from argparse import ArgumentParser
from pathlib import Path
import os
import shutil

def init_cmd_args(parser: ArgumentParser):
    parser.add_argument(
        "--master_script_slug", "-m", type=str, required=True, help="Slug of the master script"
    )
    parser.add_argument(
        "--task_script_slug", "-t", type=str, required=True, help="Slug of the task script"
    )
    parser.add_argument(
        "--folder_path", "-f", type=str, required=True, help="Destination folder"
    )
    parser.add_argument(
        "--remove", "-r", action='store_true', help="Force removal/overwrite if folder already exists"
    )
    parser.add_argument(
        "--org", "-o", type=str, required=True, help="Org into which the scripts will be uploaded"
    )
    parser.add_argument(
        "--preserve_templates",
        type=bool,
        default=False,
        help="If true, leave template files on disk instead of deleting them",
    )
    parser.set_defaults(func=__cmd)

def __cmd(args):
    # Remove folder if it exists
    new_folder_path = os.path.abspath(args.folder_path)
    new_folder = Path(new_folder_path)
    if new_folder.exists():
        print(f'{new_folder_path} already exists')
        if args.remove:
            shutil.rmtree(new_folder_path)
            print(f'{new_folder_path} removed')
        else:
            print(f'{new_folder_path} exists, do nothing. You can use --remove to remove/overwrite')
            return
    tpl_path = os.path.join(os.path.dirname(__file__), 'protocol-template')
    shutil.copytree(tpl_path, new_folder_path)
    for p in Path(new_folder_path).glob("**/*.template"):
        text = p.read_text()
        text = text.replace("{{ org }}", args.org)
        text = text.replace("{{ master_script_slug }}", args.master_script_slug)
        text = text.replace("{{ task_script_slug }}", args.task_script_slug)

        dest = p.with_name(p.stem)
        print(f'Generating {dest}')
        dest.write_text(text)

        if not args.preserve_templates:
            print(f'Deleting {p}')
            p.unlink()
