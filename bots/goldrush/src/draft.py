"""Draft phase: deterministic priority picks."""
import cambc

import config


def choose_pick(already_ours, priority=config.DRAFT_PRIORITY):
    """Return the highest-priority champion we do not already own."""
    for pick in priority:
        if pick not in already_ours:
            return pick
    return None


def play():
    ours = list(cambc.draft.current_draft(cambc.Team.ALLY))
    if not ours:
        cambc.draft_memory.submit(config.VERSION)
    pick = choose_pick(ours)
    if pick is not None:
        cambc.draft.pick(pick)
