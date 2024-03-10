import pytest
from pydantic import BaseModel

from bumpify.core.config.exc import ModuleConfigNotRegistered, RequiredModuleConfigMissing
from bumpify.core.config.objects import Config, LoadedConfig, register_module_config


class TestConfig:

    @pytest.fixture(autouse=True)
    def setup(self, config: Config):
        self.uut = config

    def test_save_module_config_fails_if_model_is_not_registered(self):

        class Dummy(BaseModel):
            foo: int

        with pytest.raises(ModuleConfigNotRegistered) as excinfo:
            self.uut.save_module_config(Dummy(foo=123))
        assert excinfo.value.model_type is Dummy

    def test_load_module_config_fails_if_model_is_not_registered(self):

        class Dummy(BaseModel):
            foo: int

        with pytest.raises(ModuleConfigNotRegistered) as excinfo:
            self.uut.load_module_config(Dummy)
        assert excinfo.value.model_type is Dummy

    def test_load_module_config_returns_none_if_no_module_config_data_does_not_exist(self):

        @register_module_config("dummy")
        class Dummy(BaseModel):
            foo: int

        assert self.uut.load_module_config(Dummy) is None

    def test_save_module_config_and_load_it_back(self):

        @register_module_config("dummy")
        class Dummy(BaseModel):
            foo: int

        dummy = Dummy(foo=123)
        self.uut.save_module_config(dummy)
        assert self.uut.module["dummy"] == {"foo": 123}
        assert self.uut.load_module_config(Dummy) == dummy


class TestLoadedConfig:

    @pytest.fixture(autouse=True)
    def setup(self, loaded_config: LoadedConfig):
        self.uut = loaded_config

    def test_load_module_config_returns_none_when_no_config_available(self):

        @register_module_config("dummy")
        class Dummy(BaseModel):
            foo: int

        assert self.uut.load_module_config(Dummy) is None

    def test_load_module_config_returns_data_when_config_present(self):

        @register_module_config("dummy")
        class Dummy(BaseModel):
            foo: int

        dummy = Dummy(foo=123)
        self.uut.config.save_module_config(dummy)
        loaded_dummy = self.uut.load_module_config(Dummy)
        assert loaded_dummy.config_file_abspath == self.uut.config_file_abspath
        assert loaded_dummy.config == dummy

    def test_require_module_config_returns_module_config_if_config_is_found(self):

        @register_module_config("dummy")
        class Dummy(BaseModel):
            foo: int

        dummy = Dummy(foo=123)
        self.uut.config.save_module_config(dummy)
        loaded_dummy = self.uut.require_module_config(Dummy)
        assert loaded_dummy.config_file_abspath == self.uut.config_file_abspath
        assert loaded_dummy.config == dummy

    def test_require_module_config_raises_exception_if_config_not_found(self):

        @register_module_config("dummy")
        class Dummy(BaseModel):
            foo: int

        with pytest.raises(RequiredModuleConfigMissing) as excinfo:
            self.uut.require_module_config(Dummy)
        assert excinfo.value.config_file_abspath == self.uut.config_file_abspath
        assert excinfo.value.model_type is Dummy
