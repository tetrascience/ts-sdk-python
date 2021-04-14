import json
import os
import sys
from main import main
from ts_sdk.taskdev import Context, load_test_file, check_test_output


def test_basic(shared_datadir):
    # set up my for local integration context
    context = Context()
    test_input_file = load_test_file(
        context, shared_datadir / "input.json", "/input.json", file_category="RAW"
    )
    test_input = {
        'input_file': test_input_file,
        'username': 'username',
        'password': 'secret'
    }

    # do the conversion
    actual_output = main(test_input, context)

    # do the check
    check_test_output(
        context, shared_datadir / "expected.json", actual_output, json.loads
    )
