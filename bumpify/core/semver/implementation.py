from typing import List

from bumpify.core.semver.objects import VersionTag
from bumpify.core.vcs.interface import IVcsReaderWriter

from .interface import ISemVerApi


class SemVerApi(ISemVerApi):
    """Default implementation of the semantic versioning API."""

    def __init__(self, vcs_reader_writer: IVcsReaderWriter):
        self._vcs_reader_writer = vcs_reader_writer

    def list_version_tags(self) -> List[VersionTag]:
        result = []
        for tag in self._vcs_reader_writer.list_merged_tags():
            maybe_version_tag = VersionTag.from_tag(tag)
            if maybe_version_tag:
                result.append(maybe_version_tag)
        result.sort(key=lambda x: x.version)
        return result
