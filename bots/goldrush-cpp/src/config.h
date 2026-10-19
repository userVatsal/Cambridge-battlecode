// Tunable strategy constants. Change numbers here, not inside the logic files.
#pragma once
#include <cambc.h>

#include <array>
#include <cstdint>
#include <limits>
#include <string_view>
#include <vector>

namespace config {

inline constexpr std::string_view version = "goldrush-cpp-v9";

// Picked top-down, skipping anything we already own. The most common winning
// set across 49 ladder losses to the top teams: Cassi+Issac (one pick, two
// bodies), Stellar, Ren, Tavi, Ryth. Marcella was in 31 losing drafts, 1 win.
// 11/18 vs v7, 18/18 vs starter.
inline constexpr std::array draft_priority{
    cambc::champion_draft::cassi_and_issac,
    cambc::champion_draft::stellar,
    cambc::champion_draft::ren,
    cambc::champion_draft::tavi,
    cambc::champion_draft::ryth,
    cambc::champion_draft::varg,
    cambc::champion_draft::vendetta,
    cambc::champion_draft::prism,
    cambc::champion_draft::vesper_vale,
    cambc::champion_draft::marcella,
    cambc::champion_draft::willow,
};

// Item build order for a champion: shards cost 30 gold and five matching shards
// combine into the family emblem. Jungle first (30% less camp damage) keeps
// farmers alive; Power shards after that. Defined in economy.cpp.
const std::vector<cambc::item_type>& build_for(cambc::champion_type champion);

// Health fractions.
inline constexpr float recall_health = 0.35f;
inline constexpr float shield_health = 0.85f;
inline constexpr float heal_ally_health = 0.65f;
// Stay on spawn (healing) until at least this much health.
inline constexpr float leave_spawn_health = 0.9f;

// Gem banking: a camp kill destroys carried gems, so bank early.
inline constexpr std::uint32_t bank_gems = 30;
inline constexpr int bank_if_altar_within = 8;
inline constexpr float bank_health = 0.6f;

// Recall to shop once this much gold is unspent. Winners in 3,160 ladder games
// spend ~90% of the gold they earn. Trips lost before v6 only because of the
// spawn-healing bug; with it fixed, 150 gold beats never-shop 12/18.
inline constexpr std::uint32_t shop_trip_gold = 150;

// Camp groups worth at least this many gems are monoliths (200 gems, 20k HP,
// 200 strength) and are only attempted once the team is strong.
inline constexpr std::uint32_t monolith_gems = 150;
inline constexpr float monolith_min_max_health = 3000.0f;
inline constexpr std::uint32_t monolith_min_round = 700;

// Visible group whose state cannot be read: try it again after this many rounds.
inline constexpr std::uint32_t unknown_group_cooldown = 20;

// Anti-loop: if a champion keeps moving but visits at most stuck_max_tiles
// distinct tiles over stuck_window turns, nearby groups are skipped for
// stuck_block_rounds so it commits to a different target.
inline constexpr std::size_t stuck_window = 12;
inline constexpr std::size_t stuck_max_tiles = 3;
inline constexpr std::uint32_t stuck_block_rounds = 40;
inline constexpr int stuck_block_radius = 10;

}  // namespace config
