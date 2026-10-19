# Problem statement and solutions

## The problem

Write an autonomous program that controls a team of 3–5 "champions" in a turn-based,
two-team strategy game on a 30×30 to 100×100 grid.

- **Goal:** be the first team to *tribute* 1,000 gems at altars. At round 2,000 the team
  with more tributed gems wins (tiebreaks: lifetime gold, then kills).
- **Gems and gold come from camps** — neutral monsters (wolf, elk, gem/gold clusters,
  monolith). Kill every monster in a connected group, then stand on one of its tiles
  uncontested for 5 rounds to capture the reward. The group respawns 40–150 rounds later.
- **Carried gems are fragile:** killed by a camp → gems destroyed; killed by an enemy →
  the enemy takes them. Only tributed gems count.
- **Gold buys power:** shards (+stats) bought on the spawn tiles; five matching shards form
  an emblem with a passive bonus.
- **Draft:** both teams pick champions one by one before the match; each champion has two
  abilities with 8-turn cooldowns.
- **Constraints:** every champion runs as its own bot instance with a per-turn compute
  ("fuel") budget; vision is per-champion and blocked by walls/bushes; teammates share only
  8 bytes of memory during the match (plus 1 KB written during the draft).

## Sub-problems and how goldrush solves them

File names below are the Python bot; the C++ bot mirrors them one-to-one
(`draft.py` → `draft.cpp`, `config.py` → `config.h`, and so on).

| # | Sub-problem | Starter bot | goldrush solution | Where |
| --- | --- | --- | --- | --- |
| 1 | Which champions to pick | random | Fixed priority list favouring tanky, splash and AoE farmers (Varg, Ryth, Stellar, Marcella…) | `draft.py`, `config.DRAFT_PRIORITY` |
| 2 | Killing camps fast | basic attacks only | Casts damage/stun/AoE spells, then attack, then attack-reset for a second hit; focus-fires the lowest-health target | `combat.fight` |
| 3 | Staying alive | recall at 35% | Self-shield when hurt, ally heals, and never starts a recall under fire (damage cancels it) — walks home first | `combat.support`, `bot._threatened` |
| 4 | Not suiciding into monoliths | farms everything | Skips 200-gem monolith groups until the team is strong and late | `farming.py` |
| 5 | Losing carried gems | banks every gem immediately | Banks at 30 gems, when an altar is close, or when health drops below 60% | `economy.should_bank` |
| 6 | Spending gold well | one random stat forever | Per-champion build: Jungle emblem first (−30% camp damage), then Power shards | `config.BUILDS` |
| 7 | Tempo | — | No dedicated recall-to-shop trips: they cost more farming time than the items repay | `config.SHOP_TRIP_GOLD` |
| 8 | Crashes | — | Each turn wrapped in a guard so one exception never forfeits the match | `main.py` |
| 9 | Knowing if a change helps | — | Deterministic batch evaluator on all 9 maps from both sides | `tools/run_matches.py` |

## Known weaknesses (next work)

- **Monolith map, Team A side** — lost 996–1012. Monolith groups are skipped all game; a
  timed full-team monolith attempt could flip it.
- **No coordination** — champions can bunch on one camp. Shared memory (8 bytes) could
  claim camps so champions spread out.
- **No real PvP logic** — we only hit enemies already in range. Real ladder opponents will
  fight; we need retreat/engage decisions and altar locks.
- **Draft ignores the map and the opponent's picks.** The draft phase sees the full map.
- **Dashes and wards are unused.**
