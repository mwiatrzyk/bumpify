import dataclasses
import enum
from typing import Dict, Generic, Optional, Type, TypeVar

from pydantic import BaseModel

from bumpify import utils
from bumpify.core.config.exc import ModuleConfigNotRegistered, RequiredModuleConfigMissing

MT = TypeVar("MT", bound=BaseModel)

_module_config_models = {}


def register_module_config(name: str):
    """Decorator used to mark a model class as a Bumpify module configuration
    object.

    :param name:
        The name of a module.

        This will be used to place configuration in right place of TOML file.
    """

    def decorator(cls):
        _module_config_models[cls] = name
        return cls

    return decorator


class VCSConfig(BaseModel):
    """VCS repository configuration model."""

    class Type(enum.Enum):
        """Supported VCS types."""

        AUTO = "auto"
        GIT = "git"

    #: VCS type.
    type: Type


class Config(BaseModel):
    """Root configuration model for Bumpify."""

    #: VCS (i.e. Version Control System) configuration of the project.
    vcs: VCSConfig

    #: Configuration of Bumpify's modules.
    #:
    #: Each domain can register its own specific config model which will be
    #: used during parsing of a raw config data stored here. This was designed
    #: to implement loose coupling between config domain and domain-specific
    #: setting models.
    module: Dict[str, dict] = {}

    def save_module_config(self, model: BaseModel):
        """Create or override module configuration.

        Encodes and and writes data under previously configured key (see
        :func:`register_module_config`) into the :attr:`module` property. If
        model class was not registered earlier, then exception is raised.

        :param model:
            The model to be written.
        """
        model_type = type(model)
        name = _module_config_models.get(model_type)
        if name is None:
            raise ModuleConfigNotRegistered(model_type)
        data = model.model_dump()
        data = utils.json_dict(data)
        self.module[name] = data

    def load_module_config(self, model_type: Type[MT]) -> Optional[MT]:
        """Load module configuration for given model type.

        Returns ``None`` if no configuration found for that model, instance of
        *model_type* if configuration found, or raises exception if model was
        not registered.

        :param model_type:
            Type of a configuration model to load.
        """
        name = _module_config_models.get(model_type)
        if name is None:
            raise ModuleConfigNotRegistered(model_type)
        data = self.module.get(name)
        if data is None:
            return None
        return model_type(**data)


@dataclasses.dataclass
class LoadedModuleConfig(Generic[MT]):
    """Model representing loaded module config."""

    #: Absolute path to config file.
    config_file_abspath: str

    #: Parsed module configuration object.
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

    def load_module_config(self, model_type: Type[MT]) -> Optional[LoadedModuleConfig[MT]]:
        """Similar to :meth:`Config.load_module_config`, but additionally
        wrapping returned object with :class:`LoadedModuleConfig` proxy, which
        additionally contains a path to a source configuration file.

        Returns :class:`LoadedModuleConfig` instance or ``None`` if no
        configuration is available for given *model_type*.

        :param model_type:
            Type of a model to be returned.

            It must be registered first (see :func:`register_module_config`
            function for more details).
        """
        obj = self.config.load_module_config(model_type)
        if obj is None:
            return None
        return LoadedModuleConfig(
            config_file_abspath=self.config_file_abspath,
            config=obj,
        )

    def require_module_config(self, model_type: Type[MT]) -> LoadedModuleConfig[MT]:
        """Similar to :meth:`load_module_config`, but raises
        :exc:`RequiredModuleConfigMissing` exception instead of returning
        ``None``.

        :param model_type:
            Type of a model to be returned.
        """
        obj = self.load_module_config(model_type)
        if obj is None:
            raise RequiredModuleConfigMissing(self.config_file_abspath, model_type)
        return obj
