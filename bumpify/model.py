"""Adapters for Modelity."""

from modelity.api import Model as _BaseModel
from modelity.api import dump, field_preprocessor, validate


class Model(_BaseModel):
    """Common base class for all models.

    Added to allow easy way of providing common hooks for models.
    """

    @field_preprocessor()
    def _decode_bytes(value):
        if not isinstance(value, bytes):
            return value
        return value.decode()  # utf-8 assumed


def dump_valid(model: Model, **kwargs) -> dict:
    """Validate model and dump it to dict.

    :param model:
        The model to dump.
    """
    validate(model)
    return dump(model, **kwargs)
