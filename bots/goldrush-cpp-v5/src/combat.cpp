#include "combat.h"

#include "config.h"

namespace combat {

using cambc::team;

std::vector<cambc::champion> enemies_in_attack_range() {
    return in_mask(alive_visible(cambc::vision::champions(team::enemy)), cambc::self().attack_tiles());
}

std::vector<cambc::camp> camps_in_attack_range() {
    return in_mask(alive_visible(cambc::vision::camps()), cambc::self().attack_tiles());
}

// Cast and swallow engine errors, so one bad cast never ends the turn.
template <class Cast>
static bool try_cast(Cast&& cast) {
    try {
        return cast();
    } catch (const std::exception&) {
        return false;
    }
}

template <class Unit>
static bool cast_at_weakest(const cambc::ability& ability, const std::vector<Unit>& pool,
                            const cambc::bitboard& reach, bool ground_only) {
    const auto target = pick_target(in_mask(pool, reach));
    if (!target) return false;
    // Ground spells (area damage / area stun) aim at the target's tile.
    if (ground_only) return try_cast([&] { return ability.use(target->position()); });
    return try_cast([&] { return ability.use(*target); });
}

bool cast_offensive() {
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    const auto enemies = alive_visible(cambc::vision::champions(team::enemy));
    const auto camps = alive_visible(cambc::vision::camps());
    for (const auto& ability : me.abilities()) {
        try {
            if (!ability.is_ready()) continue;
            if (!(ability.is_damage() || ability.is_aoe_damage() || ability.is_cc())) continue;
            const auto reach = ability.valid_tiles();
            const bool ground = ability.can_target_ground();
            const bool ground_only = ground && !(ability.can_target_enemies() || ability.can_target_camps());
            if ((ability.can_target_enemies() || ground) && cast_at_weakest(ability, enemies, reach, ground_only))
                return true;
            if ((ability.can_target_camps() || ground) && cast_at_weakest(ability, camps, reach, ground_only))
                return true;
        } catch (const std::exception&) {
            continue;
        }
    }
    return false;
}

bool cast_attack_reset() {
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    for (const auto& ability : me.abilities()) {
        try {
            if (ability.is_ready() && ability.is_attack_reset()) return try_cast([&] { return ability.use(); });
        } catch (const std::exception&) {
        }
    }
    return false;
}

bool cast_self_shield() {
    auto& me = cambc::self();
    if (!me.can_cast() || me.health() > me.max_health() * config::shield_health) return false;
    for (const auto& ability : me.abilities()) {
        try {
            if (ability.is_ready() && ability.is_shield() && ability.can_target_self())
                return try_cast([&] { return ability.use(me); });
        } catch (const std::exception&) {
        }
    }
    return false;
}

bool cast_ally_heal() {
    auto& me = cambc::self();
    if (!me.can_cast()) return false;
    for (const auto& ability : me.abilities()) {
        try {
            if (!(ability.is_ready() && ability.is_heal())) continue;
            const auto reach = ability.valid_tiles();
            std::vector<cambc::champion> hurt;
            for (const auto& ally : in_mask(alive_visible(cambc::vision::champions(team::ally)), reach)) {
                if (ally == me) continue;
                if (health_of(ally) < ally.max_health() * config::heal_ally_health) hurt.push_back(ally);
            }
            const auto target = pick_target(hurt);
            if (target && try_cast([&] { return ability.use(*target); })) return true;
        } catch (const std::exception&) {
            continue;
        }
    }
    return false;
}

void support() {
    cast_ally_heal();
    cast_self_shield();
}

}  // namespace combat
