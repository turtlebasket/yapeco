from yapeco import BaseEnvironment as Env
from typing import Optional
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

    assert Config.a == 1
    assert Config.b == "2"
    assert Config.c - 3.0 < MIN_FLOAT_DIFF
    assert not Config.d
    assert not Config.e
    assert not Config.f
    assert Config.g
    assert Config.h
    assert Config.i
    assert Config.j


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

    # same tests as before
    assert Config.a == 1
    assert Config.b == "2"
    assert Config.c != None and Config.c - 3.0 < MIN_FLOAT_DIFF
    assert not Config.d
    assert not Config.e
    assert not Config.f
    assert Config.g
    assert Config.h
    assert Config.i
    assert Config.j
    assert Config.l == None


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
