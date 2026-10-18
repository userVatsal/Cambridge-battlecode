"""Choosing which camp groups to clear and capture."""
import cambc
from cambc import game_map

import config
import navigation


def _is_monolith(group):
    return group.gem_value() >= config.MONOLITH_GEMS


def _team_ready_for_monolith(me):
    return (cambc.round_number() >= config.MONOLITH_MIN_ROUND
            and me.max_health() >= config.MONOLITH_MIN_MAX_HEALTH)


def camp_goals(state):
    """Spawn tiles of every camp group worth visiting right now.

    Spawn tiles never change, so the layout is cached once. Groups we can see
    respawning are dropped; unseen groups stay as exploration goals.
    """
    me = cambc.me()
    if state.camp_layout is None:
        state.camp_layout = [(g, g.spawn_tiles(), _is_monolith(g)) for g in game_map.camp_groups()]
    allow_monolith = _team_ready_for_monolith(me)
    visible = cambc.vision.visible_tiles()
    goals = cambc.Bitboard()
    for group, tiles, monolith in state.camp_layout:
        if monolith and not allow_monolith:
            continue
        if not (tiles & visible).is_empty():
            try:
                if isinstance(group.state(), game_map.CampGroupRespawning):
                    continue
            except cambc.Error:
                pass
        goals |= tiles
    return goals


def advance_to_camps(state):
    return navigation.move_towards_closest(camp_goals(state))
