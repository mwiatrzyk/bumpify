import pytest

from mockify.api import ABCMock, satisfied

from bumpify.core.filesystem.interface import IFileSystemReaderWriter
from bumpify.core.notifier.interface import INotifier


@pytest.fixture
def filesystem_reader_writer_mock():
    mock = ABCMock("filesystem_reader_writer_mock", IFileSystemReaderWriter)
    with satisfied(mock):
        yield mock


@pytest.fixture
def notifier_mock():
    mock = ABCMock("notifier_mock", INotifier)
    with satisfied(mock):
        yield mock
