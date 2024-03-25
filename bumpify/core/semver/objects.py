import dataclasses
import datetime
import enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from bumpify.core.vcs.objects import Commit, Tag

from . import _constants, _parsing


class SemVerConfig(BaseModel):
    """Model to store semantic versioning configuration."""

    class ChangelogFile(BaseModel):
        """Model for storing configuration of a particular changelog file."""

        #: Path to a changelog file.
        #:
        #: This is relative to project's root directory.
        path: str

        #: Changelog file encoding.
        #:
        #: By default, UTF-8 is used. This is needed because changelog files
        #: are overwritten upon version bump and it is necessary to know what
        #: encoding should be used.
        encoding: str = "utf-8"

    #: List of changelog files to be updated on version bump.
    changelog_files: List[ChangelogFile] = [ChangelogFile(path="CHANGELOG.md")]


class Version(BaseModel):
    """Semantic version data model."""

    class Component(enum.Enum):
        """Enumeration with version component.

        Each value represents one semantic version component; either major,
        minor or patch number.
        """

        MAJOR = "major"
        MINOR = "minor"
        PATCH = "patch"

    #: Major version number.
    major: int

    #: Minor version number.
    minor: int

    #: Patch number.
    patch: int

    #: Prerelease info.
    prerelease: List[Union[int, str]] = []

    #: Build metadata info.
    #:
    #: This is ignored when versions are compared, but can be used to store
    #: various build information, such as architecture, platform, commit hash etc.
    buildmetadata: Optional[str] = None

    def __lt__(self, other: "Version") -> bool:
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch
        if self.prerelease != other.prerelease:
            for left, right in zip(self.prerelease, other.prerelease):
                if left != right:
                    if isinstance(left, int) and isinstance(right, str):
                        return True
                    if isinstance(left, str) and isinstance(right, int):
                        return False
                    return left < right
            return True

    def __gt__(self, other: "Version") -> bool:
        if self.__eq__(other):
            return False
        return not self.__lt__(other)

    def to_str(self) -> str:
        """Convert this model to a semantic version string."""
        out = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            out += f"-{'.'.join(str(x) for x in self.prerelease)}"
        if self.buildmetadata:
            out += f"+{self.buildmetadata}"
        return out

    def bump(
        self, component: Component, prerelease: str = None, buildmetadata: str = None
    ) -> "Version":
        """Bump this version and create new version.

        :param component:
            Version component to bump.

            Depending on the value given, it will bump major, minor or patch
            number.

        :param prerelease:
            Prerelease name.

            When given, then prerelease version will be created instead of
            regular one.

        :param buildmetadata:
            Build metadata to be added to a newly created version object.
        """
        new_prerelease = list(self.prerelease)
        given_prerelease = prerelease.split(".") if prerelease else []
        if new_prerelease:
            if component == Version.Component.MINOR and self.patch != 0:
                return Version(
                    major=self.major,
                    minor=self.minor + 1,
                    patch=0,
                    prerelease=given_prerelease,
                    buildmetadata=buildmetadata,
                )
            if component == Version.Component.MAJOR and (self.patch != 0 or self.minor != 0):
                return Version(
                    major=self.major + 1,
                    minor=0,
                    patch=0,
                    prerelease=given_prerelease,
                    buildmetadata=buildmetadata,
                )
        if given_prerelease:
            if not new_prerelease:
                new_prerelease = given_prerelease
            elif new_prerelease[: len(given_prerelease)] == given_prerelease:
                if isinstance(new_prerelease[-1], int):
                    new_prerelease[-1] += 1
                else:
                    new_prerelease.append(1)
                return Version(
                    major=self.major,
                    minor=self.minor,
                    patch=self.patch,
                    prerelease=new_prerelease,
                    buildmetadata=buildmetadata,
                )
            else:
                return Version(
                    major=self.major,
                    minor=self.minor,
                    patch=self.patch,
                    prerelease=given_prerelease,
                    buildmetadata=buildmetadata,
                )
        elif new_prerelease:
            return Version(major=self.major, minor=self.minor, patch=self.patch)
        if component == Version.Component.MAJOR:
            return Version(
                major=self.major + 1,
                minor=0,
                patch=0,
                prerelease=new_prerelease,
                buildmetadata=buildmetadata,
            )
        if component == Version.Component.MINOR:
            return Version(
                major=self.major,
                minor=self.minor + 1,
                patch=0,
                prerelease=new_prerelease,
                buildmetadata=buildmetadata,
            )
        return Version(
            major=self.major,
            minor=self.minor,
            patch=self.patch + 1,
            prerelease=new_prerelease,
            buildmetadata=buildmetadata,
        )

    @classmethod
    def from_str(cls, value: str) -> Optional["Version"]:
        """Parse given exact semantic version string into a new instance of
        :class:`Version` class.

        Returns ``None`` if *value* is not a valid semantic versioning string.

        :param value:
            String to be parsed.
        """

        def to_int_or_to_str(v: str):
            if v.isnumeric():
                return int(v)
            return v

        m = _constants.SEMVER_EXACT_RE.match(value)
        if m is None:
            return None
        major = m.group("major")
        minor = m.group("minor")
        patch = m.group("patch")
        prerelease = m.group("prerelease")
        buildmetadata = m.group("buildmetadata")
        if prerelease is not None:
            prerelease = [to_int_or_to_str(x) for x in prerelease.split(".")]
        return Version(
            major=major,
            minor=minor,
            patch=patch,
            prerelease=prerelease or [],
            buildmetadata=buildmetadata,
        )

    @classmethod
    def extract_from_str(cls, value: str) -> Optional["Version"]:
        """Extract semantic version data from a given string.

        Unlike :meth:`from_str`, this method allows string to have prefix
        and/or postfix, which are ignored. This is suitable to extract version
        for example from version tag name, which often is prefixed with some
        prefix like ``v`` or ``ver``.

        Returns new instance of :class:`Version` if version is found, or
        ``None`` otherwise.

        :param value:
            The value to extract version from.
        """
        m = _constants.SEMVER_RE.search(value)
        if m is None:
            return None
        return cls.from_str(m.group(0))


@dataclasses.dataclass
class VersionTag:
    """Glues together repository tag and version object parsed from it."""

    #: VCS tag object, from which the version was parsed.
    tag: Tag

    #: Version parsed from a tag.
    version: Version

    @classmethod
    def from_tag(cls, tag: Tag) -> Optional["VersionTag"]:
        """Create new instance of :class:`VersionTag` from given repository tag.

        Returns ``None`` if *tag* is not a semantic version tag.

        :param tag:
            Repository tag object.
        """
        version = Version.extract_from_str(tag.name)
        if version is None:
            return None
        return cls(
            tag=tag,
            version=version,
        )


class ConventionalCommitData(BaseModel):
    """Model representing data parsed from a conventional commit.

    Visit https://www.conventionalcommits.org/en/v1.0.0/ to read about
    conventional commits. The rules depicted there are used internally by
    Bumpify.
    """

    #: Commit type.
    #:
    #: This is a single noun explaining what kind of change a commit has introduced.
    #: Two are reserved and have special meaning:
    #: * ``fix`` for marking bug fixes,
    #: * ``feat`` for new feature introduction.
    type: str

    #: Short change description (parsed from commit subject).
    description: str

    #: Long change description (parsed from commit body).
    body: Optional[str] = None

    #: Change scope.
    scope: Optional[str] = None

    #: List of breaking changes.
    #:
    #: This is parsed from a ``BREAKING CHANGE`` commit footer(-s).
    breaking_changes: List[str] = []

    #: Placeholder for non breaking change footers parsed from commit message.
    footers: Dict[str, str] = {}

    @classmethod
    def from_commit_message(cls, message: str) -> Optional["ConventionalCommitData"]:
        """Parse given commit message into a new instance of
        :class:`ConventionalCommitData` class.

        Returns ``None`` if *message* is not a conventional commit message.

        :param message:
            Commit message to be parsed.
        """
        parser = _parsing.ConventionalCommitParser()
        for line in message.splitlines():
            if not parser.feed(line):
                return None
        return cls(**parser.output())


@dataclasses.dataclass
class ConventionalCommit:
    """Glues together commit object and conventional commit data parsed from that commit object."""

    #: Repository commit object.
    commit: Commit

    #: Conventional commit data parsed from a repository commit.
    data: ConventionalCommitData

    @classmethod
    def from_commit(cls, commit: Commit) -> Optional["ConventionalCommit"]:
        """Convert :class:`Commit` object into a new instance of
        :class:`ConventionalCommit` class.

        Raises :exc:`ConventionalCommitParseError` if *commit* is not a valid
        conventional commit.

        :param commit:
            Commit to be converted.
        """
        data = ConventionalCommitData.from_commit_message(commit.message)
        if data is None:
            return None
        return cls(
            commit=commit,
            data=data,
        )


class ChangelogEntryData(BaseModel):
    """Model representing release info description.

    Each release has information about fixes made, features introduced and
    breaking changes made, parsed out from conventional commits.
    """

    #: List of fixes.
    fixes: List[ConventionalCommit] = []

    #: List of features.
    feats: List[ConventionalCommit] = []

    #: Map with list of neither fixes, nor feats, by default with only breaking
    #: changes made.
    others: Dict[str, List[ConventionalCommit]] = {}

    @property
    def breaking_changes(self) -> List[str]:
        """List of all breaking changes made."""
        out = []
        for fix in self.fixes:
            out.extend(fix.data.breaking_changes)
        for feat in self.feats:
            out.extend(feat.data.breaking_changes)
        for values in self.others.values():
            for item in values:
                out.extend(item.data.breaking_changes)
        return out

    def is_empty(self) -> bool:
        """Check if this description object contains data."""
        return not self.fixes and not self.feats and not self.others

    def update(self, conventional_commit: ConventionalCommit):
        """Update this object with data taken from given conventional
        commit.

        :param conventional_commit:
            Conventional commit to update from.
        """
        type_ = conventional_commit.data.type
        if type_ == "fix":
            self.fixes.append(conventional_commit)
        elif type_ == "feat":
            self.feats.append(conventional_commit)
        elif conventional_commit.data.breaking_changes:
            self.others.setdefault(type_, []).append(conventional_commit)

    @classmethod
    def from_conventional_commit_list(
        cls, conventional_commits: List[ConventionalCommit]
    ) -> Optional["ChangelogEntryData"]:
        """Helper factory method for creating new instance of
        :class:`ChangelogEntryData` class directly from list of conventional
        commits.

        :param conventional_commits:
            List of conventional commits to be parsed.
        """
        obj = cls()
        for item in conventional_commits:
            obj.update(item)
        if obj.is_empty():
            return None
        return obj


class ChangelogEntry(BaseModel):
    """Model representing single entry inside a changelog."""

    #: Release version or ``None`` for unreleased.
    version: Optional[Version] = None

    #: Previous release version or ``None`` for initial or unreleased.
    prev_version: Optional[Version] = None

    #: Release date and time or ``None`` for unreleased.
    released: Optional[datetime.datetime]

    #: Release data.
    data: Optional[ChangelogEntryData] = None

    # TODO: Check `released` is set when `version` is set

    def is_initial(self) -> bool:
        """Check if this is initial release info."""
        return self.version is not None and self.prev_version is None

    def is_unreleased(self) -> bool:
        """Check if this is an unreleased release info."""
        return self.version is None


class Changelog(BaseModel):
    """Model representing project's changelog.

    This is basically an ordered collection of :class:`ChangelogEntry` objects.
    """

    #: List of changelog entries.
    #:
    #: Each item of this list represents details of a changes introduced in
    #: particular release. The list is sorted in ascending order by
    #: :attr:`ChangelogEntry.version` field (with oldest version at index 0 and
    #: newest at index -1).
    entries: List[ChangelogEntry] = []

    def add_entry(self, entry: ChangelogEntry):
        """Validate and add entry to the changelog.

        :param entry:
            Changelog entry object.
        """
        self.entries.append(entry)
