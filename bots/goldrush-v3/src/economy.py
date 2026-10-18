"""Shopping and gem banking."""
import cambc
from cambc import game_map

import config
import navigation


def _owned_count(item):
    try:
        return cambc.me().item_count()[int(item)]
    except (IndexError, cambc.Error):
        return 0


def buy_items(state):
    """Follow this champion's build order, buying as many steps as gold allows."""
    me = cambc.me()
    build = config.BUILDS.get(me.champion_name(), config.BUILDS[cambc.ChampionType.VARG])
    while state.build_index < len(build):
        item = build[state.build_index]
        if not me.can_buy(item, 1):
            return
        try:
            me.buy(item, 1)
        except cambc.Error:
            return
        state.build_index += 1


def should_bank(me):
    gems = me.gem_count()
    if gems <= 0:
        return False
    if gems >= config.BANK_GEMS or me.health() < me.max_health() * config.BANK_HEALTH:
        return True
    altar = nearest_altar_distance(me.position())
    return altar is not None and altar <= config.BANK_IF_ALTAR_WITHIN


def nearest_altar_distance(position):
    best = None
    for altar in game_map.altars().positions():
        d = position.chebyshev_distance(altar)
        if best is None or d < best:
            best = d
    return best


def bank_gems():
    """Tribute at an adjacent altar, otherwise walk towards the nearest free one."""
    me = cambc.me()
    goals = cambc.Bitboard()
    for altar in game_map.altars().positions():
        if cambc.vision.has_altar_lock(altar):
            continue
        if me.position().chebyshev_distance(altar) <= cambc.constants.SUBMIT_GEMS_RANGE:
            try:
                me.submit_gems(altar)
                return True
            except cambc.Error:
                continue
        goals |= navigation.tiles_around(altar, cambc.constants.SUBMIT_GEMS_RANGE)
    return navigation.move_towards_closest(goals)
