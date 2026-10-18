"""Pathfinding on top of the engine's native Bitboard and DistanceField."""
import cambc
from cambc import game_map

Team = cambc.Team


def tiles_around(position, radius):
    tiles = cambc.Bitboard()
    tiles.draw_chebyshev(position, radius)
    return tiles


def blocked_tiles():
    blocked = (game_map.walls() | game_map.holes() | game_map.altars()
               | game_map.spawn_region(Team.ENEMY) | cambc.vision.champion_tiles()
               | cambc.vision.camp_tiles() | cambc.vision.teleport_tiles())
    blocked.set(cambc.me().position(), False)
    return blocked


def move_towards_closest(goals):
    """Step one move along a shortest path to the nearest goal tile.

    Occupied camp tiles may be goals: we path next to them, never onto them.
    """
    me = cambc.me()
    origin = me.position()
    if not me.can_move() or goals.is_set(origin):
        return False

    blocked = blocked_tiles()
    goals = goals & (~blocked | cambc.vision.camp_tiles())
    if goals.is_empty():
        return False
    if goals.count() == 1 and not blocked.is_set(goals.positions()[0]):
        return me.move_towards(goals.positions()[0])

    field = cambc.DistanceField()
    field.compute_to(blocked & ~goals, goals, tiles_around(origin, 0), cambc.Bitboard())
    reachable = blocked.reachable_tiles(origin, me.base_stats().base_move_speed)
    step = min([origin, *reachable.positions()], key=field.get)
    if step == origin:
        return False
    try:
        return me.move_absolute(step)
    except cambc.Error:
        return False


def move_home():
    return move_towards_closest(game_map.spawn_region(Team.ALLY))


def at_spawn():
    return game_map.spawn_region(Team.ALLY).is_set(cambc.me().position())
