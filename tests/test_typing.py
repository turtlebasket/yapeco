from yapeco import BaseEnvironment as Env
from typing import Optional
from os import environ

# TODO: add support for Optional types

# def test_config_optional_types():
#     environ["ABC"] = "abc"
#     environ["EFG"] = "127"
#     environ["GHI"] = ""

#     class Config(Env):
#         abc: Optional[str]
#         efg: Optional[int]
#         ghi: Optional[int]

#     assert Config.abc == "abc"
#     assert Config.efg == 127
#     assert Config.ghi == None
