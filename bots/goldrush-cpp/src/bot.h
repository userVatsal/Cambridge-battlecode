// Per-champion decision loop. One Bot instance lives for the whole match.
#pragma once
#include "state.h"

class Bot {
public:
    void play_turn();

private:
    bool guards(cambc::champion& me);
    ChampionState state_;
};
