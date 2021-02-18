import io
import typing as t
import typing_extensions as te

FileCategory = te.Literal["IDS", "RAW", "PROCESSED", "TMP"]

class File(te.TypedDict, total=False):
    type: te.Literal["s3file"]
    bucket: str
    fileKey: str
    version: t.Optional[str]

class ReadResult(te.TypedDict):
    metadata: t.Mapping[str, str]
    body: t.Optional[bytes]
    file_obj: t.Optional[io.BufferedIOBase]
    download: t.Optional[str]
    custom_metadata: t.Mapping[str, str]
    custom_tags: t.List[str]
