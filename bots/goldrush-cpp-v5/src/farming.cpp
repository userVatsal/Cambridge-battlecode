#include "farming.h"

#include <algorithm>
#include <variant>

#include "config.h"
#include "navigation.h"

namespace farming {

static bool is_monolith(const cambc::map::camp_group& group) {
    return group.gem_value() >= config::monolith_gems;
}

bool team_ready_for_monolith(const cambc::champion& me) {
    return cambc::round_number() >= config::monolith_min_round
        && me.max_health() >= config::monolith_min_max_health;
}

// Rounds until a visible group is worth visiting again, or 0 if it is now.
static std::uint32_t respawn_wait(const cambc::map::camp_group& group) {
    try {
        const auto state = group.state();
        if (const auto* respawning = std::get_if<cambc::map::camp_group_respawning>(&state))
            return static_cast<std::uint32_t>(std::max(1, static_cast<int>(respawning->timer)));
        return 0;
    } catch (const std::exception&) {
        return config::unknown_group_cooldown;
    }
}

static void ensure_layout(ChampionState& state) {
    if (state.camp_layout) return;
    std::vector<CampGroupInfo> layout;
    for (const auto& group : cambc::map::camp_groups())
    {
        auto tiles = group.spawn_tiles();
        auto tile_list = tiles.positions();
        layout.push_back(CampGroupInfo{group, std::move(tiles), std::move(tile_list), is_monolith(group)});
    }
    state.camp_layout = std::move(layout);
}

// A group seen respawning stays off the goal list until its timer has run out,
// even after it leaves vision. Forgetting it as soon as it was out of sight
// made champions oscillate on the vision edge for the rest of the match — the
// ladder games with zero gems tributed.
cambc::bitboard camp_goals(ChampionState& state) {
    auto& me = cambc::self();
    ensure_layout(state);
    const auto now = cambc::round_number();
    const bool allow_monolith = team_ready_for_monolith(me);
    const auto visible = cambc::vision::visible_tiles();
    cambc::bitboard goals;
    const auto& layout = *state.camp_layout;
    for (std::size_t index = 0; index < layout.size(); ++index) {
        const auto& info = layout[index];
        if (info.monolith && !allow_monolith) continue;
        if (std::any_of(info.tile_list.begin(), info.tile_list.end(),
                        [&](cambc::vec2 tile) { return visible.is_set(tile); })) {
            const auto wait = respawn_wait(info.group);
            if (wait)
                state.unavailable_until[index] = now + wait;
            else
                state.unavailable_until.erase(index);
        }
        const auto blocked = state.unavailable_until.find(index);
        if (blocked != state.unavailable_until.end() && blocked->second > now) continue;
        goals |= info.tiles;
    }
    return goals;
}

void block_nearby_groups(ChampionState& state, std::uint32_t rounds) {
    if (!state.camp_layout) return;
    const auto here = cambc::self().position();
    const auto until = cambc::round_number() + rounds;
    const auto& layout = *state.camp_layout;
    for (std::size_t index = 0; index < layout.size(); ++index) {
        const auto& tiles = layout[index].tile_list;
        if (std::none_of(tiles.begin(), tiles.end(), [&](cambc::vec2 tile) {
                return static_cast<int>(here.chebyshev_distance(tile)) <= config::stuck_block_radius;
            }))
            continue;
        auto& entry = state.unavailable_until[index];
        entry = std::max(entry, until);
    }
}

bool advance_to_camps(ChampionState& state) {
    auto goals = camp_goals(state);
    if (goals.is_empty() && !state.unavailable_until.empty() && state.camp_layout) {
        // Everything known is respawning: pre-position on whichever comes back first.
        const auto soonest = std::min_element(state.unavailable_until.begin(), state.unavailable_until.end(),
            [](const auto& a, const auto& b) { return a.second < b.second; });
        goals = (*state.camp_layout)[soonest->first].tiles;
    }
    if (goals.is_empty()) return false;
    return navigation::move_towards_closest(goals);
}

}  // namespace farming
