import dataclasses
from typing import Dict, Generic, Optional, Type, TypeVar

from pydantic import BaseModel
import pydantic

from bumpify import utils, exc
from bumpify.core.config.exc import ConfigValidationError, ModuleConfigNotRegistered, RequiredModuleConfigMissing

MT = TypeVar("MT", bound=BaseModel)

_module_config_models = {}


def register_section(name: str):
    """Decorator used to mark a model class as a Bumpify configuration file
    section model of given name.

    :param name:
        The name of a section.

        This will be used as a root section name inside a TOML configuration
        file.
    """

    def decorator(cls):
        _module_config_models[cls] = name
        return cls

    return decorator


@dataclasses.dataclass
class Config:
    """Root configuration model for Bumpify."""

    #: Raw config data.
    #:
    #: This dictionary contains contents of the parsed TOML config file and is
    #: modified when sections are created or updated.
    data: Dict[str, dict] = dataclasses.field(default_factory=dict)

    def save_section(self, model: BaseModel):
        """Create or override section inside a config file.

        Encodes and and writes data under previously configured section (see
        :func:`register_section`) into the :attr:`module` property. If
        model class was not registered earlier, then
        :exc:`ModuleConfigNotRegistered` exception will be raised.

        :param model:
            The model to be used to create or update a section.
        """
        model_type = type(model)
        name = _module_config_models.get(model_type)
        if name is None:
            raise ModuleConfigNotRegistered(model_type)
        data = model.model_dump()
        data = utils.json_dict(data)
        self.data[name] = data

    def load_section(self, model_type: Type[MT]) -> Optional[MT]:
        """Load and parse section assigned to provided model type.

        Returns ``None`` if no configuration was found for that model, instance
        of *model_type* if configuration is found, or raises exception if model
        was not registered.

        :param model_type:
            Type of a section model to load.
        """
        name = _module_config_models.get(model_type)
        if name is None:
            raise ModuleConfigNotRegistered(model_type)
        data = self.data.get(name)
        if data is None:
            return None
        try:
            return model_type(**data)
        except pydantic.ValidationError as e:
            errors = [exc.ValidationError.ErrorItem((name,) + x['loc'], x['msg']) for x in e.errors()]
            raise exc.ValidationError(errors, original_exc=e)


@dataclasses.dataclass
class LoadedSection(Generic[MT]):
    """Model representing single loaded config file section."""

    #: Absolute path to config file.
    config_file_abspath: str

    #: Parsed section configuration object.
    config: MT


@dataclasses.dataclass
class LoadedConfig:
    """Model representing loaded config file object."""

    #: Absolute path to config file.
    #:
    #: Used by helpers to render config-specific errors and point to a file
    #: that caused the problem. DO NOT use this property for direct file
    #: manipulations; use config domain's dedicated API for that purpose.
    config_file_abspath: str

    #: Parsed config object.
    config: Config

    def load_section(self, model_type: Type[MT]) -> Optional[LoadedSection[MT]]:
        """Similar to :meth:`Config.load_module_config`, but additionally
        wrapping returned object with :class:`LoadedModuleConfig` proxy, which
        additionally contains a path to a source configuration file.

        Returns :class:`LoadedModuleConfig` instance or ``None`` if no
        configuration is available for given *model_type*.

        :param model_type:
            Type of a model to be returned.

            It must be registered first (see :func:`register_section`
            function for more details).
        """
        try:
            obj = self.config.load_section(model_type)
        except exc.ValidationError as e:
            raise ConfigValidationError(self.config_file_abspath, e)
        if obj is None:
            return None
        return LoadedSection(
            config_file_abspath=self.config_file_abspath,
            config=obj,
        )

    def require_section(self, model_type: Type[MT]) -> LoadedSection[MT]:
        """Similar to :meth:`load_module_config`, but raises
        :exc:`RequiredModuleConfigMissing` exception instead of returning
        ``None``.

        :param model_type:
            Type of a model to be returned.
        """
        obj = self.load_section(model_type)
        if obj is None:
            raise RequiredModuleConfigMissing(self.config_file_abspath, model_type)
        return obj
