// The planning half of the hybrid design (v10).
//
// bot.cpp runs a fixed list of deterministic guards first: survival, banking,
// shopping, fights already in range. Those must never go wrong, so they are
// plain rules. Only when no guard fires does the planner decide where the next
// stretch of rounds is best spent: it scores every known camp group by
// expected reward per round of work, then reflects on that choice (commitment
// to the current target, teammates' claims) before acting on it.
#pragma once
#include <cambc.h>

#include <cstddef>
#include <optional>

#include "state.h"

namespace planner {

// Camp group (index into the cached layout) to work on now; nullopt if none.
std::optional<std::size_t> choose_target(ChampionState& state);

// Where to walk for a target: its camp tiles, or — while it is respawning —
// the ring around them, because a champion standing on a spawn tile stops the
// camp from coming back (v10 champions sat on captured tiles for 300 rounds).
cambc::bitboard goal_tiles(const ChampionState& state, std::size_t target);

// Rule table for a camp already in attack range: clusters are always worth a
// swing (120 health, no damage back), awake camps are hitting us anyway, and
// sleeping wolves/elks are only fought when they belong to our target group.
bool worth_fighting(const ChampionState& state, const cambc::camp& camp);

// Tell teammates which group we are working on (or none) through shared memory.
void publish_claim(std::optional<std::size_t> target);

}  // namespace planner
