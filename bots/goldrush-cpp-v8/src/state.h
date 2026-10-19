// Per-champion memory that survives between turns. Each champion runs its own
// copy of the bot, so this is never shared with teammates.
#pragma once
#include <cambc.h>

#include <cstddef>
#include <cstdint>
#include <optional>
#include <unordered_map>
#include <vector>

struct CampGroupInfo {
    cambc::map::camp_group group;
    cambc::bitboard tiles;  // spawn tiles never change, so they are cached once
    std::vector<cambc::vec2> tile_list;  // same tiles as a list: checking 1-4 tiles beats a full-map AND
    bool monolith;
};

struct ChampionState {
    std::size_t build_index = 0;
    std::optional<std::vector<CampGroupInfo>> camp_layout;
    // Camp group index -> first round it is worth visiting again.
    std::unordered_map<std::size_t, std::uint32_t> unavailable_until;
    // Position after each turn we chose to walk, newest last.
    std::vector<cambc::vec2> recent_moves;
};
