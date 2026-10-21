#include "bot.h"

#include <algorithm>
#include <iostream>

#include "combat.h"
#include "config.h"
#include "economy.h"
#include "farming.h"
#include "navigation.h"
#include "planner.h"

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

std::vector<cambc::camp> worth_fighting(const ChampionState& state, std::vector<cambc::camp> camps) {
    std::erase_if(camps, [&](const cambc::camp& camp) { return !planner::worth_fighting(state, camp); });
    return camps;
}

}  // namespace

// A turn has two stages, in the spirit of a hybrid "deterministic pipeline +
// agent" design. Stage 1 is a fixed list of guards, first match wins: they
// cover everything that must not go wrong (survival, banking, shopping, fights
// already in range) and are plain rules. Stage 2 only runs when no guard fired:
// the planner picks the camp group worth the next stretch of rounds.
void Bot::play_turn() {
    auto& me = cambc::self();
    if (guards(me)) return;

    // Stage 2: plan, publish the claim so teammates spread out, then act.
    if (is_looping(state_)) {
        farming::block_nearby_groups(state_, config::stuck_block_rounds);
        state_.recent_moves.clear();
    }
    const auto target = planner::choose_target(state_);
    planner::publish_claim(target);
    if (cambc::round_number() % 25 == 0) std::cout << "DBG r" << cambc::round_number() << " " << (int)me.champion_name() << " @" << me.position().x << "," << me.position().y << " hp" << me.health() << " gems" << me.gem_count() << " tgt" << (target ? (int)*target : -1) << std::endl;
    if (!target) return;
    if (navigation::move_towards_closest(planner::goal_tiles(state_, *target))) {
        record_move(state_, me);
        combat::fight(worth_fighting(state_, combat::camps_in_attack_range()));
    }
}

// Stage 1. Returns true if a guard used the turn.
bool Bot::guards(cambc::champion& me) {
    // Any guard but the camp fight means we are not farming our target now.
    const auto stop = [] {
        planner::publish_claim(std::nullopt);
        return true;
    };

    // Dead champions still get a turn: use it to shop.
    if (!me.is_alive()) {
        economy::buy_items(state_);
        return stop();
    }
    if (is_busy(me)) return stop();

    if (navigation::at_spawn()) economy::buy_items(state_);

    // Spawn heals only at the end of a turn spent on it. Walking off in the
    // arrival turn left hurt champions unhealed one tile outside spawn, so they
    // recalled again every 6 rounds for the rest of the match (ladder replays).
    if (navigation::at_spawn() && me.health() < me.max_health() * config::leave_spawn_health) return stop();

    combat::support();

    // Low health away from spawn: step out of danger, then recall
    // (damage interrupts a recall, so do not start one under fire).
    if (!navigation::at_spawn() && me.health() < me.max_health() * config::recall_health) {
        if (threatened(me))
            navigation::move_home();
        else
            recall(me);
        return stop();
    }

    // Enemy champions in range take priority: kills steal their gems.
    if (const auto enemies = combat::enemies_in_attack_range(); !enemies.empty()) {
        combat::fight(enemies);
        return stop();
    }

    if (economy::should_bank(me)) {
        economy::bank_gems();
        return stop();
    }

    if (me.gold_count() >= config::shop_trip_gold && !navigation::at_spawn() && !threatened(me)) {
        recall(me);
        return stop();
    }

    if (const auto camps = worth_fighting(state_, combat::camps_in_attack_range()); !camps.empty()) {
        combat::fight(camps);
        return true;
    }
    return false;
}
