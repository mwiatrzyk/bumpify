from typing import Any, Optional


def get_hook_name(obj: Any) -> Optional[str]:
    """Check if *obj* is a hook function and return its name if so, or ``None``
    otherwise.

    :param obj:
        The object to be checked.
    """
    if not callable(obj):
        return None
    return getattr(obj, "_bumpify_hook_name", None)
