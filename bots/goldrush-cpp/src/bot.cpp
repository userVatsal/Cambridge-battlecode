#include "bot.h"

#include <algorithm>

#include "combat.h"
#include "config.h"
#include "economy.h"
#include "farming.h"
#include "navigation.h"

namespace {

using cambc::team;

void record_move(ChampionState& state, const cambc::champion& me) {
    state.recent_moves.push_back(me.position());
    if (state.recent_moves.size() > config::stuck_window)
        state.recent_moves.erase(state.recent_moves.begin(),
                                 state.recent_moves.end() - static_cast<std::ptrdiff_t>(config::stuck_window));
}

bool is_looping(const ChampionState& state) {
    if (state.recent_moves.size() < config::stuck_window) return false;
    auto tiles = state.recent_moves;
    std::sort(tiles.begin(), tiles.end());
    const auto distinct = std::unique(tiles.begin(), tiles.end()) - tiles.begin();
    return static_cast<std::size_t>(distinct) <= config::stuck_max_tiles;
}

bool is_busy(const cambc::champion& me) {
    return !me.is_alive() || me.is_recalling() || me.is_submitting_gems() || me.is_teleporting();
}

// Any enemy champion or awake camp close enough to cancel a recall.
bool threatened(const cambc::champion& me) {
    const auto position = me.position();
    for (const auto& enemy : cambc::vision::champions(team::enemy)) {
        try {
            if (combat::health_of(enemy) > 0.0f && position.chebyshev_distance(enemy.position()) <= 4) return true;
        } catch (const std::exception&) {
        }
    }
    for (const auto& camp : cambc::vision::camps()) {
        try {
            if (camp.is_awake() && position.chebyshev_distance(camp.position()) <= 3) return true;
        } catch (const std::exception&) {
        }
    }
    return false;
}

// The engine throws "Champion cannot act" if a channel is already running or
// the champion was stunned this turn; that must not end the turn.
void recall(const cambc::champion& me) {
    try {
        me.recall();
    } catch (const std::exception&) {
    }
}

std::vector<cambc::camp> farmable(std::vector<cambc::camp> camps) {
    const bool allow_monolith = farming::team_ready_for_monolith(cambc::self());
    if (allow_monolith) return camps;
    std::erase_if(camps, [](const cambc::camp& camp) { return camp.is_monolith(); });
    return camps;
}

}  // namespace

void Bot::play_turn() {
    auto& me = cambc::self();

    // Dead champions still get a turn: use it to shop.
    if (!me.is_alive()) {
        economy::buy_items(state_);
        return;
    }
    if (is_busy(me)) return;

    if (navigation::at_spawn()) economy::buy_items(state_);

    combat::support();

    // Low health away from spawn: step out of danger, then recall
    // (damage interrupts a recall, so do not start one under fire).
    if (!navigation::at_spawn() && me.health() < me.max_health() * config::recall_health) {
        if (threatened(me))
            navigation::move_home();
        else
            recall(me);
        return;
    }

    // Enemy champions in range take priority: kills steal their gems.
    if (const auto enemies = combat::enemies_in_attack_range(); !enemies.empty()) {
        combat::fight(enemies);
        return;
    }

    if (economy::should_bank(me)) {
        economy::bank_gems();
        return;
    }

    if (me.gold_count() >= config::shop_trip_gold && !navigation::at_spawn() && !threatened(me)) {
        recall(me);
        return;
    }

    if (const auto camps = farmable(combat::camps_in_attack_range()); !camps.empty()) {
        combat::fight(camps);
        return;
    }

    if (is_looping(state_)) {
        farming::block_nearby_groups(state_, config::stuck_block_rounds);
        state_.recent_moves.clear();
    }
    if (farming::advance_to_camps(state_)) {
        record_move(state_, me);
        combat::fight(farmable(combat::camps_in_attack_range()));
    }
}
