# Ladder match log

Living record of every ladder match group we download: what happened, why we won or lost,
and what we changed. **Add a new section at the top each time** (newest first).

How to regenerate the numbers: see [Analysing ladder replays](#analysing-ladder-replays) at the bottom.

---

## 19 Oct 2026, 20:00 — scouting data: 3,160 top-team games → ships **v9**

Downloaded with `make scout` (12 top ladder teams, up to 300 matches each), analysed with
`python tools/analyse_scout.py data`.

| Team | Win rate |
| --- | --- |
| Intercontinental Fish | 92% |
| Univardisty of Shingtonwash | 89% |
| Nyx | 82% |

| Per champion (median) | Winners | Losers |
| --- | --- | --- |
| Deaths | 0 | 1 |
| Kills | 1 | 0 |
| Gold earned | 840 | 460 |
| Gold spent | 750 | 430 |
| Gems collected | 196 | 102 |
| Gems tributed | 178 | 66 |

What it means:

- **Draft barely matters.** Once each team's own win rate is subtracted, every champion is
  within about ±0.5 points; Stellar as first pick is the best at +1.1. No draft change.
- **Winners spend their gold** (about 90% of it). We had stopped shopping in v2, so our gold sat
  unused. v9 recalls to shop at 150 unspent gold: 12 / 18 vs v8, 18 / 18 vs starter.
- **Winners don't die** (median 0 deaths) and tribute almost every gem they collect.
- Top teams' item build (Power main stat, then Durability, then Power; Tavi opens Monster Focus)
  did not help our bot: 7 / 18 vs v8. Stat priorities alone: 9 / 18. Both rejected.

---

## 19 Oct 2026, 14:30 — v5 vs 10 top teams (10 groups, 50 games) → ships **v8**

We are the losing side in 49 of 50 (old draft Varg, Ryth, Stellar, Marcella, Tavi; all played
with the v5 spawn-healing bug that v6 fixed). One win: `fa46338f` game 1, 1015–794.

| What winners pick | Count in 49 winning drafts |
| --- | --- |
| Tavi | 66 picks* · Stellar 46 · Cassi+Issac 38 · Ren 31 · Ryth 31 · Varg 22 |
| First pick | Cassi+Issac 25 · Ren 8 · Ryth 6 · Stellar 5 · Varg 4 |
| Marcella | 1 winning draft vs 31 losing |

*decoder counts some 4-pick maps oddly; ranking is what matters.

- Winners carry more gems per hand-in (median 36–66 vs our 22–36), but copying that keeps
  losing locally (60 gems: 9/18; 45 gems: 9/18).
- Several 0–1000 losses on the 22-camp map again: we tribute nothing while they farm.

**Changed (v8):** draft Cassi+Issac, Stellar, Ren, Tavi, Ryth first. 11/18 vs v7, 18/18 vs starter.

---

## 19 Oct 2026, 14:15 — vs the top UK team (group `2f59cacd`, 5 games), bot v5 (C++) → ships **v7**

### Scoreboard: lost 0–5

We are Team A in all five (our draft; our C++ bot printed no errors and no fuel warnings).
Their team name is not in the files; they draft **Cassi+Issac, Varg, Stellar, Ren, Tavi**.

| Game | Map size (camps) | Rounds | Gems us–them | Kills us–them | Gems at round 200 |
| --- | --- | --- | --- | --- | --- |
| 1 | 100×97 (38) | 581 | 606–1034 | 0–0 | 178–178 |
| 2 | 32×41 (24) | 528 | 330–1058 | 0–3 | 66–300 |
| 3 | 50×48 (22) | 2000 | 0–0 (lost tiebreak) | 1–68 | 0–0 |
| 4 | 71×71 (42) | 387 | 392–1020 | 1–3 | 102–312 |
| 5 | 41×28 (20) | 364 | 94–1014 | 0–6 | 58–306 |

### What they do differently (measured from the replays)

| | Us (v5) | Top team |
| --- | --- | --- |
| Champions on the map | 5 | **6** — Cassi+Issac is one pick, two bodies |
| Average health, first 400 rounds | 48–75% | 75–87% |
| Gems carried per hand-in (median) | 22–36 | 44–89 |
| Team spread | similar | similar |

### Why we lost — the big one was a bug

**Recall loop at spawn.** A hurt champion recalls, lands on a spawn tile, buys items and then
walks off **in the same turn**. Spawn only heals at the end of a turn spent on it, so it ends
the turn unhealed one tile outside spawn, is still below 35% health, and recalls again — every
6 rounds, forever. Game 5: our Stellar sat at 210/750 health on tile (1,13) from round 31 to the
end, and Marcella at 120/1200 beside it — two of five champions out of the game. Game 3: Ryth
made 212 recalls. Game 1: Varg 83. The same loop showed up locally once we looked for it.

The 22-camp map (game 3) is still a bloodbath (68 deaths); that needs fight/retreat work.

### What we changed

| Version | Change | Result |
| --- | --- | --- |
| v6 | Stay on spawn until ≥ 90% health (`leave_spawn_health`) | **14 / 18 vs v5**, **18 / 18 vs starter** (first perfect score) |
| v7 | Draft Cassi+Issac first, then Varg, Stellar, Ren, Tavi (copied from the top team) | 10 / 18 vs v6 (marginal), 18 / 18 vs starter |
| rejected | Bank later (60 gems, altar within 4) to copy their bigger hand-ins | 9 / 18 vs v6 |

### Next

1. Get their *score* on the 22-camp map: fight/retreat logic so we stop feeding 68 kills.
2. Watch the next ladder games for whether v7's draft actually helps against real teams.

---

## 18 Oct 2026, 22:30 — 5 match groups (25 games), bot v2/v3 → ships **v4**

### Scoreboard

| Group | Result | Bot version |
| --- | --- | --- |
| G1 (`632458c4`) | **Won 3–2** | v2 |
| G2 (`46702b7a`) | Lost 2–3 | v2 |
| G3 (`985e78fe`) | Lost 0–5 | v2/v3 |
| G4 (`c40f68eb`) | Lost 0–5 | v2/v3 |
| G5 (`dd9f27ee`) | Lost 0–5 | v2/v3 |

**Total: 5 wins, 20 losses.** Opponent team names are not stored in the downloaded files
(only on the platform's match page); opponents are identified here by their draft.

### Every game

Gems, kills and deaths are written *us–them*. "Camps" is the number of monsters on the map,
which identifies the map (the ladder uses maps that are **not** in our local 9-map pool).

| Game | Result | Our side | Camps | Rounds | Gems | Kills | Deaths | Opponent draft |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| G1-1 | **W** | B | 52 | 892 | 1002–750 | 0–0 | 0–0 | Cassi+Issac, Stellar, Ren, Tavi, Tavi |
| G1-2 | L | B | 42 | 904 | 954–1010 | 4–4 | 4–5 | Cassi+Issac, Stellar, Ren, Ryth, Varg |
| G1-3 | **W** | B | 42 | 766 | 1016–748 | 6–6 | 7–9 | Cassi+Issac, Stellar, Ren, Ryth, Varg |
| G1-4 | L | B | 22 | 2000 | 0–0 | 61–36 | 36–77 | Cassi+Issac, Stellar, Ren, Ryth, Varg |
| G1-5 | **W** | B | 20 | 549 | 1006–192 | 9–4 | 4–13 | Cassi+Issac, Stellar, Ren, Tavi, Tavi |
| G2-1 | L | A | 22 | 1980 | 0–1000 | 29–35 | 35–55 | Cassi+Issac, Ren, Stellar, Ryth, Varg |
| G2-2 | **W** | B | 80 | 529 | 1024–196 | 19–2 | 3–19 | Varg, Ryth, Stellar, Marcella, Tavi |
| G2-3 | **W** | A | 20 | 569 | 1008–810 | 4–7 | 8–4 | Ryth, Vesper, Stellar, Varg, Vendetta |
| G2-4 | L | A | 38 | 790 | 784–1026 | 0–3 | 3–0 | Tavi, Ryth, Stellar, Varg, Vendetta |
| G2-5 | L | A | 42 | 473 | 290–1018 | 2–6 | 6–4 | Cassi+Issac, Ren, Stellar, Ryth, Varg |
| G3-1 | L | B | 24 | 767 | 864–1050 | 2–8 | 8–2 | Stellar, Vesper, Tavi, Tavi, Tavi |
| G3-2 | L | B | 22 | 2000 | 0–400 | 3–55 | 55–5 | Stellar, Vesper, Tavi, Willow, Prism |
| G3-3 | L | B | 28 | 615 | 858–1023 | 0–0 | 0–0 | Varg, Stellar, Prism, Vesper, Tavi |
| G3-4 | L | B | 20 | 567 | 966–1054 | 2–2 | 2–2 | Varg, Stellar, Vesper, Tavi, Tavi |
| G3-5 | L | B | 44 | 441 | 380–1010 | 0–1 | 2–0 | Stellar, Varg, Vesper, Tavi, Prism |
| G4-1 | L | B | 12 | 683 | 361–1042 | 1–7 | 7–1 | Stellar, Prism, Ren, Tavi, Tavi |
| G4-2 | L | B | 44 | 454 | 498–1018 | 0–2 | 2–2 | Stellar, Varg, Cassi+Issac, Tavi, Ren |
| G4-3 | L | B | 28 | 554 | 704–1023 | 0–0 | 0–0 | Prism, Varg, Stellar, Ren, Tavi |
| G4-4 | L | B | 22 | 2000 | 0–400 | 2–55 | 55–2 | Stellar, Varg, Cassi+Issac, Tavi, Ren |
| G4-5 | L | B | 40 | 1613 | 0–1080 | 2–4 | 4–3 | Stellar, Prism, Ren, Cassi+Issac, Varg |
| G5-1 | L | B | 46 | 1016 | 0–1020 | 0–0 | 0–1 | Ryth, Varg, Vesper, Ren, Marcella |
| G5-2 | L | B | 80 | 703 | 36–1030 | 11–17 | 19–12 | Ryth, Varg, Stellar, Marcella, Tavi |
| G5-3 | L | B | 44 | 655 | 424–1032 | 1–9 | 9–1 | Ryth, Varg, Vesper, Ren, Marcella |
| G5-4 | L | B | 20 | 746 | 576–1008 | 6–13 | 15–6 | Ryth, Varg, Stellar, Marcella, Willow |
| G5-5 | L | B | 24 | 797 | 66–1012 | 2–10 | 10–2 | Marcella, Ryth, Stellar, Tavi, Tavi |

(Opponent picks are as decoded from the replay; a repeated name such as "Tavi, Tavi" is a
decoding quirk for one pick, not a real duplicate.)

### Why we lost — four causes, biggest first

**1. Champions stuck oscillating — 6 losses with 0–66 gems tributed (G2-1, G4-4, G4-5, G5-1,
G5-2, G5-5).** Decoding positions showed our champions walking out of spawn and then staying
inside a 2–3 tile area for 500–1,000 rounds at full health, making a move every single turn
(231 moves in 50 rounds, zero distance gained). Cause: a camp group was dropped as a target
only while it was *visible and respawning*. One step back it left vision, became a target
again, the champion stepped forward, saw it respawning, stepped back… forever. Our local maps
never triggered it, so local testing missed it.

**2. The 22-camp map is a bloodbath — 4 losses (G1-4, G2-1, G3-2, G4-4).** Both teams die
35–77 times and almost nobody tributes; G1-4 ended 0–0 and we lost on the tiebreak. Our
"enemy in range → fight" rule runs before "go and bank gems", so carried gems are never
banked while enemies are around. Partly the same oscillation bug. Needs map-specific work.

**3. Losing fights — 5 losses with deaths far above kills (G3-1 2–8, G4-1 1–7, G5-3 1–9,
G5-4 6–13, G5-2 11–17).** We only react to enemies already in attack range and never retreat
when outnumbered, so grouped opponents pick our champions off one by one and take their gems.

**4. Simply out-farmed — 7 close losses with few or no deaths (G1-2, G2-4, G3-3, G3-4, G4-3,
plus fast losses G2-5, G3-5, G4-2 on 42/44-camp maps).** The best opponents reach 1,000 gems
by round ~450 on those maps; we are ~50–100 rounds slower.

### Why we won

G1-1, G1-3, G1-5, G2-2, G2-3: opponents that died a lot (13–19 deaths in G1-5 and G2-2) or
farmed slowly. Zero-death farming plus the 30-gem banking rule beats careless bots.

### Opponent trends

- **Stellar is in almost every opponent draft** (23 of 25 games) — AoE farming is the meta.
- Ryth and Varg (our first two picks) are taken by most strong opponents too.
- Tavi, Ren and Cassi+Issac show up often in the teams that beat us.

### What we changed → v4

| Change | Fixes cause | Where |
| --- | --- | --- |
| Remember each camp group's respawn timer after it leaves vision; never re-target it until the timer runs out | 1 | `farming.camp_goals` |
| Anti-loop safety net: if a champion keeps moving but visits ≤3 tiles in 12 turns, skip nearby groups for 40 rounds | 1 (any future variant) | `bot._is_looping`, `farming.block_nearby_groups` |
| If every known group is respawning, walk to the one that returns soonest instead of idling | 1, 4 | `farming.advance_to_camps` |
| (v3) Dead-camp health reads and failed recalls no longer end the turn | lost turns | `combat._health`, `bot._recall` |

Local tests (our 9 maps): v4 vs v3 **8/18** (a draw — v3 never looped on these maps, so this is
the expected "no regression" result); v4 vs starter **17/18**. Tried and *not* shipped: retreat
when outnumbered below 70% health — 9/18 vs v4, no evidence yet.

### Next, in priority order

1. Retreat when outnumbered; bank carried gems before engaging (causes 2 and 3).
2. Get the real ladder map pool locally (`cambc maps pull` from a normal network) and re-test.
3. Faster farming on 42/44-camp maps (cause 4): spread champions across camps.

---

## Analysing ladder replays

1. Download a match group ZIP from the platform and unzip it (each game is a ZIP containing
   `replay.repl26a` and our team's `stdout`, `fuel` and `debug` logs).
2. `grep "goldrush error" */team-*.stdout | sort | uniq -c` — any lines here are bugs.
3. Decode replays to JSON with the public decoder from
   [FHL-08/Tarot-Club-Cambc2026](https://github.com/FHL-08/Tarot-Club-Cambc2026)
   (`tools/replay/extract.mjs`). Current ladder replays need the **v0_0_3** engine WASM from
   `cambc view`'s assets; the decoder's default picks v0_0_1 and fails with "engine error 11".
4. `python tools/analyse_replays.py <decoded-json-dir>` prints the table above.
