"""Target selection, basic attacks and ability casting."""
import cambc

import config

Team = cambc.Team


def _alive_visible(units):
    return [u for u in units if u.is_visible() and u.health() > 0]


def _in_mask(units, mask):
    return [u for u in units if mask.is_set(u.position())]


def pick_target(units):
    """Focus fire: the lowest-health unit dies first and stops dealing damage."""
    return min(units, key=lambda u: u.health()) if units else None


def enemies_in_attack_range():
    me = cambc.me()
    return _in_mask(_alive_visible(cambc.vision.champions(Team.ENEMY)), me.attack_tiles())


def camps_in_attack_range():
    me = cambc.me()
    return _in_mask(_alive_visible(cambc.vision.camps()), me.attack_tiles())


def basic_attack(targets):
    me = cambc.me()
    target = pick_target(targets)
    if target is None or not me.can_attack():
        return False
    try:
        me.attack(target)
        return True
    except cambc.Error:
        return False


def _try_cast(ability, target=None):
    try:
        return bool(ability.use(target))
    except (cambc.Error, ValueError, TypeError):
        return False


def cast_offensive(prefer_champions=True):
    """Cast the strongest ready damage/stun spell at a target inside its range."""
    me = cambc.me()
    if not me.can_cast():
        return False
    enemies = _alive_visible(cambc.vision.champions(Team.ENEMY))
    camps = _alive_visible(cambc.vision.camps())
    for ability in me.abilities():
        if not ability.is_ready():
            continue
        if not (ability.is_damage() or ability.is_aoe_damage() or ability.is_cc()):
            continue
        try:
            reach = ability.valid_tiles()
        except (cambc.Error, ValueError):
            continue
        pools = []
        if ability.can_target_enemies() or ability.can_target_ground():
            pools.append(_in_mask(enemies, reach))
        if ability.can_target_camps() or ability.can_target_ground():
            pools.append(_in_mask(camps, reach))
        if not prefer_champions:
            pools.reverse()
        for pool in pools:
            target = pick_target(pool)
            if target is None:
                continue
            # Ground spells (area damage / area stun) aim at the target's tile.
            aim = target.position() if ability.can_target_ground() and not (
                ability.can_target_enemies() or ability.can_target_camps()) else target
            if _try_cast(ability, aim):
                return True
    return False


def cast_attack_reset():
    me = cambc.me()
    if not me.can_cast():
        return False
    for ability in me.abilities():
        if ability.is_ready() and ability.is_attack_reset():
            return _try_cast(ability)
    return False


def cast_self_shield():
    me = cambc.me()
    if not me.can_cast() or me.health() > me.max_health() * config.SHIELD_HEALTH:
        return False
    for ability in me.abilities():
        if ability.is_ready() and ability.is_shield() and ability.can_target_self():
            return _try_cast(ability, me)
    return False


def cast_ally_heal():
    me = cambc.me()
    if not me.can_cast():
        return False
    for ability in me.abilities():
        if not (ability.is_ready() and ability.is_heal()):
            continue
        try:
            reach = ability.valid_tiles()
        except (cambc.Error, ValueError):
            continue
        hurt = [a for a in _in_mask(_alive_visible(cambc.vision.champions(Team.ALLY)), reach)
                if a != me and a.health() < a.max_health() * config.HEAL_ALLY_HEALTH]
        target = pick_target(hurt)
        if target is not None and _try_cast(ability, target):
            return True
    return False


def fight(targets):
    """Full combat sequence against targets already in basic-attack range.

    Spell first (most spells exclude walking, and we are not walking while a
    target is in range), then attack, then attack-reset for a second hit.
    """
    if not targets:
        return False
    cast_self_shield()
    cast_offensive(prefer_champions=True)
    hit = basic_attack(targets)
    if hit and cast_attack_reset():
        remaining = _alive_visible(targets)
        basic_attack(remaining)
    return hit


def support():
    """Free actions every turn: heals and shields."""
    cast_ally_heal()
    cast_self_shield()
