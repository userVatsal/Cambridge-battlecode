# goldrush strategy

## Turn priorities (`bot.cpp` / `bot.py`)

Every champion, every turn, takes the first branch that applies:

1. **Dead** → shop (dead champions still get a turn).
2. **Channelling** (recall, tribute, teleport) → do nothing; acting would cancel it.
3. **On spawn** → buy the next items in the build order.
4. **Support** → heal a hurt ally / shield self if those abilities are ready.
5. **Below 35% health** → walk home if anything is threatening, otherwise recall.
6. **Enemy champion in attack range** → fight it (kills steal their carried gems).
7. **Should bank** (≥30 gems, altar within 8 tiles, or below 60% health) → walk to an altar
   and tribute.
8. **Camp in attack range** → fight it.
9. **Otherwise** → walk towards the nearest camp group that is alive or unscouted, and
   attack if that step brought a camp into range.

## Fight sequence (combat.fight)

shield if hurt → offensive spell on the weakest target in spell range → basic attack on the
weakest target in attack range → attack-reset spell → second basic attack.

## Evaluation rules

- Always test both sides: Team B acts second in round one and wins full ties.
- Matches are deterministic, so one run per map/side is real evidence.
- A change must beat the previous snapshot, not only the starter.

## Ideas backlog (ordered by expected value)

1. Camp claiming through shared memory so champions spread across camps.
2. Engage/retreat model for enemy champions (compare effective HP × damage).
3. Map-aware draft using the full map visible during the draft phase.
4. Coordinated late-game monolith attempts.
5. Altar locks to deny enemy tributes near the end of close games.
6. Dashes for chasing, escaping and crossing holes; wards on contested camps.
