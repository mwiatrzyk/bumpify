import sys
import traceback
from typing import Any, Callable, Dict, Set

from bumpify.core.config.objects import LoadedConfig
from bumpify.core.filesystem.interface import IFileSystemReader
from bumpify.core.hook.interface import IHookApi, IHookFunction
from bumpify.core.hook.objects import HookConfig

from . import _utils
from .exc import HookExecFailed
from .interface import IHookApiLoader


class _HookFunction(IHookFunction):

    def __init__(self, func: Callable):
        self._func = func

    def invoke(self, *args, **kwargs) -> Any:
        return self._func(*args, **kwargs)


class HookApiLoader(IHookApiLoader):
    """Default implementation of the :class:`IHookApiLoader` interface.

    It loads and executes Python scripts configured as Bumpify hooks to find
    and register hook functions.

    :param loaded_config:
        Config object.

        Used to get paths to configured hook files.

    :param filesystem_reader:
        Filesystem reader instance.

        Used to read payload of a hook file.
    """

    def __init__(self, loaded_config: LoadedConfig, filesystem_reader: IFileSystemReader):
        self._loaded_config = loaded_config
        self._filesystem_reader = filesystem_reader

    def load(self) -> IHookApi:
        hook_config = self._loaded_config.config.load_section(HookConfig)
        if not hook_config:
            return self._HookApi({})
        all_hook_functions = {}
        for path in hook_config.paths:
            hook_payload = self._filesystem_reader.read(path)
            try:
                g = globals()
                exec(hook_payload, g)
                for k in list(g):
                    v = g[k]
                    hook_name = _utils.get_hook_name(v)
                    if hook_name is not None:
                        all_hook_functions[hook_name] = v
                        del g[k]
            except:
                exc_type, exc, tb = sys.exc_info()
                formatted_exc = traceback.format_exception(exc_type, exc, tb.tb_next)
                tb = "".join(formatted_exc)
                raise HookExecFailed(self._filesystem_reader.abspath(path), tb, exc)
        return self._HookApi(all_hook_functions)

    class _HookApi(IHookApi):

        def __init__(self, all_hook_functions: dict):
            self._all_hook_functions = all_hook_functions

        def loaded_hook_names(self) -> Set[str]:
            return set(self._all_hook_functions)

        def get_hook(self, name: str, default_func: Callable) -> IHookFunction:
            maybe_hook = self._all_hook_functions.get(name)
            if maybe_hook is None:
                return _HookFunction(default_func)
            return _HookFunction(maybe_hook)


class AlwaysDefaultHookApiLoader(IHookApiLoader):
    """Hook API loader that does not load any hooks and always uses provided
    default functions."""

    def load(self) -> IHookApi:
        return self._HookApi()

    class _HookApi(IHookApi):

        def loaded_hook_names(self) -> Set[str]:
            return set()

        def get_hook(self, name: str, default_func: Callable) -> IHookFunction:
            return _HookFunction(default_func)
