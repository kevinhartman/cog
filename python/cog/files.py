import base64
import io
import mimetypes
import os
import typing as t

import requests


def upload_file(fh: io.IOBase, output_file_prefix: str = None) -> str:
    fh.seek(0)

    if output_file_prefix is not None:
        name = getattr(fh, "name", "output")
        url = output_file_prefix + os.path.basename(name)
        resp = requests.put(url, files={"file": fh})
        resp.raise_for_status()
        return url

    b = fh.read()
    # The file handle is strings, not bytes
    if isinstance(b, str):
        b = b.encode("utf-8")
    encoded_body = base64.b64encode(b)
    if getattr(fh, "name", None):
        # despite doing a getattr check here, mypy complains that io.IOBase has no attribute name
        mime_type = mimetypes.guess_type(fh.name)[0]  # type: ignore
    else:
        mime_type = "application/octet-stream"
    s = encoded_body.decode("utf-8")
    return f"data:{mime_type};base64,{s}"


def upload_output(fh: io.IOBase, output: t.Dict[str, t.Dict[str, t.Any]]) -> str:
    fh.seek(0)

    name = getattr(fh, "name", "output")

    # TODO: error if 'settings' not found
    settings = output[name]
    url = settings["url"]
    data = settings["data"]

    print("File upload:")
    print(url)
    print(data)

    resp = requests.put(url, data=data, files={"file": fh})
    resp.raise_for_status()
    return url


def guess_filename(obj: io.IOBase) -> str:
    """Tries to guess the filename of the given object."""
    name = getattr(obj, "name", "file")
    return os.path.basename(name)
