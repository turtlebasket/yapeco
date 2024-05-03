import yapeco as y
from yapeco import BaseEnvironment as Env
from typing import List, Optional
from os import environ

MIN_FLOAT_DIFF = 0.0000000001


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
        a: y.JSON
        b: y.JSON

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

    class Config(Env):
        a: List[int]
        b: List[int]
        c: List[str]


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
        m: Optional[y.JSON]
        n: Optional[y.JSON]
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


# TODO: test failure cases later lol


def test_fail_load() -> None:
    # json object
    try:

        class Config(Env):
            a: y.JSON

    except RuntimeError as e:
        assert e.args[0] == "Failed to load required environment variable `A`"
