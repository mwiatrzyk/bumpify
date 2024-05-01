import textwrap
from typing import Dict, Optional

import pytest
from mockify.api import FunctionMock, Return, satisfied

from bumpify.core.config.objects import LoadedConfig
from bumpify.core.filesystem.interface import IFileSystemReaderWriter
from bumpify.core.hook.exc import HookExecFailed
from bumpify.core.hook.implementation import HookApiLoader
from bumpify.core.hook.interface import IHookApiLoader
from bumpify.core.hook.objects import HookConfig

SUT = IHookApiLoader


def make_add_hook() -> str:
    return textwrap.dedent(
        """
    from bumpify.core.hook.decorators import hook

    @hook("add")
    def add(a, b):
        return a + b
    """
    )


def make_sub_hook() -> str:
    return textwrap.dedent(
        """
    from bumpify.core.hook.decorators import hook

    @hook("sub")
    def sub(a, b):
        return a - b
    """
    )


class TestLoadHook:

    @pytest.fixture
    def loaded_config(self, loaded_config: LoadedConfig, hook_config: Optional[HookConfig]):
        if hook_config is not None:
            loaded_config.config.save_section(hook_config)
        return loaded_config

    @pytest.fixture
    def sut(self, loaded_config, tmpdir_fs):
        return HookApiLoader(loaded_config, tmpdir_fs)

    @pytest.fixture
    def default_func_mock(self):
        mock = FunctionMock("default_func")
        with satisfied(mock):
            yield mock

    @pytest.mark.parametrize("hook_config", [None])
    def test_when_hooks_are_not_configured_then_default_hook_api_object_is_returned(
        self, sut: SUT, default_func_mock
    ):
        api = sut.load()
        assert api.loaded_hook_names() == set()
        default_func_mock.expect_call(2, 3).will_once(Return(5))
        assert api.get_hook("add", default_func_mock).invoke(2, 3) == 5

    @pytest.mark.parametrize("hook_config", [HookConfig(paths=["hook.py"])])
    @pytest.mark.parametrize(
        "hook_file_payload",
        [
            {"hook.py": make_add_hook()},
        ],
    )
    def test_when_hook_files_are_found_and_needed_hook_is_found_then_use_that_hook(
        self,
        sut: SUT,
        hook_config: HookConfig,
        tmpdir_fs: IFileSystemReaderWriter,
        hook_file_payload: Dict[str, str],
        default_func_mock,
    ):
        for path in hook_config.paths:
            tmpdir_fs.write(path, hook_file_payload[path].encode())
        api = sut.load()
        assert api.loaded_hook_names() == {"add"}
        default_func_mock.expect_call(2, 3).times(0)
        assert api.get_hook("add", default_func_mock).invoke(2, 3) == 5

    @pytest.mark.parametrize("hook_config", [HookConfig(paths=["add.py", "sub.py"])])
    @pytest.mark.parametrize(
        "hook_file_payload",
        [
            {"add.py": make_add_hook(), "sub.py": make_sub_hook()},
        ],
    )
    def test_load_two_hooks_from_two_different_hook_files(
        self,
        sut: SUT,
        hook_config: HookConfig,
        tmpdir_fs: IFileSystemReaderWriter,
        hook_file_payload: Dict[str, str],
        default_func_mock,
    ):
        for path in hook_config.paths:
            tmpdir_fs.write(path, hook_file_payload[path].encode())
        api = sut.load()
        assert api.loaded_hook_names() == {"add", "sub"}
        default_func_mock.expect_call(2, 3).times(0)
        assert api.get_hook("add", default_func_mock).invoke(2, 3) == 5
        assert api.get_hook("sub", default_func_mock).invoke(2, 3) == -1

    @pytest.mark.parametrize("hook_config", [HookConfig(paths=["hook.py"])])
    @pytest.mark.parametrize(
        "hook_file_payload",
        [
            {"hook.py": ""},
        ],
    )
    def test_when_hook_files_are_found_and_needed_hook_is_not_found_then_use_default_hook(
        self,
        sut: SUT,
        hook_config: HookConfig,
        tmpdir_fs: IFileSystemReaderWriter,
        hook_file_payload: Dict[str, str],
        default_func_mock,
    ):
        for path in hook_config.paths:
            tmpdir_fs.write(path, hook_file_payload[path].encode())
        api = sut.load()
        assert api.loaded_hook_names() == set()
        default_func_mock.expect_call(2, 3).will_once(Return(5))
        assert api.get_hook("add", default_func_mock).invoke(2, 3) == 5

    @pytest.mark.parametrize("hook_config", [HookConfig(paths=["hook.py"])])
    @pytest.mark.parametrize(
        "hook_file_payload",
        [
            {"hook.py": "not a Python code"},
        ],
    )
    def test_loading_hook_fails_if_hook_file_does_not_contain_valid_python_code(
        self,
        sut: SUT,
        hook_config: HookConfig,
        tmpdir_fs: IFileSystemReaderWriter,
        hook_file_payload: Dict[str, str],
    ):
        for path in hook_config.paths:
            tmpdir_fs.write(path, hook_file_payload[path].encode())
        with pytest.raises(HookExecFailed) as excinfo:
            sut.load()
        assert excinfo.value.abspath == tmpdir_fs.abspath("hook.py")
        assert excinfo.value.original_exc.__class__ is SyntaxError
        assert "not a Python code" in excinfo.value.traceback

    @pytest.mark.parametrize("hook_config", [HookConfig(paths=["hook.py"])])
    @pytest.mark.parametrize(
        "hook_file_payload",
        [
            {
                "hook.py": textwrap.dedent(
                    """
                import random
                from bumpify.core.hook.decorators import hook

                @hook("dummy")
                def dummy(a, b):
                    return random.randint(a, b)
                """
                )
            },
        ],
    )
    def test_when_hook_uses_imports_those_imports_are_automatically_propagated(
        self,
        sut: SUT,
        hook_config: HookConfig,
        tmpdir_fs: IFileSystemReaderWriter,
        hook_file_payload: Dict[str, str],
        default_func_mock,
    ):
        for path in hook_config.paths:
            tmpdir_fs.write(path, hook_file_payload[path].encode())
        api = sut.load()
        default_func_mock.expect_call(0, 255).times(0)
        assert 0 <= api.get_hook("dummy", default_func_mock).invoke(0, 255) <= 255

    @pytest.mark.parametrize("hook_config", [HookConfig(paths=["hook.py"])])
    @pytest.mark.parametrize(
        "hook_file_payload",
        [
            {
                "hook.py": textwrap.dedent(
                    """
                import random
                from bumpify.core.hook.decorators import hook

                @hook("bar")
                def foo(a, b):
                    return random.randint(a, b)
                """
                )
            },
        ],
    )
    def test_use_hook_name_that_is_different_from_decorated_functions_name(
        self,
        sut: SUT,
        hook_config: HookConfig,
        tmpdir_fs: IFileSystemReaderWriter,
        hook_file_payload: Dict[str, str],
        default_func_mock,
    ):
        for path in hook_config.paths:
            tmpdir_fs.write(path, hook_file_payload[path].encode())
        api = sut.load()
        default_func_mock.expect_call(0, 255).times(0)
        assert 0 <= api.get_hook("bar", default_func_mock).invoke(0, 255) <= 255
