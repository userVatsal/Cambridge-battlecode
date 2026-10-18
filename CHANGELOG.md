# Changelog

Results are `make eval` against the official `starter-python` (9 maps × 2 sides = 18 games).

## Experiments (rejected)

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
