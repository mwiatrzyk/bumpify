from typing import Type

import pydantic

from bumpify import exc


class ConfigError(exc.BumpifyError):
    """Base class for configuration specific errors."""


class ConfigFileNotFound(ConfigError):
    """Raised when config file is expected to exist but it is missing."""

    __message_template__ = "{self.config_file_abspath}"

    #: Absolute path to expected config file.
    config_file_abspath: str

    def __init__(self, config_file_abspath: str):
        super().__init__()
        self.config_file_abspath = config_file_abspath


class ConfigParseError(ConfigError):
    """Raised when it was not possible to parse config file."""

    #: Absolute path to config file.
    config_file_abspath: str

    #: Parsing error reason description.
    reason: str

    def __init__(self, config_file_abspath: str, reason: str, original_exc: Exception = None):
        super().__init__(original_exc)
        self.config_file_abspath = config_file_abspath
        self.reason = reason


class ConfigValidationError(ConfigError):
    """Raised when model validation failed for current configuration settings."""

    #: Absolute path to config file that failed validation.
    config_file_abspath: str

    #: Original validation error.
    original_exc: exc.ValidationError

    def __init__(self, config_file_abspath: str, original_exc: exc.ValidationError):
        super().__init__(original_exc)
        self.config_file_abspath = config_file_abspath

    def __str__(self):
        return f"for config file at: {self.config_file_abspath}\n" + str(self.original_exc)


class ModuleConfigNotRegistered(ConfigError):
    """Raised when trying to save or load a module config using unregistered model class."""

    __message_template__ = "{self.model_type}"

    #: Type of a model that was not registered.
    model_type: Type[pydantic.BaseModel]

    def __init__(self, model_type: Type[pydantic.BaseModel]):
        super().__init__()
        self.model_type = model_type


class RequiredModuleConfigMissing(ConfigError):
    """Raised when required module configuration is missing."""

    __message_template__ = "{self.model_type} (in config file: {self.config_file_abspath})"

    #: Absolute path to config file.
    config_file_abspath: str

    #: Module config object type.
    model_type: Type[pydantic.BaseModel]

    def __init__(self, config_file_abspath: str, model_type: Type[pydantic.BaseModel]):
        super().__init__()
        self.config_file_abspath = config_file_abspath
        self.model_type = model_type
