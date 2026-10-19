// Choosing which camp groups to clear and capture.
#pragma once
#include <cambc.h>

#include <cstdint>

#include "state.h"

namespace farming {

bool team_ready_for_monolith(const cambc::champion& me);

// Spawn tiles of every camp group worth visiting right now.
cambc::bitboard camp_goals(ChampionState& state);

// Anti-loop fallback: take every group near us off the goal list for a while.
void block_nearby_groups(ChampionState& state, std::uint32_t rounds);

bool advance_to_camps(ChampionState& state);

}  // namespace farming
