import datetime
import hashlib
import uuid

from .objects import Commit, Tag


def make_dummy_rev(seed: str = None) -> str:
    """Make a random commit revision.

    This helper is mostly useful for testing purposes.

    :param seed:
        The seed to use when generating revision.

        For given *seed* there will always be same revision created. If this is
        omitted, then random revision is created.
    """
    if seed is None:
        seed = str(uuid.uuid4())
    return hashlib.sha1(seed.encode()).hexdigest()


def make_dummy_tag(name: str, rev: str = None, created: datetime.datetime = None) -> Tag:
    """Make dummy tag object for testing purposes."""
    return Tag(
        rev=rev or make_dummy_rev(),
        name=name,
        created=created or datetime.datetime.utcnow(),
    )


def make_dummy_commit(
    message: str, rev: str = None, author_date: datetime.datetime = None
) -> Commit:
    """Make dummy commit object.

    Returns new instance of :class:`Commit` object and fills it with dummy
    data. This is meant to be used as a helper for upper layer testing, when
    commit object is needed.

    :param message:
        Commit message.

    :param rev:
        Commit revision.

        Random revision will be used if not given.

    :param author_date:
        Author's date to use.

        Current UTC datetime will be used if not given.
    """
    return Commit(
        rev=rev or make_dummy_rev(),
        author="John Doe",
        author_email="jd@example.com",
        author_date=author_date or datetime.datetime.utcnow(),
        message=message,
    )
