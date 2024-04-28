"""Hooks for semantic versioning."""

from bumpify.core.hook.decorators import hook


def commit_parser_hook(func):
    """Decorate user-defined hook function as a commit parser.

    A decorated function must satisfy following interface::

        def hook(commit: Commit) -> Optional[ConventionalCommit]:
            ...
    """
    return hook("core.semver.commit_parser")(func)
