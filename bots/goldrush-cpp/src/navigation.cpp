#include "navigation.h"

namespace navigation {

using cambc::team;
using cambc::vec2;

cambc::bitboard tiles_around(vec2 position, int radius) {
    cambc::bitboard tiles;
    tiles.draw_chebyshev(position, radius);
    return tiles;
}

static cambc::bitboard blocked_tiles() {
    auto blocked = cambc::map::walls() | cambc::map::holes() | cambc::map::altars()
                 | cambc::map::spawn_region(team::enemy) | cambc::vision::champion_tiles()
                 | cambc::vision::camp_tiles() | cambc::vision::teleport_tiles();
    blocked.set(cambc::self().position(), false);
    return blocked;
}

bool move_towards_closest(cambc::bitboard goals) {
    auto& me = cambc::self();
    const vec2 origin = me.position();
    if (!me.can_move() || goals.is_set(origin)) return false;

    const auto blocked = blocked_tiles();
    goals &= ~blocked | cambc::vision::camp_tiles();
    if (goals.is_empty()) return false;
    if (goals.count() == 1 && !blocked.is_set(goals.positions()[0])) {
        try {
            return me.move_towards(goals.positions()[0]);
        } catch (const std::exception&) {
            return false;
        }
    }

    cambc::distance_field field;
    cambc::bitboard visited;
    field.compute_to(blocked & ~goals, goals, tiles_around(origin, 0), visited);

    // Ties keep the current tile, then the first strictly closer tile in row order.
    vec2 step = origin;
    for (vec2 tile : blocked.reachable_tiles(origin, me.base_stats().base_move_speed).positions())
        if (field.get(tile) < field.get(step)) step = tile;
    if (step == origin) return false;
    try {
        return me.move_absolute(step);
    } catch (const std::exception&) {
        return false;
    }
}

bool move_home() {
    return move_towards_closest(cambc::map::spawn_region(team::ally));
}

bool at_spawn() {
    return cambc::map::spawn_region(team::ally).is_set(cambc::self().position());
}

}  // namespace navigation
