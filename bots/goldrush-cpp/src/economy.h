// Shopping and gem banking.
#pragma once
#include <cambc.h>

#include "state.h"

namespace economy {

// Follow this champion's build order, buying as many steps as gold allows.
void buy_items(ChampionState& state);

bool should_bank(const cambc::champion& me);

// Tribute at an adjacent altar, otherwise walk towards the nearest free one.
bool bank_gems();

}  // namespace economy
