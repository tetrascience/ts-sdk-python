import os
import argparse
import io

from ts_sdk.cli.__put_cmd import __ensure_args


def test_ensure_args():
    os.environ.update({'TS_ORG': 'env-org', 'TS_API_URL': 'env-api-url'})
    args = argparse.Namespace(
        org='arg-org',
        config=io.StringIO('{"org": "cfg-org", "auth_token": "cfg-token"}')
    )
    __ensure_args(args)
    assert args.api_url == 'env-api-url'
    assert args.org == 'arg-org'
    assert args.auth_token == 'cfg-token'
