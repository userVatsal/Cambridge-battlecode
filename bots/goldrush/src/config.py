"""Tunable strategy constants. Change numbers here, not inside the logic modules."""
import cambc

Draft = cambc.ChampionDraft
Champ = cambc.ChampionType
Item = cambc.ItemType

VERSION = b"goldrush-v9"

# Picked top-down, skipping anything we already own. The most common winning
# set across 49 ladder losses to the top teams: Cassi+Issac (one pick, two
# bodies), Stellar, Ren, Tavi, Ryth. Marcella was in 31 losing drafts, 1 win.
DRAFT_PRIORITY = (
    Draft.CASSI_AND_ISSAC,
    Draft.STELLAR,
    Draft.REN,
    Draft.TAVI,
    Draft.RYTH,
    Draft.VARG,
    Draft.VENDETTA,
    Draft.PRISM,
    Draft.VESPER_VALE,
    Draft.MARCELLA,
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
# Stay on spawn (healing) until at least this much health.
LEAVE_SPAWN_HEALTH = 0.9

# Gem banking: a camp kill destroys carried gems, so bank early.
BANK_GEMS = 30
BANK_IF_ALTAR_WITHIN = 8
BANK_HEALTH = 0.6

# Recall to shop once this much gold is unspent. Winners in 3,160 ladder games
# spend ~90% of the gold they earn. Trips lost before v6 only because of the
# spawn-healing bug; with it fixed, 150 gold beats never-shop 12/18.
SHOP_TRIP_GOLD = 150

# Camp groups worth at least this many gems are monoliths (200 gems, 20k HP,
# 200 strength) and only attempted once the team is strong.
MONOLITH_GEMS = 150
MONOLITH_MIN_MAX_HEALTH = 3000
MONOLITH_MIN_ROUND = 700

# Visible group whose state cannot be read: try it again after this many rounds.
UNKNOWN_GROUP_COOLDOWN = 20

# Anti-loop: if a champion keeps moving but visits at most STUCK_MAX_TILES
# distinct tiles over STUCK_WINDOW turns, nearby groups are skipped for
# STUCK_BLOCK_ROUNDS so it commits to a different target.
STUCK_WINDOW = 12
STUCK_MAX_TILES = 3
STUCK_BLOCK_ROUNDS = 40
STUCK_BLOCK_RADIUS = 10
