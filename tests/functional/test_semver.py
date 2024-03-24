import pytest
from mockify.api import Return

from bumpify.core.semver.implementation import SemVerApi
from bumpify.core.semver.interface import ISemVerApi
from bumpify.core.semver.objects import Version
from bumpify.core.vcs.helpers import make_dummy_tag

API = ISemVerApi


class TestListMergedVersionTags:

    @pytest.fixture(autouse=True)
    def setup(self, vcs_reader_writer_mock):
        self.api = SemVerApi(vcs_reader_writer_mock)
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
