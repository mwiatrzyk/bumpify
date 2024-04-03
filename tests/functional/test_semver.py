import datetime

import pytest
from mockify.api import Return

from bumpify.core.filesystem.helpers import read_json
from bumpify.core.filesystem.interface import IFileSystemReaderWriter
from bumpify.core.semver.exc import UnsupportedChangelogFormat, VersionFileNotUpdated
from bumpify.core.semver.helpers import make_dummy_conventional_commit, make_dummy_version_tag
from bumpify.core.semver.implementation import SemVerApi
from bumpify.core.semver.interface import ISemVerApi
from bumpify.core.semver.objects import (
    Changelog,
    ChangelogEntry,
    ChangelogEntryData,
    ConventionalCommitData,
    SemVerConfig,
    Version,
    VersionTag,
)
from bumpify.core.vcs.helpers import make_dummy_commit, make_dummy_rev, make_dummy_tag

API = ISemVerApi


@pytest.fixture
def api(semver_config, tmpdir_fs, vcs_reader_writer_mock):
    return SemVerApi(semver_config, tmpdir_fs, vcs_reader_writer_mock)


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


class TestFetchUnreleasedChanges:

    @pytest.fixture(autouse=True)
    def setup(self, api: API, vcs_reader_writer_mock):
        self.api = api
        self.vcs_reader_writer_mock = vcs_reader_writer_mock
        self.version_tag = make_dummy_version_tag(Version.from_str("1.0.0"))

    def test_when_no_changes_made_since_last_version_tag_then_return_none(self):
        self.vcs_reader_writer_mock.list_commits.expect_call(
            start_rev=self.version_tag.tag.rev, end_rev=None
        ).will_once(Return([]))
        assert self.api.fetch_unreleased_changes(self.version_tag) is None

    def test_parse_unreleased_fix(self):
        commits = [make_dummy_commit("fix: a fix")]
        self.vcs_reader_writer_mock.list_commits.expect_call(
            start_rev=self.version_tag.tag.rev, end_rev=None
        ).will_once(Return(commits))
        unreleased_changes = self.api.fetch_unreleased_changes(self.version_tag)
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
        unreleased_changes = self.api.fetch_unreleased_changes(self.version_tag)
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
        unreleased_changes = self.api.fetch_unreleased_changes(self.version_tag)
        assert unreleased_changes is not None
        assert len(unreleased_changes.others) == 1
        assert len(unreleased_changes.others["test"]) == 1
        assert len(unreleased_changes.breaking_changes) == 1
        assert unreleased_changes.breaking_changes == ["a breaking test fix"]
        unreleased = unreleased_changes.others["test"][0]
        assert unreleased.commit == commits[0]
        assert unreleased.data.type == "test"
        assert unreleased.data.description == "a breaking test fix"


class TestFetchChangelog:

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
        changelog = self.api.fetch_changelog(version_tags)
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
        changelog = self.api.fetch_changelog(version_tags)
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
        changelog = self.api.fetch_changelog(version_tags)
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

    def test_when_two_version_tags_in_list_but_no_conventional_commits_found_between_first_and_second_then_second_data_is_empty(
        self,
    ):
        version_tags = [
            make_dummy_version_tag(Version.from_str("0.0.1")),
            make_dummy_version_tag(Version.from_str("0.0.2")),
        ]
        self.vcs_reader_writer_mock.list_commits.expect_call(
            start_rev=version_tags[0].tag.rev, end_rev=version_tags[1].tag.rev
        ).will_once(Return([]))
        changelog = self.api.fetch_changelog(version_tags)
        assert changelog is not None
        assert len(changelog.entries) == 2
        first, second = changelog.entries
        self.validate_initial_entry(first, version_tags[0])
        self.validate_middle_entry(second, version_tags[1], version_tags[0], None)


class TestUpdateChangelogFiles:

    @pytest.fixture
    def semver_config(self, semver_config: SemVerConfig, changelog_file_path):
        semver_config.changelog_files = [SemVerConfig.ChangelogFile(path=changelog_file_path)]
        return semver_config

    class TestUpdateUnsupportedChangelogFile:

        @pytest.fixture
        def changelog_file_path(self):
            return "CHANGELOG.unsupported"

        def test_when_unsupported_changelog_file_format_chosen_then_update_changelog_fails(
            self, api: API, changelog_file_path: str
        ):
            with pytest.raises(UnsupportedChangelogFormat) as excinfo:
                api.update_changelog_files(Changelog())
            assert excinfo.value.path == changelog_file_path

    class TestUpdateChangelogJsonFile:

        @pytest.fixture
        def changelog_file_path(self):
            return "CHANGELOG.json"

        @pytest.fixture(autouse=True)
        def setup(self, api: API, tmpdir_fs: IFileSystemReaderWriter, changelog_file_path: str):
            self.api = api
            self.tmpdir_fs = tmpdir_fs
            self.changelog_json_path = changelog_file_path

        @pytest.mark.parametrize(
            "changelog, expected_json_data",
            [
                (Changelog(), {"entries": []}),
                (
                    Changelog(
                        entries=[
                            ChangelogEntry(
                                version=Version.from_str("0.0.1"),
                                released=datetime.datetime(1999, 1, 1),
                            )
                        ]
                    ),
                    {
                        "entries": [
                            {
                                "released": "1999-01-01T00:00:00",
                                "version": {
                                    "major": 0,
                                    "minor": 0,
                                    "patch": 1,
                                    "prerelease": [],
                                },
                            }
                        ]
                    },
                ),
                (
                    Changelog(
                        entries=[
                            ChangelogEntry(
                                version=Version.from_str("0.0.1"),
                                released=datetime.datetime(1999, 1, 1),
                            ),
                            ChangelogEntry(
                                version=Version.from_str("0.0.2"),
                                prev_version=Version.from_str("0.0.1"),
                                released=datetime.datetime(1999, 1, 2),
                                data=ChangelogEntryData.from_conventional_commit_list(
                                    [
                                        make_dummy_conventional_commit(
                                            "fix: a fix",
                                            rev="abc",
                                            author_date=datetime.datetime(1999, 1, 2),
                                        )
                                    ]
                                ),
                            ),
                        ]
                    ),
                    {
                        "entries": [
                            {
                                "released": "1999-01-01T00:00:00",
                                "version": {
                                    "major": 0,
                                    "minor": 0,
                                    "patch": 1,
                                    "prerelease": [],
                                },
                            },
                            {
                                "released": "1999-01-02T00:00:00",
                                "version": {
                                    "major": 0,
                                    "minor": 0,
                                    "patch": 2,
                                    "prerelease": [],
                                },
                                "prev_version": {
                                    "major": 0,
                                    "minor": 0,
                                    "patch": 1,
                                    "prerelease": [],
                                },
                                "data": {
                                    "feats": [],
                                    "fixes": [
                                        {
                                            "commit": {
                                                "author": "John Doe",
                                                "author_email": "jd@example.com",
                                                "author_date": "1999-01-02T00:00:00",
                                                "message": "fix: a fix",
                                                "rev": "abc",
                                            },
                                            "data": {
                                                "breaking_changes": [],
                                                "description": "a fix",
                                                "footers": {},
                                                "type": "fix",
                                            },
                                        }
                                    ],
                                    "others": {},
                                },
                            },
                        ]
                    },
                ),
            ],
        )
        def test_when_update_changelog_called_then_changelog_file_is_created(
            self, changelog, expected_json_data
        ):
            self.api.update_changelog_files(changelog)
            assert self.tmpdir_fs.exists(self.changelog_json_path)
            assert read_json(self.tmpdir_fs, self.changelog_json_path) == expected_json_data

    class TestUpdateChangelogMarkdownFile:

        @pytest.fixture
        def changelog_file_path(self):
            return "CHANGELOG.md"

        @pytest.fixture(autouse=True)
        def setup(self, api: API, tmpdir_fs: IFileSystemReaderWriter, changelog_file_path: str):
            self.api = api
            self.tmpdir_fs = tmpdir_fs
            self.changelog_markdown_path = changelog_file_path

        @pytest.mark.parametrize(
            "changelog, expected_content",
            [
                (Changelog(), ""),
                (
                    Changelog(
                        entries=[
                            ChangelogEntry(
                                version=Version.from_str("0.0.1"),
                                released=datetime.datetime(1999, 1, 1),
                            )
                        ]
                    ),
                    "## 0.0.1 (1999-01-01)\n\n" "Initial release.\n\n",
                ),
                (
                    Changelog(
                        entries=[
                            ChangelogEntry(
                                version=Version.from_str("0.0.1"),
                                released=datetime.datetime(1999, 1, 1),
                            ),
                            ChangelogEntry(
                                version=Version.from_str("0.0.2"),
                                prev_version=Version.from_str("0.0.1"),
                                released=datetime.datetime(1999, 1, 2),
                                data=ChangelogEntryData.from_conventional_commit_list(
                                    [
                                        make_dummy_conventional_commit("fix: a fix"),
                                        make_dummy_conventional_commit("feat: first feat"),
                                        make_dummy_conventional_commit("feat: second feat"),
                                        make_dummy_conventional_commit("test!: a breaking test"),
                                        make_dummy_conventional_commit(
                                            "chore: spam\n\nBREAKING CHANGE: another breaking change"
                                        ),
                                    ]
                                ),
                            ),
                        ]
                    ),
                    "## 0.0.2 (1999-01-02)\n\n"
                    "### BREAKING CHANGES\n\n"
                    "- a breaking test\n"
                    "- another breaking change\n\n"
                    "### Fix\n\n"
                    "- a fix\n\n"
                    "### Feat\n\n"
                    "- first feat\n"
                    "- second feat\n\n"
                    "## 0.0.1 (1999-01-01)\n\n"
                    "Initial release.\n\n",
                ),
                (
                    Changelog(
                        entries=[
                            ChangelogEntry(
                                version=Version.from_str("0.0.1"),
                                released=datetime.datetime(1999, 1, 1),
                            ),
                            ChangelogEntry(
                                version=Version.from_str("0.0.2"),
                                prev_version=Version.from_str("0.0.1"),
                                released=datetime.datetime(1999, 1, 2),
                            ),
                        ]
                    ),
                    "## 0.0.2 (1999-01-02)\n\n" "## 0.0.1 (1999-01-01)\n\n" "Initial release.\n\n",
                ),
            ],
        )
        def test_update_changelog_file(self, changelog, expected_content):
            self.api.update_changelog_files(changelog)
            content = self.tmpdir_fs.read(self.changelog_markdown_path).decode()
            assert content == expected_content


class TestUpdateVersionFiles:

    @pytest.fixture
    def semver_config(self, semver_config: SemVerConfig, version_file: SemVerConfig.VersionFile):
        semver_config.version_files = [version_file]
        return semver_config

    @pytest.fixture(
        params=[
            ("0.0.1", "1.2.3"),
        ]
    )
    def version_str_tuple(self, request):
        return request.param

    @pytest.fixture
    def version_before_str(self, version_str_tuple: tuple):
        return version_str_tuple[0]

    @pytest.fixture
    def version_after_str(self, version_str_tuple: tuple):
        return version_str_tuple[1]

    @staticmethod
    def run_successful_substitution_test(self, version_before_str: str, version_after_str: str):
        self.tmpdir_fs.write(
            self.version_file_.path,
            self.content_template_.format(version=version_before_str).encode(),
        )
        self.api.update_version_files(Version.from_str(version_after_str))
        content_after = self.tmpdir_fs.read(self.version_file_.path).decode()
        assert self.content_template_.format(version=version_after_str) == content_after

    class TestWithPathOnly:

        @pytest.fixture
        def version_file(self):
            return SemVerConfig.VersionFile(path="project/__init__.py")

        @pytest.fixture(
            params=[
                '__version__ = "{version}"',
                "\n".join(
                    [
                        'foo = "dummy"',
                        "bar = 123",
                        'baz = "{version}"',
                    ]
                ),
                "\n".join(['one = "{version}"', 'two = "0.0.0"']),
            ]
        )
        def content_template(self, request):
            return request.param

        @pytest.fixture(autouse=True)
        def setup(
            self,
            api: API,
            tmpdir_fs: IFileSystemReaderWriter,
            version_file: SemVerConfig.VersionFile,
            content_template: str,
        ):
            self.api = api
            self.tmpdir_fs = tmpdir_fs
            self.version_file_ = version_file
            self.content_template_ = content_template

        def test_substitute_only_first_found_version_string(
            self, version_before_str: str, version_after_str: str
        ):
            TestUpdateVersionFiles.run_successful_substitution_test(
                self, version_before_str, version_after_str
            )

        @pytest.mark.parametrize("content_template", [
            "one = 123\ntwo = 456\nthree = \"spam\""
        ])
        def test_when_no_semver_matching_line_found_then_raise_exception(self, version_after_str: str):
            self.tmpdir_fs.write(
                self.version_file_.path,
                self.content_template_.encode(),
            )
            with pytest.raises(VersionFileNotUpdated) as excinfo:
                self.api.update_version_files(Version.from_str(version_after_str))
            assert excinfo.value.reason == f"no semantic version string found"
            assert excinfo.value.path == self.version_file_.path

    class TestWithPrefixOnly:

        @pytest.fixture
        def version_file(self):
            return SemVerConfig.VersionFile(path="project/__init__.py", prefix="three")

        @pytest.fixture(
            params=[
                "\n".join(
                    [
                        'three = "{version}"',
                        'one = "0.0.0"',
                        'two = "0.0.0"',
                    ]
                ),
                "\n".join(
                    [
                        'one = "0.0.0"',
                        'three = "{version}"',
                        'two = "0.0.0"',
                    ]
                ),
                "\n".join(
                    [
                        'one = "0.0.0"',
                        'two = "0.0.0"',
                        'three = "{version}"',
                    ]
                ),
            ]
        )
        def content_template(self, request):
            return request.param

        @pytest.fixture(autouse=True)
        def setup(
            self,
            api: API,
            tmpdir_fs: IFileSystemReaderWriter,
            version_file: SemVerConfig.VersionFile,
            content_template: str,
        ):
            self.api = api
            self.tmpdir_fs = tmpdir_fs
            self.version_file_ = version_file
            self.content_template_ = content_template

        def test_substitute_only_first_line_with_matching_prefix(
            self, version_before_str: str, version_after_str: str
        ):
            TestUpdateVersionFiles.run_successful_substitution_test(
                self, version_before_str, version_after_str
            )

        @pytest.mark.parametrize("content_template", [
            "one = 123"
        ])
        def test_when_no_prefix_found_then_raise_exception(self, version_after_str: str):
            self.tmpdir_fs.write(
                self.version_file_.path,
                self.content_template_.encode(),
            )
            with pytest.raises(VersionFileNotUpdated) as excinfo:
                self.api.update_version_files(Version.from_str(version_after_str))
            assert excinfo.value.reason == f"line prefix not found: {self.version_file_.prefix}"
            assert excinfo.value.path == self.version_file_.path
