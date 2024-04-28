import abc
from typing import Any, Callable, Set


class IHookFunction(abc.ABC):
    """The interface allowing to execute hook function."""

    @abc.abstractmethod
    def invoke(self, *args, **kwargs) -> Any:
        """Invoke hook function with given parameters and return result.

        This is a low-level hook function call that should additionally be
        wrapped with some higher level function, providing named arguments and
        type hinting.
        """


class IHookApi(abc.ABC):
    """The API for interacting with loaded hooks."""

    @abc.abstractmethod
    def loaded_hook_names(self) -> Set[str]:
        """Return set containing loaded hook function names.

        This may be empty if no hook functions were found.
        """

    @abc.abstractmethod
    def get_hook(self, name: str, default_func: Callable) -> IHookFunction:
        """Get hook function by given *name*, or create an ad-hoc one using
        *default_func* if no hook with provided name was found.

        :param name:
            Name of a hook function.

        :param default_func:
            Fallback function to use if no hook function was found.

            The signature should be the same as for
            :meth:`IHookFunction.invoke` method.
        """


class IHookApiLoader(abc.ABC):
    """An interface for loading Bumpify hooks."""

    @abc.abstractmethod
    def load(self) -> IHookApi:
        """Load hooks and return API object to interact with them.

        This method will return :class:`IHookApi` object even if no hooks were
        configured, so there is no need to check that later.

        This method may raise one of following exceptions:

        * :exc:`FileNotFound` if configured hook file could not be found
        * :exc:`HookError` (or one of its subclasses) if configured hook file
          does not contain valid Python code
        """
