import cambc

import config
import draft

Draft = cambc.ChampionDraft


def test_first_pick_is_top_priority():
    assert draft.choose_pick([]) == config.DRAFT_PRIORITY[0]


def test_skips_champions_we_already_own():
    owned = list(config.DRAFT_PRIORITY[:2])
    assert draft.choose_pick(owned) == config.DRAFT_PRIORITY[2]


def test_returns_none_when_roster_exhausted():
    assert draft.choose_pick(list(config.DRAFT_PRIORITY)) is None


def test_priority_covers_every_draftable_champion_once():
    assert len(set(config.DRAFT_PRIORITY)) == len(config.DRAFT_PRIORITY) == 11
