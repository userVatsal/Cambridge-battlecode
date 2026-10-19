// Target selection, basic attacks and ability casting.
#pragma once
#include <cambc.h>

#include <optional>
#include <vector>

namespace combat {

// Health of a unit, or 0 if it has died or left vision since we listed it.
// A camp killed earlier this turn still sits in our lists, and reading its
// health throws "Unit is not in vision" — which used to abort the whole turn.
inline float health_of(const cambc::unit& unit) {
    try {
        return unit.is_visible() ? unit.health() : 0.0f;
    } catch (const std::exception&) {
        return 0.0f;
    }
}

template <class Unit>
std::vector<Unit> alive_visible(const std::vector<Unit>& units) {
    std::vector<Unit> result;
    for (const auto& unit : units)
        if (health_of(unit) > 0.0f) result.push_back(unit);
    return result;
}

template <class Unit>
std::vector<Unit> in_mask(const std::vector<Unit>& units, const cambc::bitboard& mask) {
    std::vector<Unit> result;
    for (const auto& unit : units) {
        try {
            if (mask.is_set(unit.position())) result.push_back(unit);
        } catch (const std::exception&) {
        }
    }
    return result;
}

// Focus fire: the lowest-health unit dies first and stops dealing damage.
template <class Unit>
std::optional<Unit> pick_target(const std::vector<Unit>& units) {
    std::optional<Unit> best;
    float best_health = 0.0f;
    for (const auto& unit : units) {
        const float health = health_of(unit);
        if (health <= 0.0f) continue;
        if (!best || health < best_health) {
            best = unit;
            best_health = health;
        }
    }
    return best;
}

std::vector<cambc::champion> enemies_in_attack_range();
std::vector<cambc::camp> camps_in_attack_range();

template <class Unit>
bool basic_attack(const std::vector<Unit>& targets) {
    auto& me = cambc::self();
    const auto target = pick_target(targets);
    if (!target || !me.can_attack()) return false;
    try {
        me.attack(*target);
        return true;
    } catch (const std::exception&) {
        return false;
    }
}

bool cast_offensive();
bool cast_attack_reset();
bool cast_self_shield();
bool cast_ally_heal();

// Full combat sequence against targets already in basic-attack range: spell
// first (most spells exclude walking, and we do not walk while a target is in
// range), then attack, then attack-reset for a second hit.
template <class Unit>
bool fight(const std::vector<Unit>& targets) {
    if (targets.empty()) return false;
    cast_self_shield();
    cast_offensive();
    const bool hit = basic_attack(targets);
    if (hit && cast_attack_reset()) basic_attack(alive_visible(targets));
    return hit;
}

// Free actions every turn: heals and shields.
void support();

}  // namespace combat
