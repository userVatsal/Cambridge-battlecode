#include "economy.h"

#include <optional>

#include "config.h"
#include "navigation.h"

using cambc::item_type;

namespace config {

static std::vector<item_type> make_build(item_type emblem, item_type second, item_type rest) {
    std::vector<item_type> build;
    build.insert(build.end(), 5, emblem);
    build.insert(build.end(), 5, second);
    build.insert(build.end(), 30, rest);
    return build;
}

const std::vector<item_type>& build_for(cambc::champion_type champion) {
    static const auto strength = make_build(item_type::jungle_shard_of_strength,
                                            item_type::power_shard_of_health, item_type::power_shard_of_strength);
    static const auto focus = make_build(item_type::jungle_shard_of_focus,
                                         item_type::power_shard_of_health, item_type::power_shard_of_focus);
    static const auto tank = make_build(item_type::jungle_shard_of_health,
                                        item_type::power_shard_of_strength, item_type::power_shard_of_health);
    using cambc::champion_type;
    switch (champion) {
        case champion_type::ryth:
        case champion_type::marcella:
            return tank;
        case champion_type::stellar:
        case champion_type::tavi:
        case champion_type::prism:
        case champion_type::cassi:
        case champion_type::willow:
            return focus;
        default:
            return strength;  // varg, vendetta, vesper_vale, issac, ren
    }
}

}  // namespace config

namespace economy {

void buy_items(ChampionState& state) {
    auto& me = cambc::self();
    const auto& build = config::build_for(me.champion_name());
    while (state.build_index < build.size()) {
        const auto item = build[state.build_index];
        try {
            if (!me.can_buy(item, 1)) return;
            me.buy(item, 1);
        } catch (const std::exception&) {
            return;
        }
        ++state.build_index;
    }
}

static std::optional<int> nearest_altar_distance(cambc::vec2 position) {
    std::optional<int> best;
    for (auto altar : cambc::map::altars().positions()) {
        const int distance = static_cast<int>(position.chebyshev_distance(altar));
        if (!best || distance < *best) best = distance;
    }
    return best;
}

bool should_bank(const cambc::champion& me) {
    const auto gems = me.gem_count();
    if (gems == 0) return false;
    if (gems >= config::bank_gems || me.health() < me.max_health() * config::bank_health) return true;
    const auto altar = nearest_altar_distance(me.position());
    return altar && *altar <= config::bank_if_altar_within;
}

struct AltarApproach {
    cambc::vec2 altar;
    cambc::bitboard tiles;  // altars never move, so their approach tiles are built once
};

static const std::vector<AltarApproach>& altar_approaches() {
    static const auto approaches = [] {
        std::vector<AltarApproach> result;
        for (auto altar : cambc::map::altars().positions())
            result.push_back({altar, navigation::tiles_around(altar, cambc::constants::submit_gems_range)});
        return result;
    }();
    return approaches;
}

bool bank_gems() {
    auto& me = cambc::self();
    const int range = cambc::constants::submit_gems_range;
    cambc::bitboard goals;
    for (const auto& [altar, approach] : altar_approaches()) {
        if (cambc::vision::has_altar_lock(altar)) continue;
        if (static_cast<int>(me.position().chebyshev_distance(altar)) <= range) {
            try {
                me.submit_gems(altar);
                return true;
            } catch (const std::exception&) {
                continue;
            }
        }
        goals |= approach;
    }
    return navigation::move_towards_closest(goals);
}

}  // namespace economy
