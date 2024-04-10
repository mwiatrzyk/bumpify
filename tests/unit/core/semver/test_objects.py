import pytest

from bumpify.core.semver.objects import ConventionalCommitData, Version, VersionComponent


class TestVersion:
    @pytest.mark.parametrize(
        "version_str, expected_version",
        [
            ("1.2.3", Version(major=1, minor=2, patch=3)),
            ("1.2.3-rc", Version(major=1, minor=2, patch=3, prerelease=["rc"])),
            ("1.2.3-rc.123", Version(major=1, minor=2, patch=3, prerelease=["rc", 123])),
            (
                "1.2.3-rc.123+abc",
                Version(major=1, minor=2, patch=3, prerelease=["rc", 123], buildmetadata="abc"),
            ),
            ("1.2.3+abc", Version(major=1, minor=2, patch=3, buildmetadata="abc")),
        ],
    )
    def test_parse_from_string_and_encode_to_string(
        self, version_str: str, expected_version: Version
    ):
        version = Version.from_str(version_str)
        assert version == expected_version
        assert version.to_str() == version_str

    @pytest.mark.parametrize(
        "invalid_version_str",
        [
            "1",
            "1.2",
            "1.2.a",
            "1.2.3-",
            "1.2.3+",
            # ... and so on
        ],
    )
    def test_parsing_an_invalid_version_string_returns_none(self, invalid_version_str: str):
        assert Version.from_str(invalid_version_str) is None

    @pytest.mark.parametrize(
        "left, right",
        [
            ("1.0.0", "2.0.0"),
            ("2.0.0", "2.1.0"),
            ("2.1.0", "2.1.1"),
            ("2.1.1", "2.1.2"),
            ("2.1.2", "2.1.10"),
            ("1.0.0-alpha", "1.0.0"),
            ("1.0.0-alpha", "1.0.0-alpha.1"),
            ("1.0.0-alpha.1", "1.0.0-alpha.beta"),
            ("1.0.0-alpha.beta", "1.0.0-beta"),
            ("1.0.0-beta", "1.0.0-beta.2"),
            ("1.0.0-beta.2", "1.0.0-beta.11"),
            ("1.0.0-beta.11", "1.0.0-rc.1"),
            ("1.0.0-rc.1", "1.0.0"),
        ],
    )
    def test_left_is_lower_than_right(self, left: str, right: str):
        assert Version.from_str(left) < Version.from_str(right)

    @pytest.mark.parametrize(
        "left, right",
        [
            ("1.0.0-alpha.beta", "1.0.0-alpha.1"),
        ],
    )
    def test_left_is_higher_than_right(self, left: str, right: str):
        assert Version.from_str(left) > Version.from_str(right)

    @pytest.mark.parametrize("version_str", ["1.2.3-rc.123"])
    def test_for_two_equal_versions_both_lt_and_gt_return_false(self, version_str: str):
        left = Version.from_str(version_str)
        right = Version.from_str(version_str)
        assert not (left < right)
        assert not (right > left)

    @pytest.mark.parametrize(
        "value, expected_version",
        [
            ("v1.0.0", Version(major=1, minor=0, patch=0)),
            ("ver1.0.0", Version(major=1, minor=0, patch=0)),
            ("version1.0.0spam", Version(major=1, minor=0, patch=0)),
        ],
    )
    def test_extract_from_str(self, value: str, expected_version: Version):
        assert Version.extract_from_str(value) == expected_version

    @pytest.mark.parametrize(
        "version, component, prerelease, expected_result",
        [
            ("1.2.3", VersionComponent.PATCH, None, "1.2.4"),
            ("1.2.4", VersionComponent.MINOR, None, "1.3.0"),
            ("1.3.0", VersionComponent.MAJOR, None, "2.0.0"),
            ("2.0.0", VersionComponent.PATCH, "alpha", "2.0.1-alpha"),
            ("2.0.0", VersionComponent.MINOR, "alpha", "2.1.0-alpha"),
            ("2.0.0", VersionComponent.MAJOR, "alpha", "3.0.0-alpha"),
            ("3.0.0-alpha", VersionComponent.PATCH, "alpha", "3.0.0-alpha.1"),
            ("3.0.0-alpha", VersionComponent.MINOR, "alpha", "3.0.0-alpha.1"),
            ("3.0.0-alpha", VersionComponent.MAJOR, "alpha", "3.0.0-alpha.1"),
            ("3.0.0-alpha.1", VersionComponent.PATCH, "alpha", "3.0.0-alpha.2"),
            ("3.0.0-alpha.1", VersionComponent.MINOR, "alpha", "3.0.0-alpha.2"),
            ("3.0.0-alpha.1", VersionComponent.MAJOR, "alpha", "3.0.0-alpha.2"),
            ("3.0.0-alpha.2", VersionComponent.PATCH, "beta", "3.0.0-beta"),
            ("3.0.0-alpha.2", VersionComponent.MINOR, "beta", "3.0.0-beta"),
            ("3.0.0-alpha.2", VersionComponent.MAJOR, "beta", "3.0.0-beta"),
            ("3.0.0-beta", VersionComponent.PATCH, "beta.rc", "3.0.0-beta.rc"),
            ("3.0.0-beta", VersionComponent.MINOR, "beta.rc", "3.0.0-beta.rc"),
            ("3.0.0-beta", VersionComponent.MAJOR, "beta.rc", "3.0.0-beta.rc"),
            ("3.0.0-beta.rc", VersionComponent.PATCH, "beta.rc", "3.0.0-beta.rc.1"),
            ("3.0.0-beta.rc", VersionComponent.MINOR, "beta.rc", "3.0.0-beta.rc.1"),
            ("3.0.0-beta.rc", VersionComponent.MAJOR, "beta.rc", "3.0.0-beta.rc.1"),
            ("3.0.0-beta.rc.1", VersionComponent.PATCH, "rc", "3.0.0-rc"),
            ("3.0.0-rc", VersionComponent.PATCH, None, "3.0.0"),
            ("3.0.0-rc", VersionComponent.MINOR, None, "3.0.0"),
            ("3.0.0-rc", VersionComponent.MAJOR, None, "3.0.0"),
            ("3.0.0", VersionComponent.PATCH, "alpha", "3.0.1-alpha"),
            ("3.0.1-alpha", VersionComponent.MINOR, "alpha", "3.1.0-alpha"),
            ("3.0.1-alpha.1", VersionComponent.MINOR, "alpha", "3.1.0-alpha"),
            ("3.0.1-alpha.1", VersionComponent.MINOR, "beta", "3.1.0-beta"),
            ("3.0.1-alpha.1", VersionComponent.MINOR, None, "3.1.0"),
            ("3.0.1-alpha", VersionComponent.MAJOR, "alpha", "4.0.0-alpha"),
            ("3.1.0-alpha", VersionComponent.MAJOR, "alpha", "4.0.0-alpha"),
            ("3.1.0-alpha", VersionComponent.MAJOR, "beta", "4.0.0-beta"),
            ("4.0.0-beta", VersionComponent.MAJOR, "beta", "4.0.0-beta.1"),
        ],
    )
    def test_bump(
        self, version: str, component: VersionComponent, prerelease: str, expected_result: str
    ):
        assert (
            Version.from_str(version).bump(component, prerelease=prerelease).to_str()
            == expected_result
        )

    @pytest.mark.parametrize(
        "version, component, prerelease, buildmetadata, expected_result",
        [
            ("1.0.0", VersionComponent.PATCH, None, "abc", "1.0.1+abc"),
            ("1.0.0", VersionComponent.MINOR, None, "abc", "1.1.0+abc"),
            ("1.0.0", VersionComponent.MAJOR, None, "abc", "2.0.0+abc"),
            ("1.0.0-rc", VersionComponent.PATCH, "rc", "abc", "1.0.0-rc.1+abc"),
            ("1.0.0-alpha", VersionComponent.PATCH, "beta", "abc", "1.0.0-beta+abc"),
            ("1.0.1-alpha", VersionComponent.MINOR, "alpha", "abc", "1.1.0-alpha+abc"),
            ("1.0.1-alpha", VersionComponent.MAJOR, "alpha", "abc", "2.0.0-alpha+abc"),
        ],
    )
    def test_when_bumping_with_metadata_that_metadata_is_added_to_created_version(
        self,
        version: str,
        component: VersionComponent,
        prerelease: str,
        buildmetadata: str,
        expected_result: str,
    ):
        assert (
            Version.from_str(version)
            .bump(component, prerelease=prerelease, buildmetadata=buildmetadata)
            .to_str()
            == expected_result
        )


class TestConventionalCommitData:
    @pytest.mark.parametrize(
        "message, expected_conventional_commit_data",
        [
            (
                "fix: a fix",
                ConventionalCommitData(type="fix", description="a fix"),
            ),
            (
                "fix!: a breaking fix",
                ConventionalCommitData(
                    type="fix",
                    description="a breaking fix",
                    breaking_changes=["a breaking fix"],
                ),
            ),
            (
                "feat(foo): a feat with scope",
                ConventionalCommitData(type="feat", description="a feat with scope", scope="foo"),
            ),
            (
                "feat(foo)!: a breaking feat with scope",
                ConventionalCommitData(
                    type="feat",
                    description="a breaking feat with scope",
                    scope="foo",
                    breaking_changes=["a breaking feat with scope"],
                ),
            ),
            (
                "fix: a fix with body\n\nthe body of the fix",
                ConventionalCommitData(
                    type="fix",
                    description="a fix with body",
                    body="the body of the fix",
                ),
            ),
            (
                "fix: a fix with multiline body\n\none\ntwo\n\nthree\nfour",
                ConventionalCommitData(
                    type="fix",
                    description="a fix with multiline body",
                    body="one\ntwo\n\nthree\nfour",
                ),
            ),
            (
                "fix: a fix with breaking change footer\n\nBREAKING CHANGE: a breaking change info",
                ConventionalCommitData(
                    type="fix",
                    description="a fix with breaking change footer",
                    breaking_changes=["a breaking change info"],
                ),
            ),
            (
                "fix: a fix with breaking change tag\n\nBREAKING-CHANGE: a breaking change info",
                ConventionalCommitData(
                    type="fix",
                    description="a fix with breaking change tag",
                    breaking_changes=["a breaking change info"],
                ),
            ),
            (
                "fix: a fix with multiline breaking change footer\n\nBREAKING CHANGE: first\nsecond\nthird",
                ConventionalCommitData(
                    type="fix",
                    description="a fix with multiline breaking change footer",
                    breaking_changes=["first\nsecond\nthird"],
                ),
            ),
            (
                "fix: a fix with multiline breaking change footer ending with LF\n\nBREAKING CHANGE: first\nsecond\nthird\n\n",
                ConventionalCommitData(
                    type="fix",
                    description="a fix with multiline breaking change footer ending with LF",
                    breaking_changes=["first\nsecond\nthird"],
                ),
            ),
            (
                "fix: a fix with two breaking change footers\n\nBREAKING CHANGE: first\nBREAKING CHANGE: second",
                ConventionalCommitData(
                    type="fix",
                    description="a fix with two breaking change footers",
                    breaking_changes=["first", "second"],
                ),
            ),
            (
                "fix: a fix with two breaking change footers separated with double LF\n\nBREAKING CHANGE: first\n\nBREAKING CHANGE: second",
                ConventionalCommitData(
                    type="fix",
                    description="a fix with two breaking change footers separated with double LF",
                    breaking_changes=["first", "second"],
                ),
            ),
            (
                "fix: a fix with one word footer and no body\n\nFix: 123",
                ConventionalCommitData(
                    type="fix",
                    description="a fix with one word footer and no body",
                    footers={"Fix": "123"},
                ),
            ),
            (
                "fix: a fix with two word footer and no body\n\nFixed-by: Johnny",
                ConventionalCommitData(
                    type="fix",
                    description="a fix with two word footer and no body",
                    footers={"Fixed-by": "Johnny"},
                ),
            ),
            (
                "fix: a fix with three word footer and no body\n\nReview-made-by: Johnny",
                ConventionalCommitData(
                    type="fix",
                    description="a fix with three word footer and no body",
                    footers={"Review-made-by": "Johnny"},
                ),
            ),
            (
                "fix: a fix with two footers and no body\n\nfoo: 1\nbar: 2",
                ConventionalCommitData(
                    type="fix",
                    description="a fix with two footers and no body",
                    footers={"foo": "1", "bar": "2"},
                ),
            ),
            (
                "fix: a fix with two footers after body\n\nthis is a body\n\nfoo: 1\nbar: 2",
                ConventionalCommitData(
                    type="fix",
                    description="a fix with two footers after body",
                    body="this is a body",
                    footers={"foo": "1", "bar": "2"},
                ),
            ),
        ],
    )
    def test_parse_commit_message_into_conventional_commit_data_object(
        self,
        message: str,
        expected_conventional_commit_data: ConventionalCommitData,
    ):
        assert (
            ConventionalCommitData.from_commit_message(message) == expected_conventional_commit_data
        )

    @pytest.mark.parametrize(
        "message, expected_conventional_commit_data",
        [
            (
                "chore: dummy change\n\ntag with no dash: value",
                ConventionalCommitData(
                    type="chore",
                    description="dummy change",
                    body="tag with no dash: value",
                ),
            ),
        ],
    )
    def test_when_commit_footer_tag_has_incorrect_format_then_it_becomes_part_of_a_body(
        self,
        message: str,
        expected_conventional_commit_data: ConventionalCommitData,
    ):
        assert (
            ConventionalCommitData.from_commit_message(message) == expected_conventional_commit_data
        )

    @pytest.mark.parametrize(
        "invalid_message",
        [
            "no type given",
            "fix: foo\nbody",
        ],
    )
    def test_when_commit_message_is_invalid_then_none_is_returned(self, invalid_message: str):
        assert ConventionalCommitData.from_commit_message(invalid_message) is None
