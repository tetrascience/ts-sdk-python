from .context import Context, File
import typing as t
import os


def load_pipeline_config(context: Context, config: t.Dict[str, str]):
    """Load config into this context's pipeline config."""
    context._pipeline_config = config


def load_test_input(
    context: Context, local_path: os.PathLike, datalake_path: str, **kwargs
) -> File:
    """Load a local file into the testing data lake, for use in an
    integration test.

    >>> load_test_input(ctx, base_dir / 'setup.py', '/setup.py', file_category='RAW')
    {'type': 's3', 'bucket': 'fake-unittest-bucket', 'fileKey': '/setup.py'}
    """
    with open(local_path) as f:
        return context.write_file(f.read(), datalake_path, **kwargs)


def check_test_output(
    context: Context,
    local_path: os.PathLike,
    datalake_file: File,
    transform: t.Callable[[bytes], t.Any] = None,
):
    """Assert that a file in the testing data lake matches the contents of a
    local file. Optionally transforms the file contents before comparing
    (for example, to ignore whitespace and text ordering for JSON files).

    >>> check_test_output(ctx, base_dir / 'expected.json', output_file, json.loads)
    """
    with open(local_path, "rb") as f:
        expected = f.read()
    actual = context.read_file(datalake_file)["body"]
    if transform is not None:
        expected = transform(expected)
        actual = transform(actual)
    assert expected == actual
