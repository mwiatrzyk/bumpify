from typing import List

from pydantic import BaseModel

from bumpify.core.config.objects import register_module_config


@register_module_config("hook")
class HookConfig(BaseModel):
    """Configuration object for hook module."""

    #: List of hook file(-s) relative paths.
    #:
    #: Each element must point to an existing and valid Python module. Once
    #: configured, those modules will be loaded by Bumpify when a hook is
    #: going to be used for the first time.
    paths: List[str]
