from typing import Optional

import pydantic
import tomlkit
import tomlkit.exceptions

from bumpify import exc, utils
from bumpify.core.config.exc import ConfigParseError, ConfigValidationError
from bumpify.core.config.objects import Config, LoadedConfig
from bumpify.core.filesystem.exc import FileNotFound
from bumpify.core.filesystem.interface import IFileSystemReaderWriter

from .interface import IConfigReaderWriter


class ConfigReaderWriter(IConfigReaderWriter):
    """Main implementation of the :class:`IConfigReaderWriter` interface.

    :param filesystem_reader_writer:
        Filesystem reader/writer object.

    :param config_file_path:
        Path to a config file to be managed by this class.

        The path is relative to underlying project's root directory.

    :param config_file_encoding:
        Encoding used to encode/decode config file.
    """

    def __init__(
        self,
        filesystem_reader_writer: IFileSystemReaderWriter,
        config_file_path: str,
        config_file_encoding: str = "utf-8",
    ):
        self._filesystem_reader_writer = filesystem_reader_writer
        self._config_file_path = config_file_path
        self._config_file_encoding = config_file_encoding

    def abspath(self) -> str:
        return self._filesystem_reader_writer.abspath(self._config_file_path)

    def exists(self) -> bool:
        return self._filesystem_reader_writer.exists(self._config_file_path)

    def load(self) -> Optional[LoadedConfig]:
        try:
            data = self._filesystem_reader_writer.read(self._config_file_path).decode(
                self._config_file_encoding
            )
        except FileNotFound:
            return None
        try:
            data = tomlkit.loads(data)
        except tomlkit.exceptions.ParseError as e:
            raise ConfigParseError(self.abspath(), str(e), original_exc=e)
        try:
            return LoadedConfig(
                config_file_abspath=self.abspath(),
                config=Config(data=data),
            )
        except pydantic.ValidationError as e:
            raise ConfigValidationError(self.abspath(), exc.ValidationError(e))

    def save(self, config: Config):
        data = utils.json_dict(config.data, exclude_none=True)
        data = tomlkit.dumps(data)
        self._filesystem_reader_writer.write(
            self._config_file_path, data.encode(self._config_file_encoding)
        )
