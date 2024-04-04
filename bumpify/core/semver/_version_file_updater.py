import io
import re

from . import _constants
from .exc import VersionFileNotUpdated
from .objects import SemVerConfig, Version


class VersionFileUpdater:
    """State machine based updater for version files.

    :param version_file:
        Version file configuration.

    :param version:
        Version to be written to a file.

    :param out:
        Output buffer where updated file content will be stored.
    """

    def __init__(self, version_file: SemVerConfig.VersionFile, version: Version, out: io.StringIO):
        self._vf = version_file
        self._version = version
        self._out = out
        if self._vf.prefix is not None and self._vf.section is not None:
            self._next_state = self._st_section_lookup
        elif self._vf.prefix is not None:
            self._next_state = self._st_prefix_lookup
        elif self._vf.section is not None:
            self._next_state = self._st_section_lookup
        else:
            self._next_state = self._st_semver_lookup

    def feed(self, line: str):
        """Feed the updater with a next line read from a version file.

        To finalize the state machine, it is required that the last call to
        this method must be performed with empty string as an argument.

        :param line:
            The line from a version file.
        """
        self._next_state = self._next_state(line)

    def _repl(self, m):
        return self._version.to_str()

    def _st_section_lookup(self, line: str):
        if not line:
            raise VersionFileNotUpdated(self._vf.path, f"section not found: {self._vf.section}")
        self._out.write(line)
        if line.strip() == self._vf.section:
            if self._vf.prefix is not None:
                return self._st_prefix_lookup
            return self._st_semver_lookup
        return self._st_section_lookup

    def _st_prefix_lookup(self, line: str):
        if not line:
            raise VersionFileNotUpdated(self._vf.path, f"line prefix not found: {self._vf.prefix}")
        if not line.lstrip().startswith(self._vf.prefix):
            self._out.write(line)
            return self._st_prefix_lookup
        new_line = re.sub(_constants.SEMVER_RE, self._repl, line)
        self._out.write(new_line)
        return self._st_done

    def _st_semver_lookup(self, line: str):
        if not line:
            raise VersionFileNotUpdated(self._vf.path, "no semantic version string found")
        new_line = re.sub(_constants.SEMVER_RE, self._repl, line)
        self._out.write(new_line)
        if new_line != line:
            return self._st_done
        return self._st_semver_lookup

    def _st_done(self, line: str):
        self._out.write(line)
        return self._st_done
