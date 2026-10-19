#include "draft.h"

#include <algorithm>

#include "config.h"

std::optional<cambc::champion_draft> choose_pick(const std::vector<cambc::champion_draft>& already_ours) {
    for (auto pick : config::draft_priority)
        if (std::find(already_ours.begin(), already_ours.end(), pick) == already_ours.end()) return pick;
    return std::nullopt;
}

void play_draft() {
    const auto ours = cambc::draft::current_draft(cambc::team::ally);
    if (ours.empty()) cambc::draft_memory = config::version;
    if (const auto pick = choose_pick(ours)) cambc::draft::pick(*pick);
}
