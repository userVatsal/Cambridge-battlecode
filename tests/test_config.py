import cambc

import config


def test_every_champion_has_a_build():
    for name in ("RYTH", "VESPER_VALE", "VENDETTA", "CASSI", "ISSAC", "STELLAR",
                 "PRISM", "MARCELLA", "WILLOW", "REN", "VARG", "TAVI"):
        assert getattr(cambc.ChampionType, name) in config.BUILDS, name


def test_builds_open_with_a_full_emblem():
    # Only a completed emblem (5 matching shards) grants its passive.
    for build in config.BUILDS.values():
        assert len(set(build[:5])) == 1


def test_thresholds_are_fractions():
    for value in (config.RECALL_HEALTH, config.SHIELD_HEALTH, config.HEAL_ALLY_HEALTH, config.BANK_HEALTH):
        assert 0 < value < 1


def test_recall_happens_before_banking_would_be_forced():
    assert config.RECALL_HEALTH < config.BANK_HEALTH
