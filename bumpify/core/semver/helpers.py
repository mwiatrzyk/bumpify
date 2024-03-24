from bumpify.core.vcs.helpers import make_dummy_tag

from .objects import Version, VersionTag


def make_dummy_version_tag(version: Version, rev: str = None) -> VersionTag:
    """Create dummy version tag.

    This helper is useful mostly for testing purposes.

    :param version:
        The version to be attached and encoded in resulting tag's name.

    :param rev:
        Commit revision.

        This overrides default random revision.
    """
    return VersionTag(
        tag=make_dummy_tag(f"v{version.to_str()}", rev=rev),
        version=version,
    )
