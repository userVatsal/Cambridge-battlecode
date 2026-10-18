"""Tunable strategy constants. Change numbers here, not inside the logic modules."""
import cambc

Draft = cambc.ChampionDraft
Champ = cambc.ChampionType
Item = cambc.ItemType

VERSION = b"goldrush-v2"

# Picked top-down, skipping anything we already own. Tanky splash/AoE farmers
# first: the game is a farming race, and dead champions drop their gems.
DRAFT_PRIORITY = (
    Draft.VARG,
    Draft.RYTH,
    Draft.STELLAR,
    Draft.MARCELLA,
    Draft.TAVI,
    Draft.VESPER_VALE,
    Draft.VENDETTA,
    Draft.REN,
    Draft.PRISM,
    Draft.CASSI_AND_ISSAC,
    Draft.WILLOW,
)

# Shards cost 30 gold; five matching shards combine into the family emblem.
# Jungle first (30% less camp damage) keeps farmers alive; Power after that.
_STRENGTH_BUILD = (Item.JUNGLE_SHARD_OF_STRENGTH,) * 5 + (Item.POWER_SHARD_OF_HEALTH,) * 5 \
    + (Item.POWER_SHARD_OF_STRENGTH,) * 30
_FOCUS_BUILD = (Item.JUNGLE_SHARD_OF_FOCUS,) * 5 + (Item.POWER_SHARD_OF_HEALTH,) * 5 \
    + (Item.POWER_SHARD_OF_FOCUS,) * 30
_TANK_BUILD = (Item.JUNGLE_SHARD_OF_HEALTH,) * 5 + (Item.POWER_SHARD_OF_STRENGTH,) * 5 \
    + (Item.POWER_SHARD_OF_HEALTH,) * 30

BUILDS = {
    Champ.VARG: _STRENGTH_BUILD,
    Champ.VENDETTA: _STRENGTH_BUILD,
    Champ.VESPER_VALE: _STRENGTH_BUILD,
    Champ.ISSAC: _STRENGTH_BUILD,
    Champ.REN: _STRENGTH_BUILD,
    Champ.RYTH: _TANK_BUILD,
    Champ.MARCELLA: _TANK_BUILD,
    Champ.STELLAR: _FOCUS_BUILD,
    Champ.TAVI: _FOCUS_BUILD,
    Champ.PRISM: _FOCUS_BUILD,
    Champ.CASSI: _FOCUS_BUILD,
    Champ.WILLOW: _FOCUS_BUILD,
}

# Health fractions.
RECALL_HEALTH = 0.35
SHIELD_HEALTH = 0.85
HEAL_ALLY_HEALTH = 0.65

# Gem banking: a camp kill destroys carried gems, so bank early.
BANK_GEMS = 30
BANK_IF_ALTAR_WITHIN = 8
BANK_HEALTH = 0.6

# Dedicated recall-to-shop trips. Testing showed they cost more farming time
# than the items repay (collision: lost at 1464 rounds with trips, won at 668
# without), so they are disabled: champions shop when low-health recalls or
# deaths bring them home anyway.
SHOP_TRIP_GOLD = 10**9

# Camp groups worth at least this many gems are monoliths (200 gems, 20k HP,
# 200 strength) and only attempted once the team is strong.
MONOLITH_GEMS = 150
MONOLITH_MIN_MAX_HEALTH = 3000
MONOLITH_MIN_ROUND = 700
