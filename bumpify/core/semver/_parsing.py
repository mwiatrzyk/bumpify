import re
import typing

from . import _constants


class ConventionalCommitParser:
    """State machine based parser for conventional commits."""

    def __init__(self):
        self._next_state = self._st_start
        self._type = None
        self._scope = None
        self._description = None
        self._breaking_changes = []
        self._footer_tags = []
        self._body = []

    def feed(self, line: str) -> bool:
        """Feed the state machine with next commit message line.

        Each line is then processed by the current state of the state
        machine, and then traversal to another state is performed. Return
        ``True`` if *line* was accepted, or ``False`` otherwise.

        :param line:
            Commit message line to feed the parser with.
        """
        next_state = self._next_state(line)
        if next_state is None:
            raise RuntimeError(f"no traversal defined for: {self._next_state.__name__}")
        self._next_state = next_state
        if next_state == self._st_failed:
            return False
        return True

    def output(self) -> typing.Dict[str, str]:
        """Get parsed data."""
        footers = {}
        for tag in self._footer_tags:
            key, value = tag[0], ("\n".join(tag[1:])).strip()
            if self._is_breaking_change_footer(key):
                self._breaking_changes.append(value)
            else:
                footers[key] = value
        return {
            "type": self._type,
            "scope": self._scope,
            "description": self._description,
            "body": ("\n".join(self._body)).strip() or None,
            "breaking_changes": self._breaking_changes,
            "footers": footers,
        }

    def _create_footer(self, m: re.Match):
        key = m.group("breaking_change") or m.group("breaking_change_tag") or m.group("tag")
        value = m.group("value")
        self._footer_tags.append([key, value])

    def _is_breaking_change_footer(self, name: str) -> bool:
        return name == "BREAKING CHANGE" or name == "BREAKING-CHANGE"

    def _st_start(self, line: str):
        return self._st_subject(line)

    def _st_subject(self, line: str):
        match = _constants.CONVENTIONAL_COMMIT_SUBJECT_RE.match(line)
        if match is None:
            return self._st_failed
        self._type = match.group("type")
        self._scope = match.group("scope")
        self._description = match.group("description")
        if match.group("breaking_sign") is not None:
            self._breaking_changes.append(self._description)
        return self._st_subject_body_separator

    def _st_subject_body_separator(self, line: str):
        if line:
            return self._st_failed
        return self._st_body_or_footer

    def _st_body_or_footer(self, line: str):
        match = _constants.CONVENTIONAL_COMMIT_FOOTER_TAG_RE.match(line)
        if not match:
            return self._st_body(line)
        self._create_footer(match)
        return self._st_footer

    def _st_body(self, line: str):
        self._body.append(line)
        if not line:
            return self._st_body_after_blank_line
        return self._st_body

    def _st_body_after_blank_line(self, line: str):
        match = _constants.CONVENTIONAL_COMMIT_FOOTER_TAG_RE.match(line)
        if not match:
            self._body.append(line)
            return self._st_body
        self._create_footer(match)
        return self._st_footer

    def _st_footer(self, line: str):
        match = _constants.CONVENTIONAL_COMMIT_FOOTER_TAG_RE.match(line)
        if not match:
            self._footer_tags[-1].append(line)
            return self._st_footer
        self._create_footer(match)
        return self._st_footer

    def _st_failed(self, line: str):
        return self._st_failed
