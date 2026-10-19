// Draft phase: deterministic priority picks.
#pragma once
#include <cambc.h>

#include <optional>
#include <vector>

// Highest-priority champion we do not already own, if any is left.
std::optional<cambc::champion_draft> choose_pick(const std::vector<cambc::champion_draft>& already_ours);

void play_draft();
