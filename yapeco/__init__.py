from typing import Any, Dict, Optional
from os import getenv
from re import compile as compile_regex

builtin_field_re = compile_regex(r"^__[a-z][a-z0-9_]+__$")


class BaseEnvironment:
    """
    Base class for environment-config objects.
    """

    def __init_subclass__(cls) -> None:
        annotations: Dict[str, Any] = cls.__dict__["__annotations__"]
        fields = filter(
            lambda x: builtin_field_re.search(x) == None,
            annotations.keys(),
        )
        for field in fields:
            varname = field.upper()
            varval = getenv(varname)
            default_value = cls.__dict__.get(field, None)
            field_type = annotations[field]
            v = None
            optional = False

            # optional case

            if field_type == Optional[bool]:
                optional = True
                if varval != None:
                    v = varval.lower() != "false" and varval != "0"
            else:
                for typ in [str, int, float]:
                    if field_type == Optional[typ]:
                        optional = True
                        if varval != None:
                            v = typ(varval)
                        break

            if not optional:
                if varval == None:
                    if default_value != None:
                        v = default_value
                    else:
                        raise RuntimeError(
                            f"Failed to load required environment variable {varname}"
                        )
                elif field_type == bool:
                    v = varval.lower() != "false" and varval != "0"
                else:
                    for typ in [str, int, float]:
                        if field_type == typ:
                            v = field_type(varval)
                            break

                if v == None:
                    raise RuntimeError(
                        f"Unsupported type {field_type} for field {field}"
                    )

            setattr(cls, field, v)

    @classmethod
    def refresh(cls) -> None:
        """
        Refresh the environment-config object.
        """
        cls.__init_subclass__()
