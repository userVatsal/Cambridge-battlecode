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


def _respawn_timer(group):
    """Rounds until a visible group is worth visiting again, or 0 if it is now."""
    try:
        group_state = group.state()
    except cambc.Error:
        return config.UNKNOWN_GROUP_COOLDOWN
    if isinstance(group_state, game_map.CampGroupRespawning):
        return max(1, int(group_state.timer))
    return 0


def camp_goals(state):
    """Spawn tiles of every camp group worth visiting right now.

    Spawn tiles never change, so the layout is cached once. A group seen
    respawning stays off the goal list until its timer has run out, even after
    it leaves vision. (v3 forgot it as soon as it was out of sight, so
    champions stepped towards it, saw it respawning, stepped away, and
    oscillated on the vision edge for the rest of the match — ladder games
    with zero gems tributed.)
    """
    me = cambc.me()
    if state.camp_layout is None:
        state.camp_layout = [(g, g.spawn_tiles(), _is_monolith(g)) for g in game_map.camp_groups()]
    now = cambc.round_number()
    allow_monolith = _team_ready_for_monolith(me)
    visible = cambc.vision.visible_tiles()
    goals = cambc.Bitboard()
    for index, (group, tiles, monolith) in enumerate(state.camp_layout):
        if monolith and not allow_monolith:
            continue
        if not (tiles & visible).is_empty():
            wait = _respawn_timer(group)
            if wait:
                state.unavailable_until[index] = now + wait
            else:
                state.unavailable_until.pop(index, None)
        if state.unavailable_until.get(index, 0) > now:
            continue
        goals |= tiles
    return goals


def block_nearby_groups(state, rounds):
    """Anti-loop fallback: take every group near us off the goal list for a while."""
    if state.camp_layout is None:
        return
    here = cambc.me().position()
    until = cambc.round_number() + rounds
    for index, (_, tiles, _) in enumerate(state.camp_layout):
        if (tiles & navigation.tiles_around(here, config.STUCK_BLOCK_RADIUS)).is_empty():
            continue
        state.unavailable_until[index] = max(state.unavailable_until.get(index, 0), until)


def advance_to_camps(state):
    goals = camp_goals(state)
    if goals.is_empty() and state.unavailable_until and state.camp_layout:
        # Everything known is respawning: pre-position on whichever comes back first.
        soonest = min(state.unavailable_until, key=state.unavailable_until.get)
        goals = state.camp_layout[soonest][1].copy()
    if goals.is_empty():
        return False
    return navigation.move_towards_closest(goals)
