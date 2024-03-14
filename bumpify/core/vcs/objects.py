import datetime
import typing

from pydantic import BaseModel, field_validator


class Commit(BaseModel):
    """Model representing information parsed from a single commit."""

    #: Commit's revision.
    #:
    #: This uniquely identifies a commit within entire repository. For example,
    #: this is SHA1 hash in case of Git commits.
    rev: str

    #: Author's name
    author: str

    #: Author's e-mail address
    author_email: str

    #: Author's date and time.
    #:
    #: This represents time the commit was created by its author. If no
    #: timezone information is present, then this should be interpreted as UTC.
    author_date: datetime.datetime

    #: Commit message
    message: str

    @field_validator("message")
    def _preprocess_message(cls, v: typing.Any):
        return v.strip()


class Tag(BaseModel):
    """Model representing information parsed from a repository tag."""

    #: Revision of a commit that was tagged with this tag.
    rev: str

    #: Commit's name.
    name: str

    #: Tag creation time.
    #:
    #: In case when timezone information is missing this should be interpreted
    #: as UTC.
    created: datetime.datetime

    # TODO: Add support for annotated tags.
