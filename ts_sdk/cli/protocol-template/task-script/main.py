# The following imports are necessary for type-checking and editor integration.
from __future__ import annotations
import typing as t

if t.TYPE_CHECKING:
    import ts_sdk.task as ts
# End imports related to type-checking and editor integration.

import io
import json


def convert(input: t.BinaryIO) -> t.Any:
    """Given a file-like object "input", produce a JSON-serializable object
    (nested dictionary, array, etc) that will get dumped to the data lake as
    the output of this workflow.

    ADD YOUR BUSINESS LOGIC HERE.
    """
    return {"a": "1", "label": "label"}

def decorate(input_dict, label):
    input_dict['label'] = label
    return input_dict

def main(input, context: ts.Context):

    IDSNAMESPACE = "common"
    IDSTYPE = "example"
    IDSVERSION = "v1.0.0"

    username = input.get("username")
    passwordKey = input.get("passwordKey")
    password = context.get_secret_config_value(passwordKey)

    ## Add your logic
    file = context.read_file(input["input_file"])
    input_dict = json.loads(file["body"])
    
    decorate(input_dict, "label")
    
    convert(io.BytesIO(file["body"]))
    

    # Validate against IDS 
    context.validate_ids(
        input_dict, 
        IDSNAMESPACE, 
        IDSTYPE, 
        IDSVERSION
    )

    # write the IDS JSON to the data lake
    output = context.write_file(
        content=json.dumps(input_dict, indent=2, allow_nan=False),
        file_name="0.json",
        file_category="IDS",
        ids="{}/{}:{}".format(IDSNAMESPACE, IDSTYPE, IDSVERSION),
    )

    print(output)
    return output
