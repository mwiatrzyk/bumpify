import os
import random
import typing

import pytest
from mockify.api import Return, _

from bumpify.core.filesystem import exc as fs_exc
from bumpify.core.filesystem.implementation import (
    DryRunFileSystemReaderWriterProxy,
    FileSystemReaderWriter,
)
from bumpify.core.filesystem.interface import IFileSystemReaderWriter
from bumpify.core.status.objects import Styled


@pytest.fixture(
    params=[
        ("foo.txt", "foo.txt", b"content of foo.txt"),
        ("foo/bar/baz.txt", "foo/bar/baz.txt", b"content of baz.txt"),
        ("/spam.txt", "spam.txt", b"content of spam.txt"),
    ]
)
def data(request):
    return request.param


@pytest.fixture
def path(data):
    return data[0]


@pytest.fixture
def normalized_path(data):
    return data[1]


@pytest.fixture
def payload(data):
    return data[2]


@pytest.fixture(
    params=[
        "foo/../bar.txt",
        "foo/./baz.txt",
        "foo/./baz.txt",
        "./baz.txt",
        "../baz.txt",
    ]
)
def relative_path(request):
    return request.param


class TestFileSystemReaderWriter:
    SUT = IFileSystemReaderWriter

    @pytest.fixture
    def sut(self, tmpdir):
        return FileSystemReaderWriter(tmpdir)

    def test_return_absolute_path_to_a_file_and_check_if_the_file_exists(
        self, sut: SUT, path, payload
    ):
        abspath = sut.abspath(path)
        assert not os.path.exists(abspath)
        sut.write(path, payload)
        assert os.path.exists(abspath)

    def test_write_file_and_read_it_back(self, sut: SUT, path: str, payload: bytes):
        sut.write(path, payload)
        assert sut.read(path) == payload

    def test_write_fails_if_relative_path_is_used(
        self, sut: SUT, relative_path: str, payload: bytes
    ):
        with pytest.raises(fs_exc.RelativePathUsed) as excinfo:
            sut.write(relative_path, payload)
        assert excinfo.value.path == relative_path

    def test_read_fails_if_relative_path_is_used(self, sut: SUT, relative_path: str):
        with pytest.raises(fs_exc.RelativePathUsed) as excinfo:
            sut.read(relative_path)
        assert excinfo.value.path == relative_path

    def test_exists_fails_if_relative_path_is_used(self, sut: SUT, relative_path: str):
        with pytest.raises(fs_exc.RelativePathUsed) as excinfo:
            sut.exists(relative_path)
        assert excinfo.value.path == relative_path

    def test_exists_returns_false_if_file_does_not_exist_or_true_otherwise(
        self, sut: SUT, path: str, payload: bytes
    ):
        assert not sut.exists(path)
        sut.write(path, payload)
        assert sut.exists(path)

    def test_after_file_is_written_modified_paths_contains_path_of_written_file(
        self, sut: SUT, path: str, normalized_path: str, payload: bytes
    ):
        assert sut.modified_paths() == set()
        sut.write(path, payload)
        assert sut.modified_paths() == {normalized_path}

    def test_when_clear_modified_paths_called_then_set_of_modified_paths_is_cleared(
        self, sut: SUT, path, payload, normalized_path
    ):
        assert sut.modified_paths() == set()
        sut.write(path, payload)
        assert sut.modified_paths() == {normalized_path}
        sut.clear_modified_paths()
        assert sut.modified_paths() == set()

    def test_scan_returns_normalized_created_file_path(
        self, sut: SUT, path: str, normalized_path: str, payload: bytes
    ):
        sut.write(path, payload)
        assert set(sut.scan()) == {normalized_path}

    @pytest.mark.parametrize(
        "paths, exclude, expected_result",
        [
            (["foo.txt"], {"foo.txt"}, set()),
            (["foo.txt", "bar.txt"], {"/foo.txt"}, {"bar.txt"}),
            (["foo.txt", "bar.txt"], {"bar.txt"}, {"foo.txt"}),
            (["/foo.txt"], {"foo.txt"}, set()),
        ],
    )
    def test_when_exclude_given_then_scan_ignores_excluded_paths(
        self,
        sut: SUT,
        paths: typing.List[str],
        exclude: typing.Set[str],
        expected_result: typing.Set[str],
    ):
        for path in paths:
            sut.write(path, b"dummy content")
        assert set(sut.scan(exclude=exclude)) == expected_result


class TestDryRunFileSystemReaderWriterProxy:
    SUT = IFileSystemReaderWriter

    @pytest.fixture
    def sut(self, filesystem_reader_writer_mock, status_listener_mock):
        return DryRunFileSystemReaderWriterProxy(
            filesystem_reader_writer_mock, status_listener_mock
        )

    @pytest.fixture(autouse=True)
    def setup(self, filesystem_reader_writer_mock, status_listener_mock):
        self.target_mock = filesystem_reader_writer_mock
        self.notifier_mock = status_listener_mock

    @pytest.mark.parametrize(
        "args, result",
        [
            ("dummy.txt", True),
        ],
    )
    def test_when_reader_interface_method_called_then_call_is_forwarded_to_target(
        self, sut: SUT, args, result
    ):
        self.target_mock.exists.expect_call(args).will_once(Return(result))
        assert sut.exists(args) is result

    @pytest.mark.parametrize(
        "path, exists, payload, expected_message",
        [
            (
                "dummy.txt",
                True,
                b"spam",
                (
                    "Would",
                    Styled("overwrite", bold=True),
                    "file at",
                    Styled("dummy.txt", bold=True),
                    "and set it with following content:\n",
                    Styled("  spam", fg="blue"),
                ),
            ),
            (
                "dummy.txt",
                False,
                b"spam\nmore spam",
                (
                    "Would",
                    Styled("create", bold=True),
                    "file at",
                    Styled("dummy.txt", bold=True),
                    "and set it with following content:\n",
                    Styled("  spam\n  more spam", fg="blue"),
                ),
            ),
            (
                "dummy.txt",
                True,
                random.randbytes(128),
                (
                    "Would",
                    Styled("overwrite", bold=True),
                    "file at",
                    Styled("dummy.txt", bold=True),
                    "and set it with content having",
                    Styled("128 bytes", bold=True),
                    "in total",
                ),
            ),
            (
                "dummy.txt",
                False,
                random.randbytes(64),
                (
                    "Would",
                    Styled("create", bold=True),
                    "file at",
                    Styled("dummy.txt", bold=True),
                    "and set it with content having",
                    Styled("64 bytes", bold=True),
                    "in total",
                ),
            ),
        ],
    )
    def test_write(self, sut: SUT, path, exists, payload, expected_message):
        self.target_mock.exists.expect_call(path).will_once(Return(exists))
        self.notifier_mock.info.expect_call(*expected_message)
        sut.write(path, payload)

    def test_when_write_called_then_path_is_added_to_modified_paths(
        self, sut: SUT, path, normalized_path
    ):
        self.target_mock.exists.expect_call(path).will_once(Return(True))
        self.notifier_mock.info.expect_call(_, _, _, _, _, _)
        assert sut.modified_paths() == set()
        sut.write(path, b"content")
        assert sut.modified_paths() == {normalized_path}

    def test_clear_modified_paths(self, sut: SUT, path, normalized_path):
        self.target_mock.exists.expect_call(path).will_once(Return(True))
        self.notifier_mock.info.expect_call(_, _, _, _, _, _)
        assert sut.modified_paths() == set()
        sut.write(path, b"content")
        assert sut.modified_paths() == {normalized_path}
        sut.clear_modified_paths()
        assert sut.modified_paths() == set()
