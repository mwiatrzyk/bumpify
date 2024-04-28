from typing import Callable


def hook(name: str) -> Callable:

    def decorator(func: Callable):
        func._bumpify_hook_name = name
        return func

    return decorator
