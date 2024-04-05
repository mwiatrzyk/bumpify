from typing import List
from bumpify.core.api.interface import IInitCommand
from bumpify.core.config.objects import Config, VCSConfig
from bumpify.core.prompt.interface import IPrompt
from bumpify.core.semver.objects import SemVerConfig


class InitProvider(IInitCommand.IInitProvider):

    def __init__(self, prompt: IPrompt):
        self._prompt = prompt

    def provide_config(self) -> Config:
        config = Config(vcs=self._VCSConfigProvider(self._prompt).provide())
        if self._prompt.confirm("Create semantic versioning configuration?"):
            config.save_module_config(self._SemVerConfigProvider(self._prompt).provide())
        return config

    class _SemVerConfigProvider:

        def __init__(self, prompt: IPrompt):
            self._prompt = prompt

        def provide(self) -> SemVerConfig:
            return SemVerConfig(
                version_files=self._provide_version_files()
            )

        def _provide_version_files(self) -> List[SemVerConfig.VersionFile]:
            out = []
            while True:
                index = len(out) + 1
                out.append(SemVerConfig.VersionFile(
                    path=self._prompt.path(f"Version file #{index} path"),
                    prefix=self._prompt.string(f"Version file #{index} prefix", optional=True),
                    section=self._prompt.string(f"Version file #{index} section", optional=True),
                    encoding=self._prompt.string(f"Version file #{index} encoding", default="utf-8"),
                ))
                if not self._prompt.confirm(f"Add another version file?"):
                    break
            return out

    class _VCSConfigProvider:

        def __init__(self, prompt: IPrompt):
            self._prompt = prompt

        def provide(self) -> VCSConfig:
            return VCSConfig(
                type=self._provide_type()
            )

        def _provide_type(self) -> VCSConfig.Type:
            return self._prompt.enum("Choose project's repository type", VCSConfig.Type)
