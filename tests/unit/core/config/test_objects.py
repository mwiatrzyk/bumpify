import pytest

from bumpify.model import Model
from bumpify.core.config.exc import (
    ConfigValidationError,
    ModuleConfigNotRegistered,
    RequiredModuleConfigMissing,
)
from bumpify.core.config.objects import Config, LoadedConfig, register_section
from bumpify.exc import ValidationError


class TestConfig:

    @pytest.fixture(autouse=True)
    def setup(self, config: Config):
        self.uut = config

    def test_save_section_fails_if_model_is_not_registered(self):

        class Dummy(Model):
            foo: int

        with pytest.raises(ModuleConfigNotRegistered) as excinfo:
            self.uut.save_section(Dummy(foo=123))
        assert excinfo.value.model_type is Dummy

    def test_load_section_fails_if_model_is_not_registered(self):

        class Dummy(Model):
            foo: int

        with pytest.raises(ModuleConfigNotRegistered) as excinfo:
            self.uut.load_section(Dummy)
        assert excinfo.value.model_type is Dummy

    def test_load_section_returns_none_if_no_section_data_does_not_exist(self):

        @register_section("dummy")
        class Dummy(Model):
            foo: int

        assert self.uut.load_section(Dummy) is None

    def test_load_section_fails_if_mandatory_field_is_missing(self):

        @register_section("dummy")
        class Dummy(Model):
            foo: int

        self.uut.data = {"dummy": {}}
        with pytest.raises(ValidationError) as excinfo:
            self.uut.load_section(Dummy)
        e = excinfo.value
        assert len(e.errors) == 1
        assert e.find_msg_by_loc("dummy", "foo") == "this field is required"

    def test_save_section_and_load_it_back(self):

        @register_section("dummy")
        class Dummy(Model):
            foo: int

        dummy = Dummy(foo=123)
        self.uut.save_section(dummy)
        assert self.uut.data["dummy"] == {"foo": 123}
        assert self.uut.load_section(Dummy) == dummy


class TestLoadedConfig:

    @pytest.fixture(autouse=True)
    def setup(self, loaded_config: LoadedConfig):
        self.uut = loaded_config

    def test_load_section_returns_none_when_no_config_available(self):

        @register_section("dummy")
        class Dummy(Model):
            foo: int

        assert self.uut.load_section(Dummy) is None

    def test_load_section_returns_data_when_config_present(self):

        @register_section("dummy")
        class Dummy(Model):
            foo: int

        dummy = Dummy(foo=123)
        self.uut.config.save_section(dummy)
        loaded_dummy = self.uut.load_section(Dummy)
        assert loaded_dummy.config_file_abspath == self.uut.config_file_abspath
        assert loaded_dummy.config == dummy

    def test_load_section_fails_if_mandatory_field_is_missing(self):

        @register_section("dummy")
        class Dummy(Model):
            foo: int

        self.uut.config.data = {"dummy": {}}
        with pytest.raises(ConfigValidationError) as excinfo:
            self.uut.load_section(Dummy)
        e = excinfo.value
        assert e.config_file_abspath == self.uut.config_file_abspath
        assert isinstance(e.original_exc, ValidationError)
        assert len(e.original_exc.errors) == 1
        assert e.original_exc.find_msg_by_loc("dummy", "foo") == "this field is required"

    def test_require_section_returns_section_if_config_is_found(self):

        @register_section("dummy")
        class Dummy(Model):
            foo: int

        dummy = Dummy(foo=123)
        self.uut.config.save_section(dummy)
        loaded_dummy = self.uut.require_section(Dummy)
        assert loaded_dummy.config_file_abspath == self.uut.config_file_abspath
        assert loaded_dummy.config == dummy

    def test_require_section_raises_exception_if_config_not_found(self):

        @register_section("dummy")
        class Dummy(Model):
            foo: int

        with pytest.raises(RequiredModuleConfigMissing) as excinfo:
            self.uut.require_section(Dummy)
        assert excinfo.value.config_file_abspath == self.uut.config_file_abspath
        assert excinfo.value.model_type is Dummy
