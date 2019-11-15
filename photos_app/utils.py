# coding: utf-8
import enum
from typing import Callable, Any, Optional

from photos_app import logger


class RichEnumTrait(enum.Enum):

    @classmethod
    def has_enum_key(cls, key):
        return key in cls._value2member_map_


def build_to_enum_converter(enum_constructor: RichEnumTrait) -> Callable[[Any], Optional[RichEnumTrait]]:
    def _int(value):
        if enum_constructor.has_enum_key(value):
            return enum_constructor(value)
        else:
            logger.warn('unknown value %r for %s', value, type(enum_constructor))
            return None
    return _int
