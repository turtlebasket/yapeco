import json
import yapeco as y
from yapeco import BaseEnvironment as Env
from typing import List, Optional, TYPE_CHECKING
from os import environ
from enum import Enum, unique

if TYPE_CHECKING:
    try:
        from typing import Literal
    except ImportError:
        from typing_extensions import Literal
else:
    try:
        from typing import Literal
    except ImportError:
        try:
            from typing_extensions import Literal
        except ImportError:
            Literal = None

MIN_FLOAT_DIFF = 0.0000000001


@unique
class EnvMode(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


def test_config_primitive_types() -> None:
    environ.clear()

    environ["A"] = "1"
    environ["B"] = "2"
    environ["C"] = "3"
    environ["D"] = "False"
    environ["E"] = "false"
    environ["F"] = "0"
    environ["G"] = "True"
    environ["H"] = "true"
    environ["I"] = "1"
    environ["J"] = "abc"

    class Config(Env):
        a: int
        b: str
        c: float
        d: bool
        e: bool
        f: bool
        g: bool
        h: bool
        i: bool
        j: bool

    assert Config.a == 1, "int not parsed correctly"
    assert Config.b == "2", "str not parsed correctly"
    assert Config.c - 3.0 < MIN_FLOAT_DIFF, "float not parsed correctly"
    assert not Config.d, "bool not parsed correctly"
    assert not Config.e, "bool not parsed correctly"
    assert not Config.f, "bool not parsed correctly"
    assert Config.g, "bool not parsed correctly"
    assert Config.h, "bool not parsed correctly"
    assert Config.i, "bool not parsed correctly"
    assert Config.j, "bool not parsed correctly"


def test_config_objects() -> None:
    environ.clear()
    environ["A"] = "{}"
    environ["B"] = '{"a": 1, "b": "2", "c": 3.14, "d": false, "e": true, "f": 0}'

    class Config(Env):
        a: y.JsonObject
        b: y.JsonObject

    assert Config.a == {}, "Empty JSON object not parsed correctly"
    assert Config.b == {
        "a": 1,
        "b": "2",
        "c": 3.14,
        "d": False,
        "e": True,
        "f": 0,
    }, "JSON object not parsed correctly"


def test_config_lists() -> None:
    environ.clear()
    environ["A"] = "1, 2, 3"
    environ["B"] = "1,2,3"
    environ["C"] = "1, '2', 3"
    environ["D"] = "1.1, 2.2, 3.3"

    class Config(Env):
        a: List[int]
        b: List[int]
        c: List[str]
        d: List[float]

    assert Config.a == [1, 2, 3], "List[int] with spaces not parsed correctly"
    assert Config.b == [1, 2, 3], "List[int] without spaces not parsed correctly"
    assert Config.c == ["1", "'2'", "3"], "List[str] not parsed correctly"
    assert Config.d == [1.1, 2.2, 3.3], "List[float] not parsed correctly"


def test_config_optional_types() -> None:
    environ.clear()

    environ["A"] = "1"
    environ["B"] = "2"
    environ["C"] = "3"
    environ["D"] = "False"
    environ["E"] = "false"
    environ["F"] = "0"
    environ["G"] = "True"
    environ["H"] = "true"
    environ["I"] = "1"
    environ["J"] = "abc"
    environ["K"] = "abc"

    environ["M"] = '{"a": 1, "b": "2", "c": 3.14, "d": false, "e": true, "f": 0}'
    environ["N"] = ""  # None
    environ["O"] = "1"
    environ["P"] = "1, 2,3, 4,5"
    environ["Q"] = ""
    environ["R"] = "abc"
    environ["S"] = "abc, def,ghi"
    environ["T"] = ""  # None

    class Config(Env):
        a: Optional[int]
        b: Optional[str]
        c: Optional[float]
        d: Optional[bool]
        e: Optional[bool]
        f: Optional[bool]
        g: Optional[bool]
        h: Optional[bool]
        i: Optional[bool]
        j: Optional[bool]
        k: Optional[str]
        l: Optional[str]  # will have no value
        m: Optional[y.JsonObject]
        n: Optional[y.JsonObject]
        o: Optional[List[int]]  # one item
        p: Optional[List[int]]  # multiple items
        q: Optional[List[int]]  # no items
        r: Optional[List[str]]  # one item
        s: Optional[List[str]]  # multiple items
        t: Optional[List[str]]  # no items

    # same tests as before
    assert Config.a == 1, "Optional int not parsed correctly"
    assert Config.b == "2", "Optional str not parsed correctly"
    assert (
        Config.c != None and Config.c - 3.0 < MIN_FLOAT_DIFF
    ), "Optional float not parsed correctly"
    assert not Config.d, "Optional bool not parsed correctly"
    assert not Config.e, "Optional bool not parsed correctly"
    assert not Config.f, "Optional bool not parsed correctly"
    assert Config.g, "Optional bool not parsed correctly"
    assert Config.h, "Optional bool not parsed correctly"
    assert Config.i, "Optional bool not parsed correctly"
    assert Config.j, "Optional bool not parsed correctly"
    assert Config.k == "abc", "str not parsed correctly"
    assert Config.l == None, "Optional JSON object not parsed correctly"
    assert Config.m == {
        "a": 1,
        "b": "2",
        "c": 3.14,
        "d": False,
        "e": True,
        "f": 0,
    }, "JSON object not parsed correctly"
    assert Config.n == None, "Optional JSON object not parsed correctly"
    assert Config.o == [1], "Optional List[int] not parsed correctly"
    assert Config.p == [1, 2, 3, 4, 5], "Optional List[int] not parsed correctly"
    assert Config.q == [], "Optional List[int] not parsed correctly"
    assert Config.r == ["abc"], "Optional List[str] not parsed correctly"
    assert Config.s == ["abc", "def", "ghi"], "Optional List[str] not parsed correctly"
    assert Config.t == [], "Optional List[str] not parsed correctly"


def test_config_default_values_and_implied() -> None:
    environ.clear()

    class Config(Env):
        a: int = 1
        b: str = "hello"
        c: float = 3.14
        d: bool = True

    assert Config.a == 1
    assert Config.b == "hello"
    assert Config.c - 3.14 < MIN_FLOAT_DIFF
    assert Config.d


def test_error_handling() -> None:
    environ.clear()

    # Test missing required variable
    try:

        class Config1(Env):
            a: y.JsonObject

        assert False, "Should have raised RuntimeError for missing required variable"
    except RuntimeError as e:
        assert e.args[0] == "Failed to load required environment variable `A`"

    # Test blank required variable
    environ["B"] = ""
    try:

        class Config2(Env):
            b: int

        assert False, "Should have raised RuntimeError for blank required variable"
    except RuntimeError as e:
        assert (
            e.args[0]
            == "Environment variable `B` is blank and not marked as optional; it must have a value"
        )

    # invalid JSON conversion
    environ["C"] = "<invalid json>"
    try:

        class Config3(Env):
            c: y.JsonObject

        assert False, "Should have raised exception for invalid JSON"
    except json.JSONDecodeError:
        pass  # Should raise some JSON parsing error

    # invalid type conversion
    environ["D"] = "<not_a_number>"
    try:

        class Config4(Env):
            d: int

        assert False, "Should have raised exception for invalid int conversion"
    except ValueError:
        pass

    # test unsupported type
    environ["E"] = "test"
    try:

        class Config5(Env):
            e: set

        assert False, "Should have raised RuntimeError for unsupported type"
    except RuntimeError as e:
        assert "Unsupported type" in e.args[0]


def test_edge_cases() -> None:
    environ.clear()

    # whitespace handling
    environ["A"] = "  123  "
    environ["B"] = " hello world "
    environ["C"] = "  3.14  "
    environ["D"] = "  true  "
    environ["E"] = " 1, 2 , 3 "

    class Config1(Env):
        a: int
        b: str
        c: float
        d: bool
        e: List[int]

    assert Config1.a == 123, "int with whitespace not trimmed correctly"
    assert Config1.b == " hello world ", "str should preserve whitespace"
    assert Config1.c == 3.14, "float with whitespace not trimmed correctly"
    assert Config1.d == True, "bool with whitespace not trimmed correctly"
    assert Config1.e == [1, 2, 3], "List with extra whitespace not parsed correctly"

    environ.clear()

    # extreme values
    environ["F"] = "0"
    environ["G"] = "-1"
    environ["H"] = "999999999"
    environ["I"] = "-3.14159"
    environ["J"] = "0.0"

    class Config2(Env):
        f: int
        g: int
        h: int
        i: float
        j: float

    assert Config2.f == 0, "Zero int not parsed correctly"
    assert Config2.g == -1, "Negative int not parsed correctly"
    assert Config2.h == 999999999, "Large int not parsed correctly"
    assert Config2.i == -3.14159, "Negative float not parsed correctly"
    assert Config2.j == 0.0, "Zero float not parsed correctly"

    environ.clear()

    # special string values
    environ["K"] = "0"
    environ["L"] = "false"
    environ["M"] = ""

    class Config3(Env):
        k: str
        l: str
        m: Optional[str]

    assert Config3.k == "0", "String '0' should remain as string"
    assert Config3.l == "false", "String 'false' should remain as string"
    assert Config3.m == None, "Empty string for Optional[str] should be None"

    environ.clear()

    # single item lists
    environ["N"] = "42"
    environ["O"] = "hello"
    environ["P"] = "3.14"

    class Config4(Env):
        n: List[int]
        o: List[str]
        p: List[float]

    assert Config4.n == [42], "Single item List[int] not parsed correctly"
    assert Config4.o == ["hello"], "Single item List[str] not parsed correctly"
    assert Config4.p == [3.14], "Single item List[float] not parsed correctly"


def test_json_edge_cases() -> None:
    environ.clear()

    # JSON arrays
    environ["A"] = "[1, 2, 3]"
    environ["B"] = '["a", "b", "c"]'
    environ["C"] = '[{"key": "value"}, {"key2": "value2"}]'

    # nested JSON objects
    environ["D"] = '{"nested": {"key": "value", "array": [1, 2, 3]}}'

    # JSON with special characters
    environ["E"] = (
        '{"unicode": "café", "quotes": "he said \\"hello\\"", "newline": "line1\\nline2"}'
    )

    class Config(Env):
        a: y.JsonObject
        b: y.JsonObject
        c: y.JsonObject
        d: y.JsonObject
        e: y.JsonObject

    assert Config.a == [1, 2, 3], "JSON array of numbers not parsed correctly"
    assert Config.b == ["a", "b", "c"], "JSON array of strings not parsed correctly"
    assert Config.c == [
        {"key": "value"},
        {"key2": "value2"},
    ], "JSON array of objects not parsed correctly"
    assert Config.d == {
        "nested": {"key": "value", "array": [1, 2, 3]}
    }, "Nested JSON object not parsed correctly"
    assert Config.e["unicode"] == "café", "JSON with unicode not parsed correctly"
    assert (
        Config.e["quotes"] == 'he said "hello"'
    ), "JSON with escaped quotes not parsed correctly"
    assert (
        Config.e["newline"] == "line1\nline2"
    ), "JSON with newline not parsed correctly"


def test_refresh_method() -> None:
    environ.clear()
    environ["TEST_VAR"] = "initial"

    class Config(Env):
        test_var: str

    assert Config.test_var == "initial", "Initial value not set correctly"

    # Change environment variable
    environ["TEST_VAR"] = "updated"

    # Value should still be the old one
    assert Config.test_var == "initial", "Value should not change without refresh"

    # Refresh and check new value
    Config.refresh()
    assert Config.test_var == "updated", "Value should update after refresh"


def test_inheritance() -> None:
    environ.clear()
    environ["BASE_VAR"] = "base"
    environ["CHILD_VAR"] = "child"

    class BaseConfig(Env):
        base_var: str

    class ChildConfig(BaseConfig):
        child_var: str

    assert ChildConfig.base_var == "base", "Inherited variable not accessible"
    assert ChildConfig.child_var == "child", "Child variable not accessible"
    assert BaseConfig.base_var == "base", "Base class variable not accessible"


def test_type_coercion_edge_cases() -> None:
    environ.clear()

    # boolean edge cases
    environ["A"] = "FALSE"
    environ["B"] = "True"
    environ["C"] = "1"
    environ["D"] = "0"
    environ["E"] = "yes"  # Should be truthy
    environ["F"] = "no"  # Should be truthy (not "false" or "0")

    class Config(Env):
        a: bool
        b: bool
        c: bool
        d: bool
        e: bool
        f: bool

    assert not Config.a, "FALSE should be false"
    assert Config.b, "True should be true"
    assert Config.c, "1 should be true"
    assert not Config.d, "0 should be false"
    assert Config.e, "yes should be true (not false or 0)"
    assert Config.f, "no should be true (not false or 0)"

    environ.clear()

    # list edge cases with mixed whitespace
    environ["G"] = "1,2,3"
    environ["H"] = "1, 2, 3"
    environ["I"] = " 1 , 2 , 3 "
    environ["J"] = "1,  2,   3"

    class Config2(Env):
        g: List[int]
        h: List[int]
        i: List[int]
        j: List[int]

    assert Config2.g == [1, 2, 3], "List without spaces not parsed correctly"
    assert Config2.h == [1, 2, 3], "List with spaces not parsed correctly"
    assert Config2.i == [1, 2, 3], "List with extra whitespace not parsed correctly"
    assert Config2.j == [1, 2, 3], "List with irregular spacing not parsed correctly"


def test_enum_types() -> None:
    environ.clear()

    environ["MODE"] = "development"
    environ["LOG_LEVEL"] = "info"

    class Config(Env):
        mode: EnvMode
        log_level: LogLevel

    assert Config.mode == EnvMode.DEVELOPMENT, "Enum not parsed correctly"
    assert Config.log_level == LogLevel.INFO, "Enum not parsed correctly"
    assert isinstance(Config.mode, EnvMode), "Value should be enum instance"
    assert isinstance(Config.log_level, LogLevel), "Value should be enum instance"


def test_optional_enum_types() -> None:
    environ.clear()

    environ["MODE"] = "production"
    # LOG_LEVEL not set

    class Config(Env):
        mode: Optional[EnvMode]
        log_level: Optional[LogLevel]

    assert Config.mode == EnvMode.PRODUCTION, "Optional enum not parsed correctly"
    assert Config.log_level is None, "Optional enum should be None when not set"
    assert isinstance(Config.mode, EnvMode), "Value should be enum instance"


def test_enum_default_values() -> None:
    environ.clear()

    class Config(Env):
        mode: EnvMode = EnvMode.DEVELOPMENT
        log_level: LogLevel = LogLevel.WARNING

    assert Config.mode == EnvMode.DEVELOPMENT, "Enum default not set correctly"
    assert Config.log_level == LogLevel.WARNING, "Enum default not set correctly"


def test_enum_error_handling() -> None:
    environ.clear()

    # missing required enum
    try:

        class Config1(Env):
            mode: EnvMode

        assert False, "Should have raised RuntimeError for missing required enum"
    except RuntimeError as e:
        assert e.args[0] == "Failed to load required environment variable `MODE`"

    # invalid enum value
    environ["MODE"] = "invalid_mode"
    try:

        class Config2(Env):
            mode: EnvMode

        assert False, "Should have raised ValueError for invalid enum value"
    except ValueError:
        pass  # Should raise ValueError for invalid enum value

    # try blank string value for enum
    environ["MODE"] = ""
    try:

        class Config3(Env):
            mode: EnvMode

        assert False, "Should have raised RuntimeError for blank enum value"
    except RuntimeError as e:
        assert "is blank and not marked as optional" in e.args[0]


def test_enum_refresh() -> None:
    environ.clear()
    environ["MODE"] = "development"

    class Config(Env):
        mode: EnvMode

    assert Config.mode == EnvMode.DEVELOPMENT, "Initial enum value not set correctly"

    # change environment variable
    environ["MODE"] = "production"

    # value should still be the old one
    assert (
        Config.mode == EnvMode.DEVELOPMENT
    ), "Enum value should not change without refresh"

    # refresh and check new value
    Config.refresh()
    assert Config.mode == EnvMode.PRODUCTION, "Enum value should update after refresh"


def test_literal_types() -> None:
    if Literal is None:
        raise RuntimeError("Literal is not available")

    environ.clear()

    environ["MODE"] = "debug"
    environ["PORT"] = "8080"
    environ["ENABLED"] = "true"
    environ["VERSION"] = "1.0"

    class Config(Env):
        mode: Literal["debug", "release"]
        port: Literal[8080, 9000, 3000]
        enabled: Literal[True, False]
        version: Literal["1.0", "2.0"]

    assert Config.mode == "debug", "String literal not parsed correctly"
    assert Config.port == 8080, "Int literal not parsed correctly"
    assert Config.enabled == True, "Bool literal not parsed correctly"
    assert Config.version == "1.0", "Mixed literal not parsed correctly"


def test_optional_literal_types() -> None:
    if Literal is None:
        raise RuntimeError("Literal is not available")

    environ.clear()

    environ["MODE"] = "production"
    # PORT not set

    class Config(Env):
        mode: Optional[Literal["development", "production"]]
        port: Optional[Literal[8080, 9000]]

    assert Config.mode == "production", "Optional literal not parsed correctly"
    assert Config.port is None, "Optional literal should be None when not set"


def test_literal_default_values() -> None:
    if Literal is None:
        return  # Skip test if Literal is not available

    environ.clear()

    class Config(Env):
        mode: Literal["dev", "prod"] = "dev"
        count: Literal[1, 5, 10] = 5

    assert Config.mode == "dev", "Literal default not set correctly"
    assert Config.count == 5, "Literal default not set correctly"


def test_literal_error_handling() -> None:
    if Literal is None:
        raise RuntimeError("Literal is not available")

    environ.clear()

    # Test missing required literal
    try:

        class Config1(Env):
            mode: Literal["dev", "prod"]

        assert False, "Should have raised RuntimeError for missing required literal"
    except RuntimeError as e:
        assert e.args[0] == "Failed to load required environment variable `MODE`"

    # Test invalid literal value
    environ["MODE"] = "invalid_mode"
    try:

        class Config2(Env):
            mode: Literal["dev", "prod"]

        assert False, "Should have raised ValueError for invalid literal value"
    except ValueError as e:
        assert "not one of the allowed literal values" in str(e)

    # Test blank literal value
    environ["MODE"] = ""
    try:

        class Config3(Env):
            mode: Literal["dev", "prod"]

        assert False, "Should have raised RuntimeError for blank literal value"
    except RuntimeError as e:
        assert "is blank and not marked as optional" in e.args[0]


def test_literal_type_coercion() -> None:
    if Literal is None:
        raise RuntimeError("Literal is not available")

    environ.clear()

    # Test type coercion for different literal types
    environ["STR_VAL"] = "hello"
    environ["INT_VAL"] = "42"
    environ["INT_VAL2"] = "314"
    environ["BOOL_VAL"] = "false"
    environ["MIXED_VAL"] = "100"  # Should match int literal

    class Config(Env):
        str_val: Literal["hello", "world"]
        int_val: Literal[42, 99]
        int_val2: Literal[314, 271]  # Using ints instead of floats for type checker
        bool_val: Literal[True, False]
        mixed_val: Literal["text", 100]  # Mixed types without floats

    assert Config.str_val == "hello", "String literal coercion failed"
    assert Config.int_val == 42, "Int literal coercion failed"
    assert Config.int_val2 == 314, "Int literal coercion failed"
    assert Config.bool_val == False, "Bool literal coercion failed"
    assert Config.mixed_val == 100, "Mixed literal coercion failed"
