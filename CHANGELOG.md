# Changelog

Results are `make eval` against the official `starter-python` (9 maps × 2 sides = 18 games)
unless stated otherwise.

## v5 — C++ port (19 Oct 2026)

- `bots/goldrush-cpp`: file-for-file C++ port of Python v4. Python `bots/goldrush` kept as
  reference and fallback. Frozen as `bots/goldrush-cpp-v5`.
- First port used up to **91%** of the 100k C++ fuel budget (lanes; one turn ran out), versus
  ~50% of the 2.5M Python budget. Cause: full-map bitboard temporaries every turn in camp
  targeting (up to 102k fuel alone) and altar banking. Fix: check each group's 1-4 spawn tiles
  directly, and build altar approach masks once. Worst case now **67%** (corners), 0 turns out
  of fuel on all 9 maps.
- vs starter: **17 / 18**, 15 of 18 games move-for-move identical to Python v4 (elkring ×2 and
  interlock A differ slightly; same results). vs Python v4: **9 / 18** (equal strength).
  `errors=0 fuel_warnings=0` over 36 games.
- Bot now prints `goldrush warning: turn ran out of fuel` when a turn is cut short, and
  `make eval` reports error and fuel-warning counts.
- Added `CLAUDE.md` working rules (adapted from multica-ai/andrej-karpathy-skills) and a C++
  build job in CI.

## v4 — no more stuck champions (18 Oct 2026)

- Ladder analysis of 25 games (see `docs/MATCH_LOG.md`): 6 losses had 0–66 gems tributed
  because champions oscillated on the edge of vision next to a respawning camp group for
  500–1,000 rounds.
- Camp groups seen respawning are remembered until their timer runs out; anti-loop safety net
  (≤3 tiles visited in 12 moving turns → skip nearby groups for 40 rounds); when everything is
  respawning, pre-position on the group that returns first.
- vs starter: **17 / 18** (now wins monolith A; loses corners B). vs v3: 8 / 18 (draw on local
  maps, which never triggered the loop).

## v3 — crash-free (18 Oct 2026)

- First ladder match group (5 games) showed 169 caught errors in our logs, each one ending
  that champion's turn early: 162 × "Unit is not in vision" (reading the health of a camp
  killed earlier the same turn) and 7 × "Champion cannot act" (recall while unable to act).
- Health reads and recalls are now error-safe. Local runs: 0 errors (was 25 on two maps).
- vs starter: **17 / 18** (unchanged). vs v2: 8 / 18 — a draw; most maps are exact mirrors
  decided by which side moves second.

## Experiments (rejected)

- Retreat when outnumbered below 70% health: **9 / 18** vs v4 — no evidence it helps; revisit with ladder maps.
- Tank + healer core (draft Ryth, Willow, Tavi first): **6 / 18** head-to-head vs v2.
- Fuel check: worst turn on collision still had ~1.26M of the 2.5M Python budget left, so an
  emergency low-fuel fallback is not needed yet.
- Bank later (`BANK_GEMS=50`, `BANK_IF_ALTAR_WITHIN=5`): **7 / 18** head-to-head vs v2. Kept 30 / 8.

## v2 — Sprint 1 submission (18 Oct 2026)

- Frozen as `bots/goldrush-v2` — the baseline every new version must beat.

- Disabled recall-to-shop trips (`SHOP_TRIP_GOLD`). Collision went from a 1,464-round loss
  to a 668-round win; rows Team A also flipped to a win.
- **17 / 18 wins.** Only loss: monolith as Team A, 996–1012.

## v1

- Priority draft, ability casting (damage, stun, AoE, attack reset, shield, heal),
  per-champion item builds, monolith avoidance, threshold-based gem banking, safe recalls.
- **14 / 18 wins.** Losses: collision ×2, monolith A, rows A.
