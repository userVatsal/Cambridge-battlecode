"""Run bot logic on the host by replacing the engine-only `cambc` module with a stub.

The real SDK only works inside the match engine (WebAssembly). Pure decision
logic — draft order, build lists, thresholds — is tested here without it.
"""
import sys
import types
from pathlib import Path


class _Enum:
    """Any attribute access returns a stable, unique, comparable value."""

    def __init__(self, name, members=()):
        self._name = name
        for index, member in enumerate(members):
            setattr(self, member, index)

    def __getattr__(self, attr):
        if attr.startswith("_"):
            raise AttributeError(attr)
        value = f"{self._name}.{attr}"
        setattr(self, attr, value)
        return value


stub = types.ModuleType("cambc")
stub.ChampionDraft = _Enum("ChampionDraft", (
    "RYTH", "VESPER_VALE", "VENDETTA", "CASSI_AND_ISSAC", "STELLAR", "PRISM",
    "MARCELLA", "WILLOW", "REN", "VARG", "TAVI"))
stub.ChampionType = _Enum("ChampionType", (
    "RYTH", "VESPER_VALE", "VENDETTA", "CASSI", "ISSAC", "STELLAR", "PRISM",
    "MARCELLA", "WILLOW", "REN", "VARG", "TAVI"))
stub.ItemType = _Enum("ItemType")
stub.Team = _Enum("Team", ("ALLY", "ENEMY"))
stub.Error = type("Error", (Exception,), {})
stub.game_map = types.ModuleType("cambc.game_map")
sys.modules["cambc"] = stub
sys.modules["cambc.game_map"] = stub.game_map

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "bots" / "goldrush" / "src"))
