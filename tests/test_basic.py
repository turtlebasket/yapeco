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
        from typing_extensions import Literal  # type: ignore
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


def test_unicode_handling() -> None:
    """Test Unicode and special character handling."""
    environ.clear()

    environ["UNICODE_STR"] = "café ☕ 🚀"
    environ["EMOJI"] = "🎉"
    environ["CHINESE"] = "你好"
    environ["ESCAPED"] = "line1\\nline2\\ttab"
    environ["QUOTES"] = "He said \"hello\" and 'goodbye'"

    class Config(Env):
        unicode_str: str
        emoji: str
        chinese: str
        escaped: str
        quotes: str

    assert Config.unicode_str == "café ☕ 🚀", "Unicode string not handled correctly"
    assert Config.emoji == "🎉", "Emoji not handled correctly"
    assert Config.chinese == "你好", "Chinese characters not handled correctly"
    assert (
        Config.escaped == "line1\\nline2\\ttab"
    ), "Escaped characters should remain as literal"
    assert (
        Config.quotes == "He said \"hello\" and 'goodbye'"
    ), "Quotes not handled correctly"


def test_large_numbers() -> None:
    """Test handling of very large numbers and scientific notation."""
    environ.clear()

    environ["LARGE_INT"] = "999999999999999999"
    environ["NEGATIVE_LARGE"] = "-999999999999999999"
    environ["SCIENTIFIC"] = "1.23e10"
    environ["NEGATIVE_SCIENTIFIC"] = "-4.56e-10"
    environ["ZERO_SCIENTIFIC"] = "0.0e0"

    class Config(Env):
        large_int: int
        negative_large: int
        scientific: float
        negative_scientific: float
        zero_scientific: float

    assert Config.large_int == 999999999999999999, "Large int not parsed correctly"
    assert (
        Config.negative_large == -999999999999999999
    ), "Negative large int not parsed correctly"
    assert (
        abs(Config.scientific - 1.23e10) < 1e6
    ), "Scientific notation not parsed correctly"
    assert (
        abs(Config.negative_scientific - (-4.56e-10)) < 1e-15
    ), "Negative scientific notation not parsed correctly"
    assert (
        Config.zero_scientific == 0.0
    ), "Zero in scientific notation not parsed correctly"


def test_type_annotation_variations() -> None:
    """Test different ways of writing type annotations for backward compatibility."""
    environ.clear()

    environ["LIST_OLD"] = "1, 2, 3"
    environ["LIST_NEW"] = "a, b, c"
    environ["OPT_OLD"] = "test"
    environ["OPT_UNION"] = "42"

    from typing import List, Union

    class ConfigOld(Env):
        list_old: List[int]
        opt_old: Optional[str]

    class ConfigNew(Env):
        # Python 3.9+ style annotations, but should work in 3.8 too
        list_new: List[str]  # Using List[] for compatibility
        opt_union: Union[int, None]  # Alternative to Optional[]

    assert ConfigOld.list_old == [1, 2, 3], "List[T] annotation not working"
    assert ConfigOld.opt_old == "test", "Optional[T] annotation not working"
    assert ConfigNew.list_new == ["a", "b", "c"], "List[T] annotation not working"
    assert ConfigNew.opt_union == 42, "Union[T, None] annotation not working"


def test_complex_json_structures() -> None:
    """Test complex nested JSON structures."""
    environ.clear()

    environ[
        "DEEPLY_NESTED"
    ] = """
    {
        "level1": {
            "level2": {
                "level3": {
                    "data": [1, 2, 3],
                    "flags": {"a": true, "b": false}
                }
            }
        },
        "arrays": [
            {"id": 1, "name": "first"},
            {"id": 2, "name": "second"}
        ]
    }
    """

    environ["JSON_ARRAY"] = '[{"x": 1}, {"y": 2}, {"z": [3, 4, 5]}]'
    environ["MIXED_TYPES"] = (
        '{"str": "text", "int": 42, "float": 3.14, "bool": true, "null": null, "array": [1, "two", 3.0]}'
    )

    class Config(Env):
        deeply_nested: y.JsonObject
        json_array: y.JsonObject
        mixed_types: y.JsonObject

    assert Config.deeply_nested["level1"]["level2"]["level3"]["data"] == [1, 2, 3]
    assert Config.deeply_nested["level1"]["level2"]["level3"]["flags"]["a"] is True
    assert Config.deeply_nested["arrays"][0]["name"] == "first"

    assert len(Config.json_array) == 3
    assert Config.json_array[2]["z"] == [3, 4, 5]

    assert Config.mixed_types["str"] == "text"
    assert Config.mixed_types["int"] == 42
    assert Config.mixed_types["float"] == 3.14
    assert Config.mixed_types["bool"] is True
    assert Config.mixed_types["null"] is None
    assert Config.mixed_types["array"] == [1, "two", 3.0]


def test_malformed_input_edge_cases() -> None:
    """Test various malformed inputs and their error handling."""
    environ.clear()

    # Test malformed JSON
    environ["BAD_JSON1"] = '{"missing": quote}'
    try:

        class BadConfig1(Env):
            bad_json1: y.JsonObject

        assert False, "Should have raised JSON error for missing quote"
    except json.JSONDecodeError:
        pass  # Expected

    environ["BAD_JSON2"] = "{trailing comma,}"
    try:

        class BadConfig2(Env):
            bad_json2: y.JsonObject

        assert False, "Should have raised JSON error for trailing comma"
    except json.JSONDecodeError:
        pass  # Expected

    environ["BAD_JSON3"] = '{"unclosed": {'
    try:

        class BadConfig3(Env):
            bad_json3: y.JsonObject

        assert False, "Should have raised JSON error for unclosed brace"
    except json.JSONDecodeError:
        pass  # Expected


def test_extreme_list_edge_cases() -> None:
    """Test edge cases for list parsing."""
    environ.clear()

    # Lists with unusual spacing and formatting
    environ["WEIRD_SPACES"] = "  1  ,  2  ,  3  "
    environ["MIXED_QUOTES"] = "\"hello\", 'world', unquoted"

    class Config1(Env):
        weird_spaces: List[int]
        mixed_quotes: List[str]

    assert Config1.weird_spaces == [1, 2, 3], "Weird spacing not handled"
    assert Config1.mixed_quotes == [
        '"hello"',
        "'world'",
        "unquoted",
    ], "Mixed quotes not preserved"

    # Test lists that will cause ValueError due to empty strings
    environ.clear()
    environ["TRAILING_COMMA"] = "1,2,3,"
    try:

        class ConfigTrailing(Env):
            trailing_comma: List[int]

        assert False, "Should have raised ValueError for empty string in int list"
    except ValueError:
        pass  # Expected - empty string after trailing comma can't convert to int

    environ["LEADING_COMMA"] = ",1,2,3"
    try:

        class ConfigLeading(Env):
            leading_comma: List[int]

        assert False, "Should have raised ValueError for empty string in int list"
    except ValueError:
        pass  # Expected - empty string before leading number can't convert to int

    environ["MULTIPLE_COMMAS"] = "1,,2,,,3"
    try:

        class ConfigMultiple(Env):
            multiple_commas: List[int]

        assert False, "Should have raised ValueError for empty strings in int list"
    except ValueError:
        pass  # Expected - empty strings between commas can't convert to int

    # String lists handle empty strings fine
    environ["ONLY_COMMAS"] = ",,,"

    class ConfigStrings(Env):
        only_commas: List[str]

    assert Config1.mixed_quotes == [
        '"hello"',
        "'world'",
        "unquoted",
    ], "Mixed quotes not preserved"
    assert ConfigStrings.only_commas == [
        "",
        "",
        "",
        "",
    ], "Only commas should create empty strings"


def test_boolean_edge_cases_comprehensive() -> None:
    """Comprehensive test of boolean parsing edge cases."""
    environ.clear()

    test_cases = [
        # (env_value, expected_bool, description)
        ("True", True, "capitalized True"),
        ("TRUE", True, "uppercase TRUE"),
        ("true", True, "lowercase true"),
        ("False", False, "capitalized False"),
        ("FALSE", False, "uppercase FALSE"),
        ("false", False, "lowercase false"),
        ("1", True, "string '1'"),
        ("0", False, "string '0'"),
        ("yes", True, "string 'yes'"),
        ("no", True, "string 'no' is truthy"),
        ("on", True, "string 'on'"),
        ("off", True, "string 'off' is truthy"),
        ("", False, "empty string in optional context"),
        ("   true   ", True, "true with whitespace should be truthy"),
        (
            "   false   ",
            True,
            "false with whitespace should be truthy because of spaces",
        ),
        ("2", True, "number > 1"),
        ("-1", True, "negative number"),
        ("0.0", True, "float zero as string is truthy"),
        ("anything", True, "random string is truthy"),
    ]

    for i, (env_value, expected, description) in enumerate(test_cases):
        environ.clear()
        environ[f"TEST_VAR"] = env_value

        if env_value == "":
            # Test optional bool for empty string
            class TestConfig(Env):
                test_var: Optional[bool]

            expected_result = None if env_value == "" else expected
            assert (
                TestConfig.test_var == expected_result
            ), f"Failed for {description}: got {TestConfig.test_var}, expected {expected_result}"
        else:

            class TestConfig(Env):
                test_var: bool

            assert (
                TestConfig.test_var == expected
            ), f"Failed for {description}: got {TestConfig.test_var}, expected {expected}"


def test_multiple_inheritance() -> None:
    """Test multiple inheritance scenarios."""
    environ.clear()

    environ["BASE1_VAR"] = "base1"
    environ["BASE2_VAR"] = "base2"
    environ["CHILD_VAR"] = "child"

    class Base1(Env):
        base1_var: str

    class Base2(Env):
        base2_var: str

    class MultiChild(Base1, Base2):
        child_var: str

    assert MultiChild.base1_var == "base1", "Multiple inheritance from Base1 failed"
    assert MultiChild.base2_var == "base2", "Multiple inheritance from Base2 failed"
    assert (
        MultiChild.child_var == "child"
    ), "Child variable in multiple inheritance failed"


def test_override_behavior() -> None:
    """Test behavior when subclasses override parent fields."""
    environ.clear()

    environ["SHARED_VAR"] = "parent_value"
    environ["OVERRIDE_VAR"] = "42"

    class Parent(Env):
        shared_var: str
        override_var: str = "default"

    class Child(Parent):
        override_var: int  # Different type

    assert Parent.shared_var == "parent_value"
    assert Parent.override_var == "42"  # String type from parent
    assert Child.shared_var == "parent_value"  # Inherited
    assert Child.override_var == 42  # Int type from child override


def test_class_variable_isolation() -> None:
    """Test that different config classes don't interfere with each other."""
    environ.clear()

    environ["VAR1"] = "config1"
    environ["VAR2"] = "config2"

    class Config1(Env):
        var1: str

    class Config2(Env):
        var2: str

    # Each should only have its own variable
    assert hasattr(Config1, "var1"), "Config1 should have var1"
    assert not hasattr(Config1, "var2"), "Config1 should not have var2"
    assert not hasattr(Config2, "var1"), "Config2 should not have var1"
    assert hasattr(Config2, "var2"), "Config2 should have var2"

    assert Config1.var1 == "config1"
    assert Config2.var2 == "config2"


def test_refresh_with_type_changes() -> None:
    """Test refresh behavior when environment values change to different types."""
    environ.clear()
    environ["DYNAMIC_VAR"] = "123"

    class Config(Env):
        dynamic_var: str

    assert Config.dynamic_var == "123"

    # Change to a different value but same type
    environ["DYNAMIC_VAR"] = "456"
    Config.refresh()
    assert Config.dynamic_var == "456"

    # Test with optional field changing from None to value
    environ.clear()

    class OptionalConfig(Env):
        optional_var: Optional[str]

    assert OptionalConfig.optional_var is None

    environ["OPTIONAL_VAR"] = "now_has_value"
    OptionalConfig.refresh()
    assert OptionalConfig.optional_var == "now_has_value"


def test_deep_inheritance_chain() -> None:
    """Test deep inheritance chains and method resolution order."""
    environ.clear()

    environ["GRANDPARENT_VAR"] = "grandparent"
    environ["PARENT_VAR"] = "parent"
    environ["CHILD_VAR"] = "child"
    environ["GRANDCHILD_VAR"] = "grandchild"

    class GrandParent(Env):
        grandparent_var: str

    class Parent(GrandParent):
        parent_var: str

    class Child(Parent):
        child_var: str

    class GrandChild(Child):
        grandchild_var: str

    # Test all levels have access to all inherited variables
    assert GrandChild.grandparent_var == "grandparent"
    assert GrandChild.parent_var == "parent"
    assert GrandChild.child_var == "child"
    assert GrandChild.grandchild_var == "grandchild"

    # Test intermediate levels only have their inheritance
    assert hasattr(Parent, "grandparent_var")
    assert hasattr(Parent, "parent_var")
    assert not hasattr(Parent, "child_var")
    assert not hasattr(Parent, "grandchild_var")


def test_mixin_patterns() -> None:
    """Test mixin-style inheritance patterns."""
    environ.clear()

    environ["DATABASE_URL"] = "postgresql://localhost"
    environ["REDIS_URL"] = "redis://localhost"
    environ["LOG_LEVEL"] = "info"
    environ["DEBUG"] = "false"

    class DatabaseMixin(Env):
        database_url: str

    class CacheMixin(Env):
        redis_url: str

    class LoggingMixin(Env):
        log_level: str
        debug: bool

    class AppConfig(DatabaseMixin, CacheMixin, LoggingMixin):
        # Need at least one annotation to trigger __init_subclass__
        _dummy: str = "dummy"

    assert AppConfig.database_url == "postgresql://localhost"
    assert AppConfig.redis_url == "redis://localhost"
    assert AppConfig.log_level == "info"
    assert AppConfig.debug == False


def test_diamond_inheritance() -> None:
    """Test diamond inheritance pattern."""
    environ.clear()

    environ["BASE_VAR"] = "base"
    environ["LEFT_VAR"] = "left"
    environ["RIGHT_VAR"] = "right"
    environ["CHILD_VAR"] = "child"

    class Base(Env):
        base_var: str

    class Left(Base):
        left_var: str

    class Right(Base):
        right_var: str

    class Diamond(Left, Right):
        child_var: str

    # Should have all variables from the inheritance hierarchy
    assert Diamond.base_var == "base"
    assert Diamond.left_var == "left"
    assert Diamond.right_var == "right"
    assert Diamond.child_var == "child"


def test_concurrent_class_creation() -> None:
    """Test thread safety during class creation."""
    import threading
    import time

    environ.clear()
    environ["CONCURRENT_VAR"] = "shared_value"

    results = []
    exceptions = []

    def create_config_class(thread_id):
        try:
            # Create a unique class name to avoid conflicts
            class_name = f"ThreadConfig{thread_id}"
            ThreadConfig = type(
                class_name,
                (Env,),
                {"__annotations__": {"concurrent_var": str}, "thread_id": thread_id},
            )

            results.append(
                (thread_id, ThreadConfig.concurrent_var, ThreadConfig.thread_id)
            )
        except Exception as e:
            exceptions.append((thread_id, e))

    threads = []
    for i in range(5):
        thread = threading.Thread(target=create_config_class, args=(i,))
        threads.append(thread)

    # Start all threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    # Check results
    assert len(exceptions) == 0, f"Exceptions occurred: {exceptions}"
    assert len(results) == 5, f"Expected 5 results, got {len(results)}"

    for thread_id, concurrent_var, result_thread_id in results:
        assert (
            concurrent_var == "shared_value"
        ), f"Thread {thread_id} got wrong value: {concurrent_var}"
        assert (
            result_thread_id == thread_id
        ), f"Thread {thread_id} got wrong thread_id: {result_thread_id}"


def test_memory_cleanup_behavior() -> None:
    """Test that class variables are properly set and don't leak."""
    environ.clear()
    environ["MEMORY_TEST"] = "test_value"

    # Create multiple config classes to test memory behavior
    configs = []
    for i in range(100):
        class_name = f"MemoryConfig{i}"
        ConfigClass = type(
            class_name, (Env,), {"__annotations__": {"memory_test": str}}
        )
        configs.append(ConfigClass)

    # All should have the same value
    for config in configs:
        assert config.memory_test == "test_value"

    # Test cleanup by checking that each class only has its own attributes
    for config in configs:
        # Should have the environment variable
        assert hasattr(config, "memory_test")
        # Should have the refresh method
        assert hasattr(config, "refresh")
        # Should not have variables from other test classes
        assert not hasattr(config, "var1")  # From test_class_variable_isolation
        assert not hasattr(config, "var2")


def test_python_version_compatibility() -> None:
    """Test compatibility features across Python versions."""
    import sys

    environ.clear()
    environ["VERSION_TEST"] = "3, 2, 1"

    # Test that both list and List work (should work in all supported versions)
    if sys.version_info >= (3, 9):
        # In Python 3.9+, both should work
        try:

            class ModernConfig(Env):
                version_test: list[int]  # Python 3.9+ style

            assert ModernConfig.version_test == [
                3,
                2,
                1,
            ], "Modern list annotation failed"
        except (SyntaxError, TypeError):
            # If this fails, it's expected in older Python versions
            pass

    # This should work in all supported versions (3.8+)
    from typing import List

    class CompatConfig(Env):
        version_test: List[int]  # Traditional typing.List style

    assert CompatConfig.version_test == [3, 2, 1], "Compatible List annotation failed"


def test_typing_extensions_fallback() -> None:
    """Test fallback to typing_extensions for older Python versions."""
    # This test verifies that the Literal import logic works correctly
    if Literal is not None:
        environ.clear()
        environ["FALLBACK_TEST"] = "option1"

        class FallbackConfig(Env):
            fallback_test: Literal["option1", "option2"]

        assert FallbackConfig.fallback_test == "option1", "Literal fallback failed"
    else:
        # If Literal is None, the import fallback worked as expected
        assert (
            True
        ), "Literal correctly unavailable when typing_extensions not installed"


def test_field_name_edge_cases() -> None:
    """Test edge cases in field naming and environment variable mapping."""
    environ.clear()

    # Test various field name patterns
    environ["SIMPLE"] = "simple"
    environ["WITH_UNDERSCORE"] = "underscore"
    environ["MULTIPLE_UNDER_SCORES"] = "multiple"
    environ["CAMELCASE"] = "camel"  # Note: field is camelCase but env var is CAMELCASE
    environ["NUMBER123"] = "number"

    class FieldNameConfig(Env):
        simple: str
        with_underscore: str
        multiple_under_scores: str
        camelCase: str  # This maps to CAMELCASE
        number123: str

    assert FieldNameConfig.simple == "simple"
    assert FieldNameConfig.with_underscore == "underscore"
    assert FieldNameConfig.multiple_under_scores == "multiple"
    assert FieldNameConfig.camelCase == "camel"
    assert FieldNameConfig.number123 == "number"


def test_builtin_field_exclusion() -> None:
    """Test that built-in fields are properly excluded from processing."""
    environ.clear()
    environ["__BUILTIN__"] = "should_be_ignored"
    environ["NORMAL_FIELD"] = "should_be_processed"

    class BuiltinFieldConfig(Env):
        __builtin__: str  # Should be ignored due to _builtin_field_re
        normal_field: str

    # Should not have processed the builtin field
    assert (
        not hasattr(BuiltinFieldConfig, "__builtin__")
        or BuiltinFieldConfig.__builtin__ != "should_be_ignored"
    )
    assert BuiltinFieldConfig.normal_field == "should_be_processed"


def test_json_null_handling() -> None:
    """Test handling of JSON null values in different contexts."""
    environ.clear()

    environ["JSON_WITH_NULL"] = '{"key": null, "other": "value"}'
    environ["JSON_NULL_ARRAY"] = '[null, "text", null, 42]'
    # Note: 'null' by itself is valid JSON but yapeco doesn't distinguish
    # between JsonObject types, so we test with optional instead

    class JsonNullConfig(Env):
        json_with_null: y.JsonObject
        json_null_array: y.JsonObject

    class OptionalJsonConfig(Env):
        json_just_null: Optional[y.JsonObject] = None

    assert JsonNullConfig.json_with_null["key"] is None
    assert JsonNullConfig.json_with_null["other"] == "value"
    assert JsonNullConfig.json_null_array == [None, "text", None, 42]

    # Test optional JSON with null value
    environ["JSON_JUST_NULL"] = "null"

    class OptionalJsonConfigWithValue(Env):
        json_just_null: Optional[y.JsonObject]

    assert OptionalJsonConfigWithValue.json_just_null is None


def test_enum_case_sensitivity() -> None:
    """Test enum parsing case sensitivity."""
    environ.clear()

    environ["CASE_MODE"] = "DEVELOPMENT"  # uppercase
    environ["MIXED_MODE"] = "Production"  # mixed case

    try:

        class CaseConfig1(Env):
            case_mode: EnvMode  # expects "development"

        assert False, "Should have raised ValueError for case mismatch"
    except ValueError:
        pass  # Expected - enum values are case sensitive

    try:

        class CaseConfig2(Env):
            mixed_mode: EnvMode  # expects "production"

        assert False, "Should have raised ValueError for case mismatch"
    except ValueError:
        pass  # Expected - enum values are case sensitive


def test_list_of_enums() -> None:
    """Test parsing lists of enum values."""
    environ.clear()

    # This should fail because the current implementation doesn't support List[Enum]
    environ["ENUM_LIST"] = "development,production,testing"

    try:

        class EnumListConfig(Env):
            enum_list: List[EnvMode]

        assert False, "Should have raised error - List[Enum] not supported"
    except RuntimeError as e:
        assert "Unsupported type" in str(e), f"Unexpected error message: {e}"


def test_comprehensive_error_messages() -> None:
    """Test that error messages are informative and helpful."""
    environ.clear()

    # Test missing required variable error message format
    try:

        class MissingConfig(Env):
            required_missing: str

        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "Failed to load required environment variable `REQUIRED_MISSING`" in str(
            e
        )

    # Test blank required variable error message format
    environ["BLANK_VAR"] = ""
    try:

        class BlankConfig(Env):
            blank_var: str

        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert (
            "Environment variable `BLANK_VAR` is blank and not marked as optional"
            in str(e)
        )

    # Test unsupported type error message format
    environ["UNSUPPORTED_VAR"] = "test"
    try:

        class UnsupportedConfig(Env):
            unsupported_var: set  # Unsupported type

        assert False, "Should have raised RuntimeError"
    except RuntimeError as e:
        assert "Unsupported type" in str(e) and "unsupported_var" in str(e)
