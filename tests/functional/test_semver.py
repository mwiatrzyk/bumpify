import pytest
from mockify.api import Return

from bumpify.core.semver.implementation import SemVerApi
from bumpify.core.semver.interface import ISemVerApi
from bumpify.core.semver.objects import ConventionalCommitData, Version
from bumpify.core.vcs.helpers import make_dummy_rev, make_dummy_tag, make_dummy_commit

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

    @pytest.mark.parametrize('start_rev', [None, make_dummy_rev()])
    @pytest.mark.parametrize('end_rev', [None, make_dummy_rev()])
    def test_when_no_conventional_commits_found_then_empty_list_is_returned(self, start_rev, end_rev):
        commits = [make_dummy_commit('non conventional change')]
        self.vcs_reader_writer_mock.list_commits.expect_call(start_rev=start_rev, end_rev=end_rev).will_once(Return(commits))
        conventional_commits = self.api.list_conventional_commits(start_rev, end_rev)
        assert conventional_commits == []

    @pytest.mark.parametrize('message, expected_conventional_commit_data', [
        ('fix: a fix', ConventionalCommitData(type='fix', description='a fix')),
    ])
    def test_parse_conventional_commit(self, message, expected_conventional_commit_data):
        commits = [make_dummy_commit(message)]
        self.vcs_reader_writer_mock.list_commits.expect_call(start_rev=None, end_rev=None).will_once(Return(commits))
        conventional_commits = self.api.list_conventional_commits()
        assert len(conventional_commits) == 1
        assert conventional_commits[0].commit == commits[0]
        assert conventional_commits[0].data == expected_conventional_commit_data
