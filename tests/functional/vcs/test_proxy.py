import pytest
from mockify.api import Return

from bumpify.core.notifier.objects import Styled
from bumpify.core.vcs.helpers import make_dummy_rev
from bumpify.core.vcs.implementation.proxy import DryRunVcsReaderWriterProxy
from bumpify.core.vcs.interface import IVcsReaderWriter


@pytest.fixture
def sut(vcs_reader_writer_mock, status_listener_mock):
    return DryRunVcsReaderWriterProxy(vcs_reader_writer_mock, status_listener_mock)


class TestDryRunVcsReaderWriterProxy:
    SUT = IVcsReaderWriter

    @pytest.fixture(autouse=True)
    def setup(self, sut: SUT, vcs_reader_writer_mock, status_listener_mock):
        self.vcs_reader_writer_mock = vcs_reader_writer_mock
        self.status_listener_mock = status_listener_mock
        self.sut = sut

    def test_when_query_method_called_then_forward_call_to_target(self):
        rev = make_dummy_rev()
        self.vcs_reader_writer_mock.find_initial_rev.expect_call().will_once(Return(rev))
        assert self.sut.find_initial_rev() == rev

    @pytest.mark.parametrize(
        "paths",
        [
            ("foo.txt", "bar.txt", "bar/spam.txt"),
        ],
    )
    def test_add(self, paths):
        for path in paths:
            self.status_listener_mock.info.expect_call(
                "Would",
                Styled("add", bold=True),
                "following file to the next commit:",
                Styled(path, bold=True),
            )
        self.sut.add(*paths)

    @pytest.mark.parametrize("branch", ["dummy"])
    def test_branch(self, branch):
        rev = make_dummy_rev()
        self.vcs_reader_writer_mock.find_head_rev.expect_call().will_once(Return(rev))
        self.status_listener_mock.info.expect_call(
            "Would",
            Styled("create", bold=True),
            "a branch named",
            Styled(branch, bold=True),
            "at",
            Styled(rev, bold=True),
        )
        self.sut.branch(branch)

    @pytest.mark.parametrize("rev_or_name", [make_dummy_rev(), "v1.2.3", "dummy"])
    def test_checkout(self, rev_or_name):
        self.status_listener_mock.info.expect_call(
            "Would", Styled("checkout", bold=True), "HEAD at", Styled(rev_or_name, bold=True)
        )
        self.sut.checkout(rev_or_name)

    @pytest.mark.parametrize(
        "rev, message",
        [
            (make_dummy_rev("fix: a fix"), "fix: a fix"),
        ],
    )
    def test_commit(self, rev, message):
        self.status_listener_mock.info.expect_call(
            "Would create a",
            Styled("commit", bold=True),
            "with message",
            Styled(message, bold=True),
            "and return",
            Styled(rev, bold=True),
        )
        assert self.sut.commit(message) == rev

    @pytest.mark.parametrize(
        "rev, name",
        [
            (make_dummy_rev(), "v1.2.3"),
        ],
    )
    def test_tag(self, rev, name):
        self.status_listener_mock.info.expect_call(
            "Would create a",
            Styled("tag", bold=True),
            "named",
            Styled(name, bold=True),
            "at",
            Styled(rev, bold=True),
        )
        self.sut.tag(rev, name)
