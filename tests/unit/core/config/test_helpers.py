import pytest

from mockify.api import Return

from bumpify.core.config import exc as config_exc
from bumpify.core.config.objects import LoadedConfig
from bumpify.core.config.helpers import require_config


class TestRequireConfig:

    @pytest.fixture(autouse=True)
    def setup(self, config_reader_writer_mock, loaded_config: LoadedConfig):
        self.config_reader_writer_mock = config_reader_writer_mock
        self.loaded_config = loaded_config

    def test_when_config_exists_then_return_it(self):
        self.config_reader_writer_mock.load.expect_call().will_once(Return(self.loaded_config))
        loaded_config = require_config(self.config_reader_writer_mock)
        assert loaded_config is self.loaded_config

    def test_when_config_does_not_exist_then_exception_is_raised(self, config_file_abspath: str):
        self.config_reader_writer_mock.load.expect_call().will_once(Return(None))
        self.config_reader_writer_mock.abspath.expect_call().will_once(Return(config_file_abspath))
        with pytest.raises(config_exc.ConfigFileNotFound) as excinfo:
            require_config(self.config_reader_writer_mock)
        assert excinfo.value.config_file_abspath == config_file_abspath
