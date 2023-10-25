from typing import List
from os import getenv
from re import compile as compile_regex

builtin_field_re = compile_regex(r"^__[a-z][a-z0-9_]+__$")


class BaseEnvironment:
    """
    Base class for config objects.
    """

    def __init_subclass__(cls) -> None:
        annotations = cls.__dict__["__annotations__"]
        fields: List[str] = filter(
            lambda x: builtin_field_re.search(x) == None,
            annotations.keys(),
        )
        for field in fields:
            varname = field.upper()
            varval = getenv(varname)
            if not varval:
                raise RuntimeError(
                    f"Failed to load required environment variable {varname}"
                )
            field_type = annotations[field]
            if field_type == bool:
                v = varval.lower() != "false" and varval != "0"
            else:
                v = field_type(varval)
            setattr(cls, field, v)
