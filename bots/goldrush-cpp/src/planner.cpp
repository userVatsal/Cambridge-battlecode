#include "planner.h"

#include <algorithm>

#include "config.h"
#include "farming.h"
#include "navigation.h"

namespace planner {

namespace {

using cambc::camp_type;

// Fixed camp stats from the SDK documentation; camp health is only readable in
// vision, but the planner has to price groups it cannot see yet.
float camp_health(camp_type type) {
    switch (type) {
        case camp_type::wolf: return 1350.0f;
        case camp_type::elk: return 2400.0f;
        case camp_type::gem_cluster:
        case camp_type::gold_cluster: return 120.0f;
        case camp_type::monolith: return 20000.0f;
        case camp_type::golem: return 5000.0f;
    }
    return 1000.0f;
}

float camp_strength(camp_type type) {
    switch (type) {
        case camp_type::wolf: return 20.0f;
        case camp_type::elk: return 60.0f;
        case camp_type::gem_cluster:
        case camp_type::gold_cluster: return 0.0f;
        case camp_type::monolith: return 200.0f;
        case camp_type::golem: return 120.0f;
    }
    return 0.0f;
}

bool hits_back(camp_type type) {
    return camp_strength(type) > 0.0f;
}

// Damage the group deals while `fighters` champions of our strength clear it.
// Raw strength overstates it about sevenfold (armour, heals, recalls): on rows
// v9 took 0.14 camp damage per point it dealt, so the result is scaled down.
float expected_damage(const CampGroupInfo& info, float strength, float fighters) {
    float health = 0.0f, hitting = 0.0f;
    for (const auto& camp : info.group) {
        health += camp_health(camp.kind());
        hitting += camp_strength(camp.kind());
    }
    return config::plan_damage_scale * hitting * health / (strength * fighters) / fighters;
}

// Terrain that never changes; camps and champions move or die, so they are left out.
const cambc::bitboard& terrain() {
    static const auto blocked = cambc::map::walls() | cambc::map::holes() | cambc::map::altars()
                              | cambc::map::spawn_region(cambc::team::enemy);
    return blocked;
}

// Our shared-memory byte: our position in the ally list (stable all match).
std::optional<std::size_t> my_slot() {
    static const auto slot = []() -> std::optional<std::size_t> {
        const auto allies = cambc::champions(cambc::team::ally);
        for (std::size_t i = 0; i < allies.size(); ++i)
            if (allies[i] == cambc::self() && i < cambc::shared_memory.size()) return i;
        return std::nullopt;
    }();
    return slot;
}

// How many teammates have claimed each group (stored as index + 1, 0 = none).
std::vector<int> teammate_claims(std::size_t groups) {
    std::vector<int> claims(groups, 0);
    const auto slot = my_slot();
    try {
        for (std::size_t i = 0; i < cambc::shared_memory.size(); ++i) {
            if (slot && i == *slot) continue;
            const std::uint8_t value = cambc::shared_memory[i];
            if (value > 0 && value <= groups) ++claims[value - 1];
        }
    } catch (const std::exception&) {
    }
    return claims;
}

// Expected rounds of hitting to clear a group alone, with fighting-back camps
// priced higher because their damage sends us home to heal.
float clear_rounds(const CampGroupInfo& info, float strength) {
    float work = 0.0f;
    for (const auto& camp : info.group)
        work += camp_health(camp.kind()) * (hits_back(camp.kind()) ? config::plan_hits_back_cost : 1.0f);
    return work / strength;
}

}  // namespace

std::optional<std::size_t> choose_target(ChampionState& state) {
    farming::refresh(state);
    auto& me = cambc::self();
    const auto& layout = *state.camp_layout;
    if (layout.empty()) return std::nullopt;

    // The full-map distance search is the expensive part of a turn: keep the
    // current target for plan_interval rounds unless it went on respawn.
    const auto now = cambc::round_number();
    if (state.target && now < state.next_plan_round) {
        const auto blocked = state.unavailable_until.find(*state.target);
        if (blocked == state.unavailable_until.end() || blocked->second <= now) return state.target;
    }
    state.next_plan_round = now + config::plan_interval;
    const bool allow_monolith = farming::team_ready_for_monolith(me);
    const float strength = std::max(1.0f, me.strength());
    const auto claims = teammate_claims(layout.size());

    cambc::bitboard roots;
    roots.set(me.position());
    cambc::bitboard reached;
    cambc::distance_field distance;
    distance.compute(terrain(), roots, reached);

    std::optional<std::size_t> best;
    float best_score = 0.0f;
    for (std::size_t index = 0; index < layout.size(); ++index) {
        const auto& info = layout[index];
        if (info.monolith && !allow_monolith) continue;

        float travel = -1.0f;
        for (auto tile : info.tile_list)
            if (reached.is_set(tile)) {
                const float d = distance.get(tile);
                if (travel < 0.0f || d < travel) travel = d;
            }
        if (travel < 0.0f) continue;

        // A respawning group is fine if it is back by the time we arrive.
        float start = travel;
        if (const auto blocked = state.unavailable_until.find(index); blocked != state.unavailable_until.end())
            if (blocked->second > now) start = std::max(start, static_cast<float>(blocked->second - now));

        const float value = static_cast<float>(info.group.gem_value())
                          + config::plan_gold_weight * static_cast<float>(info.group.gold_value());
        // A teammate who claimed a group that hits back will fight it with us.
        // Only one helper counts: counting all of them pulled the whole team
        // onto one elk group for 400 rounds on monolith.
        const bool dangerous = std::any_of(info.group.begin(), info.group.end(),
                                           [](const cambc::camp& camp) { return hits_back(camp.kind()); });
        const int helpers = dangerous ? std::min(claims[index], config::plan_max_helpers) : 0;
        if (dangerous && claims[index] > config::plan_max_helpers) continue;  // already crowded
        const float fighters = 1.0f + static_cast<float>(helpers);

        // Reflection 1 — survivability: never pick a group that would kill us
        // before it dies (v10 first draft died 70 times on elkring soloing elks).
        if (expected_damage(info, strength, fighters) > me.health() * config::plan_max_damage_fraction) continue;

        const float rounds = start + clear_rounds(info, strength) / fighters
                           + static_cast<float>(cambc::constants::capture_time);
        float score = value / rounds;

        // Reflection 2 — stay committed unless something is clearly better, and
        // spread out over harmless clusters rather than queue behind a teammate.
        if (state.target && *state.target == index) score *= config::plan_commit_bonus;
        if (!dangerous && claims[index] > 0) score *= config::plan_claimed_factor;

        if (score > best_score) {
            best = index;
            best_score = score;
        }
    }
    state.target = best;
    return best;
}

cambc::bitboard goal_tiles(const ChampionState& state, std::size_t target) {
    const auto& info = (*state.camp_layout)[target];
    const auto blocked = state.unavailable_until.find(target);
    if (blocked != state.unavailable_until.end() && blocked->second > cambc::round_number()) {
        cambc::bitboard ring;
        for (auto tile : info.tile_list) ring |= navigation::tiles_around(tile, config::plan_wait_radius);
        return ring & ~info.tiles;
    }
    // Walk into attack range of every camp still standing; once all are dead,
    // onto the spawn tiles to capture. Standing on a dead camp's tile used to
    // count as "arrived" while its neighbour was still alive two tiles away.
    const auto visible = cambc::vision::visible_tiles();
    const int range = cambc::self().attack_range();
    cambc::bitboard reach;
    for (const auto& camp : info.group) {
        try {
            if (camp.is_visible()) {
                if (camp.is_alive()) reach |= navigation::tiles_around(camp.position(), range);
            } else if (!visible.is_set(camp.spawn_position())) {
                reach |= navigation::tiles_around(camp.spawn_position(), range);
            }
        } catch (const std::exception&) {
        }
    }
    return reach.is_empty() ? info.tiles : reach;
}

bool worth_fighting(const ChampionState& state, const cambc::camp& camp) {
    try {
        if (camp.is_monolith() && !farming::team_ready_for_monolith(cambc::self())) return false;
        if (camp.is_gem_cluster() || camp.is_gold_cluster() || camp.is_awake()) return true;
        if (!state.target || !state.camp_layout) return false;
        return (*state.camp_layout)[*state.target].group == camp.camp_group();
    } catch (const std::exception&) {
        return false;
    }
}

void publish_claim(std::optional<std::size_t> target) {
    const auto slot = my_slot();
    if (!slot) return;
    const std::uint8_t value = target && *target < 255 ? static_cast<std::uint8_t>(*target + 1) : 0;
    try {
        if (static_cast<std::uint8_t>(cambc::shared_memory[*slot]) != value) cambc::shared_memory[*slot] = value;
    } catch (const std::exception&) {
    }
}

}  // namespace planner
