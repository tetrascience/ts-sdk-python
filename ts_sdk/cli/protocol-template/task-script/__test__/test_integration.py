import os
import sys
import json
from ts_sdk.taskdev import Context, load_test_input, check_test_output

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from main import main


def test_basic(shared_datadir):
    # set up my for local integration context
    context = Context({ 'mosaic_password': 'secret' })
    test_input_file = load_test_input(
        context, shared_datadir / "input.json", "/input.json", file_category="RAW"
    )
    test_input = {
        'input_file': test_input_file,
        'username': 'username',
        'passwordKey': 'mosaic_password'
    }

    # do the conversion
    actual_output = main(test_input, context)

    # do the check
    check_test_output(
        context, shared_datadir / "expected.json", actual_output, json.loads
    )
