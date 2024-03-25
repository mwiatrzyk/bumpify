import io
import json
import typing

import tomlkit

from .interface import IFileSystemReader, IFileSystemWriter


def read_json(fs: IFileSystemReader, path: str, encoding: str = "utf-8") -> dict:
    """Read and decode a JSON file.

    :param fs:
        Filesystem reader to use.

    :param path:
        Path to a JSON file.

    :param encoding:
        Encoding to be used when file is decoded.
    """
    payload = fs.read(path).decode(encoding)
    return json.loads(payload)


def read_toml(fs: IFileSystemReader, path: str) -> tomlkit.TOMLDocument:
    """Read TOML file.

    :param fs:
        Filesystem reader instance.

    :param path:
        Path to a TOML file.
    """
    data = fs.read(path)
    data = tomlkit.loads(data)
    return data


def write_toml(
    fs: IFileSystemWriter,
    path: str,
    data: typing.Union[dict, tomlkit.TOMLDocument],
    encoding: str = "utf-8",
):
    """Write TOML file.

    :param fs:
        Filesystem writer instance.

    :param path:
        Path to a TOML file to be created or modified.

    :param data:
        TOML data to be written.

    :param encoding:
        Encoding to be used to encode resulting TOML file.

        By default, UTF-8 is used.
    """
    payload = tomlkit.dumps(data)
    payload = payload.encode(encoding)
    fs.write(path, payload)


def iter_lines(
    fs_api: IFileSystemReader, path: str, encoding: str = "utf-8"
) -> typing.Iterator[str]:
    """Helper function that reads file in text mode and returns iterator yielding file lines.

    :param fs_api:
        File system API object.

    :param path:
        Path to a text file to be read.

    :param encoding:
        Encoding using to decode file content.
    """
    for line in io.StringIO(fs_api.read(path).decode(encoding)):
        yield line


def write_lines(
    fs_api: IFileSystemWriter,
    path: str,
    lines: typing.Iterable[str],
    encoding: str = "utf-8",
):
    """Helper function that writes lines to a text file either creating or modifying it.

    :param fs_api:
        File system API object.

    :param path:
        Path to a text file to be created/replaced.

    :param lines:
        Lines to be written to a file.

    :param encoding:
        Encoding to be used to encode file.
    """
    src = io.StringIO()
    src.writelines(lines)
    fs_api.write(path, src.getvalue().encode(encoding))
