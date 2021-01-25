import io
import tempfile
import typing as t
import typing_extensions as te


FileCategory = te.Literal["IDS", "RAW", "PROCESSED"]
JSONType = t.Union[
    str, int, float, bool, None, t.List["JSONType"], t.Dict[str, "JSONType"]
]


class File(te.TypedDict, total=False):
    type: te.Literal["s3"]
    bucket: str
    fileKey: str
    version: t.Optional[str]


class Result(te.TypedDict):
    metadata: t.Dict[str, str]
    body: bytes
    custom_metadata: t.Dict[str, str]
    custom_tags: t.List[str]


class Context:
    """A development-time version of the context object that is passed into
    the task script handler when running as part of a pipeline.
    """

    def __init__(self, pipeline_config = {}):
        self._storage = {}
        self._pipeline_config = pipeline_config

    @property
    def pipeline_config(self) -> t.Dict[str, str]:
        """Pipeline configuration including secrets."""
        return self._pipeline_config

    def read_file(self, file: File, form: str = 'body') -> Result:
        if form == 'body':
            return self._storage[file["fileKey"]]
        elif form == 'file_obj':
            result = self._storage[file["fileKey"]]
            body = result['body']
            buf = io.BytesIO()
            buf.write(body)
            buf.seek(0)
            result['file_obj'] = buf
            return result
        elif form == 'download':
            result = self._storage[file["fileKey"]]
            with tempfile.NamedTemporaryFile(mode='wb', delete=False) as tf:
                tf.write(result['body'])
                result['download'] = tf.name
            return result
        raise Exception(f'Invalid form: {form}')

    def write_file(
        self,
        content: t.AnyStr,
        file_name: str,
        file_category: FileCategory,
        ids: str = None,
        custom_metadata: t.Dict[str, str] = None,
        custom_tags: t.List[str] = None,
        source_type: str = None,
    ) -> File:
        if type(content) == str:
            content = content.encode('UTF-8')
        self._storage[file_name] = {
            "metadata": {
                "TS_IDS": ids,
                "TS_SOURCE_TYPE": source_type,
                "TS_FILE_CATEGORY": file_category,
            },
            "body": content,
            "custom_metadata": custom_metadata,
            "custom_tags": custom_tags,
        }
        return {
            "type": "s3",
            "bucket": "fake-unittest-bucket",
            "fileKey": file_name,
        }

    # always return true in local context
    def validate_ids(
        self,
        data: dict,
        namespace: str,
        slug: str,
        version: str
    ) -> bool:
        return True

    def get_secret_config_value(self, key):
        return self._pipeline_config[key]
