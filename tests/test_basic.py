from yapeco import BaseEnvironment as Env
from os import environ

MIN_FLOAT_DIFF = 0.0000000001


def test_config_primitive_types() -> None:
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
