from typing import List

from bumpify.core.api.interface import IInitCommand
from bumpify.core.config.objects import Config
from bumpify.core.console.helpers import prompt_confirm, prompt_enum, prompt_string
from bumpify.core.console.interface import IConsoleInput
from bumpify.core.semver.objects import SemVerConfig, VersionComponent
from bumpify.core.vcs.objects import VCSConfig


class InitProvider(IInitCommand.IInitProvider):

    def __init__(self, cin: IConsoleInput):
        self._cin = cin

    def provide_config(self) -> Config:
        config = Config()
        config.save_section(self._VCSConfigProvider(self._cin).provide())
        if prompt_confirm(self._cin, "Create semantic versioning configuration?", default=True):
            config.save_section(self._SemVerConfigProvider(self._cin).provide())
        return config

    class _SemVerConfigProvider:

        def __init__(self, cin: IConsoleInput):
            self._cin = cin

        def provide(self) -> SemVerConfig:
            return SemVerConfig(
                bump_rules=self._provide_bump_rules(), version_files=self._provide_version_files()
            )

        def _provide_bump_rules(self) -> List[SemVerConfig.BumpRule]:
            out = []
            while True:
                index = len(out) + 1
                out.append(
                    SemVerConfig.BumpRule(
                        branch=prompt_string(
                            self._cin, f"Branch name/pattern for bump rule #{index}"
                        ),
                        when_breaking=prompt_enum(
                            self._cin,
                            "Version component to bump on breaking change",
                            VersionComponent,
                            default=VersionComponent.MAJOR,
                        ),
                        when_feat=prompt_enum(
                            self._cin,
                            "Version component to bump on feature introduction",
                            VersionComponent,
                            default=VersionComponent.MINOR,
                        ),
                        when_fix=prompt_enum(
                            self._cin,
                            "Version component to bump on bug fix",
                            VersionComponent,
                            default=VersionComponent.PATCH,
                        ),
                        prerelease=prompt_string(self._cin, "Prerelease name", optional=True),
                    )
                )
                if not prompt_confirm(self._cin, "Add another bump rule?", default=False):
                    break
            return out

        def _provide_version_files(self) -> List[SemVerConfig.VersionFile]:
            out = []
            while True:
                index = len(out) + 1
                out.append(
                    SemVerConfig.VersionFile(
                        path=prompt_string(self._cin, f"Version file #{index} path"),
                        prefix=prompt_string(
                            self._cin, f"Version file #{index} prefix", optional=True
                        ),
                        section=prompt_string(
                            self._cin, f"Version file #{index} section", optional=True
                        ),
                        encoding=prompt_string(
                            self._cin, f"Version file #{index} encoding", default="utf-8"
                        ),
                    )
                )
                if not prompt_confirm(self._cin, "Add another version file?", default=False):
                    break
            return out

    class _VCSConfigProvider:

        def __init__(self, cin: IConsoleInput):
            self._cin = cin

        def provide(self) -> VCSConfig:
            return VCSConfig(type=self._provide_type())

        def _provide_type(self) -> VCSConfig.Type:
            return prompt_enum(
                self._cin,
                ["Choose project's repository type"],
                VCSConfig.Type,
                default=VCSConfig.Type.AUTO,
            )
