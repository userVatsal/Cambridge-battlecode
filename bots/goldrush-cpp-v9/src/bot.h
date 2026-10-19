// Per-champion decision loop. One Bot instance lives for the whole match.
#pragma once
#include "state.h"

class Bot {
public:
    void play_turn();

private:
    ChampionState state_;
};
