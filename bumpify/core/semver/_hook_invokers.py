from typing import Optional

from bumpify.core.hook.interface import IHookApi
from bumpify.core.vcs.objects import Commit

from .objects import ConventionalCommit


def invoke_parse_commit_hook(hook_api: IHookApi, commit: Commit) -> Optional[ConventionalCommit]:
    """Invoke commit parsing hook.

    Return :class:`ConventionalCommit` object parsed from *commit* or ``None``
    to signal that a *commit* cannot be interpreted as a valid conventional
    commit.

    :param hook_api:
        Hook API to be used to access user-defined hook.

    :param commit:
        Commit to be parsed.
    """
    return hook_api.get_hook(
        "core.semver.commit_parser", lambda commit: ConventionalCommit.from_commit(commit)
    ).invoke(commit)
