import pytest
import tomlkit
import tomlkit.exceptions
from pydantic import BaseModel

from bumpify.core.config.exc import ConfigParseError, ConfigValidationError
from bumpify.core.config.implementation import ConfigReaderWriter
from bumpify.core.config.interface import IConfigReaderWriter
from bumpify.core.config.objects import Config, register_module_config
from bumpify.core.filesystem.interface import IFileSystemReaderWriter


class TestConfigReaderWriter:
    SUT = IConfigReaderWriter

    @pytest.fixture
    def sut(self, tmpdir_fs, config_file_path):
        return ConfigReaderWriter(tmpdir_fs, config_file_path)

    @pytest.fixture(autouse=True)
    def setup(
        self,
        config: Config,
        config_file_path: str,
        config_file_abspath: str,
        tmpdir_fs: IFileSystemReaderWriter,
    ):
        self.config = config
        self.config_file_path = config_file_path
        self.config_file_abspath = config_file_abspath
        self.tmpdir_fs = tmpdir_fs

    def test_save_config_and_load_it_back(self, sut: SUT):
        assert not self.tmpdir_fs.exists(self.config_file_path)
        sut.save(self.config)
        assert self.tmpdir_fs.exists(self.config_file_path)
        loaded_config = sut.load()
        assert loaded_config is not None
        assert loaded_config.config_file_abspath == self.config_file_abspath
        assert loaded_config.config == self.config

    def test_load_returns_none_if_config_file_does_not_exist(self, sut: SUT):
        assert not self.tmpdir_fs.exists(self.config_file_path)
        assert sut.load() is None

    @pytest.mark.parametrize(
        "payload, expected_reason",
        [(b"not a toml file", 'Invalid key "not a toml file" at line 1 col 15')],
    )
    def test_load_fails_with_error_if_config_file_is_not_a_valid_toml_file(
        self, sut: SUT, payload, expected_reason
    ):
        self.tmpdir_fs.write(self.config_file_path, payload)
        with pytest.raises(ConfigParseError) as excinfo:
            sut.load()
        assert excinfo.value.config_file_abspath == self.config_file_abspath
        assert excinfo.value.reason == expected_reason
        assert isinstance(excinfo.value.original_exc, tomlkit.exceptions.ParseError)

    @pytest.mark.parametrize(
        "payload, expected_errors",
        [(b'[vcs]\ntype="dummy"', [("vcs.type", "Input should be 'git'")])],
    )
    def test_load_fails_with_validation_error_if_config_file_has_invalid_settings(
        self, sut: SUT, payload, expected_errors
    ):
        self.tmpdir_fs.write(self.config_file_path, payload)
        with pytest.raises(ConfigValidationError) as excinfo:
            sut.load()
        assert excinfo.value.config_file_abspath == self.config_file_abspath
        assert [(e.loc_str, e.msg) for e in excinfo.value.original_exc.errors] == expected_errors

    def test_register_module_settings_model_and_parse_module_settings(self, sut: SUT):

        @register_module_config("dummy")
        class Dummy(BaseModel):
            foo: int

        dummy = Dummy(foo=123)
        self.config.save_module_config(dummy)
        sut.save(self.config)
        loaded_config = sut.load()
        assert loaded_config is not None
        loaded_module_config = loaded_config.config.load_module_config(Dummy)
        assert loaded_module_config == dummy
