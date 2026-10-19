// Pathfinding on top of the engine's native bitboard and distance_field.
#pragma once
#include <cambc.h>

namespace navigation {

cambc::bitboard tiles_around(cambc::vec2 position, int radius);

// Step one move along a shortest path to the nearest goal tile. Occupied camp
// tiles may be goals: we path next to them, never onto them.
bool move_towards_closest(cambc::bitboard goals);

bool move_home();

bool at_spawn();

}  // namespace navigation
