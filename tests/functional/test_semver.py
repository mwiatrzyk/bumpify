import pytest
from mockify.api import Return

from bumpify.core.semver.helpers import make_dummy_conventional_commit, make_dummy_version_tag
from bumpify.core.semver.implementation import SemVerApi
from bumpify.core.semver.interface import ISemVerApi
from bumpify.core.semver.objects import (
    ChangelogEntry,
    ChangelogEntryData,
    ConventionalCommitData,
    Version,
    VersionTag,
)
from bumpify.core.vcs.helpers import make_dummy_commit, make_dummy_rev, make_dummy_tag

API = ISemVerApi


@pytest.fixture
def api(vcs_reader_writer_mock):
    return SemVerApi(vcs_reader_writer_mock)


class TestListMergedVersionTags:

    @pytest.fixture(autouse=True)
    def setup(self, api: API, vcs_reader_writer_mock):
        self.api = api
        self.vcs_reader_writer_mock = vcs_reader_writer_mock

    def test_when_no_tags_found_then_empty_list_returned(self):
        self.vcs_reader_writer_mock.list_merged_tags.expect_call().will_once(Return([]))
        assert self.api.list_version_tags() == []

    def test_when_tags_found_but_none_is_semantic_version_tag_then_return_empty_list(self):
        tags = [
            make_dummy_tag("foo"),
        ]
        self.vcs_reader_writer_mock.list_merged_tags.expect_call().will_once(Return(tags))
        assert self.api.list_version_tags() == []

    @pytest.mark.parametrize(
        "tag_name, expected_version",
        [
            ("v1.2.3", Version(major=1, minor=2, patch=3)),
            ("ver1.2.3", Version(major=1, minor=2, patch=3)),
            ("ver-1.2.3", Version(major=1, minor=2, patch=3)),
            ("v1.2.3-rc.123", Version(major=1, minor=2, patch=3, prerelease=["rc", 123])),
            (
                "v1.2.3-rc.123+abc",
                Version(major=1, minor=2, patch=3, prerelease=["rc", 123], buildmetadata="abc"),
            ),
        ],
    )
    def test_successfully_parse_version_tag(self, tag_name, expected_version):
        tags = [make_dummy_tag(tag_name)]
        self.vcs_reader_writer_mock.list_merged_tags.expect_call().will_once(Return(tags))
        version_tags = self.api.list_version_tags()
        assert len(version_tags) == 1
        assert version_tags[0].tag == tags[0]
        assert version_tags[0].version == expected_version

    @pytest.mark.parametrize(
        "tags, expected_version_tags",
        [
            (["v1.0.0", "v1.0.1"], ["v1.0.0", "v1.0.1"]),
            # NOTE: Although the tags are sorted by semver rules, reordering should
            # never happen as in testcase data below. The only way for this to
            # happen is when some incorrect version tag is added manually.
            (["v1.0.1", "v1.0.0"], ["v1.0.0", "v1.0.1"]),
        ],
    )
    def test_returned_tags_are_ordered_according_to_semantic_version_rules(
        self, tags, expected_version_tags
    ):
        tags = [make_dummy_tag(x) for x in tags]
        self.vcs_reader_writer_mock.list_merged_tags.expect_call().will_once(Return(tags))
        version_tags = self.api.list_version_tags()
        assert [x.tag.name for x in version_tags] == expected_version_tags


class TestListConventionalCommits:

    @pytest.fixture(autouse=True)
    def setup(self, api: API, vcs_reader_writer_mock):
        self.api = api
        self.vcs_reader_writer_mock = vcs_reader_writer_mock

    @pytest.mark.parametrize("start_rev", [None, make_dummy_rev()])
    @pytest.mark.parametrize("end_rev", [None, make_dummy_rev()])
    def test_when_no_conventional_commits_found_then_empty_list_is_returned(
        self, start_rev, end_rev
    ):
        commits = [make_dummy_commit("non conventional change")]
        self.vcs_reader_writer_mock.list_commits.expect_call(
            start_rev=start_rev, end_rev=end_rev
        ).will_once(Return(commits))
        conventional_commits = self.api.list_conventional_commits(start_rev, end_rev)
        assert conventional_commits == []

    @pytest.mark.parametrize(
        "message, expected_conventional_commit_data",
        [
            ("fix: a fix", ConventionalCommitData(type="fix", description="a fix")),
        ],
    )
    def test_parse_conventional_commit(self, message, expected_conventional_commit_data):
        commits = [make_dummy_commit(message)]
        self.vcs_reader_writer_mock.list_commits.expect_call(
            start_rev=None, end_rev=None
        ).will_once(Return(commits))
        conventional_commits = self.api.list_conventional_commits()
        assert len(conventional_commits) == 1
        assert conventional_commits[0].commit == commits[0]
        assert conventional_commits[0].data == expected_conventional_commit_data


class TestLoadUnreleasedChanges:

    @pytest.fixture(autouse=True)
    def setup(self, api: API, vcs_reader_writer_mock):
        self.api = api
        self.vcs_reader_writer_mock = vcs_reader_writer_mock
        self.version_tag = make_dummy_version_tag(Version.from_str("1.0.0"))

    def test_when_no_changes_made_since_last_version_tag_then_return_none(self):
        self.vcs_reader_writer_mock.list_commits.expect_call(
            start_rev=self.version_tag.tag.rev, end_rev=None
        ).will_once(Return([]))
        assert self.api.load_unreleased_changes(self.version_tag) is None

    def test_parse_unreleased_fix(self):
        commits = [make_dummy_commit("fix: a fix")]
        self.vcs_reader_writer_mock.list_commits.expect_call(
            start_rev=self.version_tag.tag.rev, end_rev=None
        ).will_once(Return(commits))
        unreleased_changes = self.api.load_unreleased_changes(self.version_tag)
        assert unreleased_changes is not None
        assert len(unreleased_changes.fixes) == 1
        unreleased_fix = unreleased_changes.fixes[0]
        assert unreleased_fix.commit == commits[0]
        assert unreleased_fix.data.type == "fix"
        assert unreleased_fix.data.description == "a fix"

    def test_parse_unreleased_feature(self):
        commits = [make_dummy_commit("feat: a feat")]
        self.vcs_reader_writer_mock.list_commits.expect_call(
            start_rev=self.version_tag.tag.rev, end_rev=None
        ).will_once(Return(commits))
        unreleased_changes = self.api.load_unreleased_changes(self.version_tag)
        assert unreleased_changes is not None
        assert len(unreleased_changes.feats) == 1
        unreleased_feat = unreleased_changes.feats[0]
        assert unreleased_feat.commit == commits[0]
        assert unreleased_feat.data.type == "feat"
        assert unreleased_feat.data.description == "a feat"

    def test_parse_unreleased_other_breaking_change(self):
        commits = [make_dummy_commit("test!: a breaking test fix")]
        self.vcs_reader_writer_mock.list_commits.expect_call(
            start_rev=self.version_tag.tag.rev, end_rev=None
        ).will_once(Return(commits))
        unreleased_changes = self.api.load_unreleased_changes(self.version_tag)
        assert unreleased_changes is not None
        assert len(unreleased_changes.others) == 1
        assert len(unreleased_changes.others["test"]) == 1
        assert len(unreleased_changes.breaking_changes) == 1
        assert unreleased_changes.breaking_changes == ["a breaking test fix"]
        unreleased = unreleased_changes.others["test"][0]
        assert unreleased.commit == commits[0]
        assert unreleased.data.type == "test"
        assert unreleased.data.description == "a breaking test fix"


class TestLoadChangelog:

    @pytest.fixture(autouse=True)
    def setup(self, api: API, vcs_reader_writer_mock):
        self.api = api
        self.vcs_reader_writer_mock = vcs_reader_writer_mock

    def validate_initial_entry(self, entry: ChangelogEntry, expected_version_tag: VersionTag):
        assert entry.version == expected_version_tag.version
        assert entry.prev_version is None
        assert entry.released == expected_version_tag.tag.created
        assert entry.data is None

    def validate_middle_entry(
        self,
        entry: ChangelogEntry,
        expected_version_tag: VersionTag,
        expected_prev_version_tag: VersionTag,
        expected_data: ChangelogEntryData,
    ):
        assert entry.version == expected_version_tag.version
        assert entry.prev_version == expected_prev_version_tag.version
        assert entry.released == expected_version_tag.tag.created
        assert entry.data == expected_data

    def test_when_only_one_version_in_list_then_return_only_initial_version_in_changelog(self):
        version_tags = [make_dummy_version_tag(Version.from_str("0.0.1"))]
        changelog = self.api.load_changelog(version_tags)
        assert changelog is not None
        assert len(changelog.entries) == 1
        initial = changelog.entries[0]
        self.validate_initial_entry(initial, version_tags[0])

    def test_when_two_version_tags_in_list_then_return_changelog_with_two_entries(self):
        version_tags = [
            make_dummy_version_tag(Version.from_str("0.0.1")),
            make_dummy_version_tag(Version.from_str("0.0.2")),
        ]
        commits = [make_dummy_commit("fix: a fix")]
        self.vcs_reader_writer_mock.list_commits.expect_call(
            start_rev=version_tags[0].tag.rev, end_rev=version_tags[1].tag.rev
        ).will_once(Return(commits))
        changelog = self.api.load_changelog(version_tags)
        assert changelog is not None
        assert len(changelog.entries) == 2
        first, second = changelog.entries
        expected_second_data = ChangelogEntryData(
            fixes=[
                make_dummy_conventional_commit(
                    "fix: a fix", rev=commits[0].rev, author_date=commits[0].author_date
                )
            ]
        )
        self.validate_initial_entry(first, version_tags[0])
        self.validate_middle_entry(second, version_tags[1], version_tags[0], expected_second_data)

    def test_when_three_version_tags_in_list_then_return_changelog_with_three_entries(self):
        version_tags = [
            make_dummy_version_tag(Version.from_str("0.0.1")),
            make_dummy_version_tag(Version.from_str("0.0.2")),
            make_dummy_version_tag(Version.from_str("0.0.3")),
        ]
        first_commits = [make_dummy_commit("fix: a fix")]
        self.vcs_reader_writer_mock.list_commits.expect_call(
            start_rev=version_tags[0].tag.rev, end_rev=version_tags[1].tag.rev
        ).will_once(Return(first_commits))
        second_commits = [
            make_dummy_commit("fix: a fix"),
            make_dummy_commit("feat: a feat"),
        ]
        self.vcs_reader_writer_mock.list_commits.expect_call(
            start_rev=version_tags[1].tag.rev, end_rev=version_tags[2].tag.rev
        ).will_once(Return(second_commits))
        changelog = self.api.load_changelog(version_tags)
        assert changelog is not None
        assert len(changelog.entries) == 3
        first, second, third = changelog.entries
        expected_second_data = ChangelogEntryData(
            fixes=[
                make_dummy_conventional_commit(
                    "fix: a fix", rev=first_commits[0].rev, author_date=first_commits[0].author_date
                )
            ]
        )
        expected_third_data = ChangelogEntryData(
            fixes=[
                make_dummy_conventional_commit(
                    "fix: a fix",
                    rev=second_commits[0].rev,
                    author_date=second_commits[0].author_date,
                )
            ],
            feats=[
                make_dummy_conventional_commit(
                    "feat: a feat",
                    rev=second_commits[1].rev,
                    author_date=second_commits[1].author_date,
                )
            ],
        )
        self.validate_initial_entry(first, version_tags[0])
        self.validate_middle_entry(second, version_tags[1], version_tags[0], expected_second_data)
        self.validate_middle_entry(third, version_tags[2], version_tags[1], expected_third_data)

    def test_when_two_version_tags_in_list_but_no_conventional_commits_found_between_first_and_second_then_second_data_is_empty(self):
        version_tags = [
            make_dummy_version_tag(Version.from_str("0.0.1")),
            make_dummy_version_tag(Version.from_str("0.0.2")),
        ]
        self.vcs_reader_writer_mock.list_commits.expect_call(
            start_rev=version_tags[0].tag.rev, end_rev=version_tags[1].tag.rev
        ).will_once(Return([]))
        changelog = self.api.load_changelog(version_tags)
        assert changelog is not None
        assert len(changelog.entries) == 2
        first, second = changelog.entries
        self.validate_initial_entry(first, version_tags[0])
        self.validate_middle_entry(second, version_tags[1], version_tags[0], None)
