"""Per-champion decision loop. One Bot instance lives for the whole match."""
import cambc

import combat
import config
import economy
import farming
import navigation


class ChampionState:
    def __init__(self):
        self.build_index = 0
        self.camp_layout = None


def _is_busy(me):
    return (not me.is_alive() or me.is_recalling() or me.is_submitting_gems()
            or me.is_teleporting())


def _threatened(me):
    """Any enemy champion or awake camp close enough to cancel a recall."""
    position = me.position()
    for enemy in cambc.vision.champions(cambc.Team.ENEMY):
        try:
            near = enemy.is_visible() and enemy.health() > 0 and position.chebyshev_distance(enemy.position()) <= 4
        except cambc.Error:
            near = False
        if near:
            return True
    for camp in cambc.vision.camps():
        try:
            awake = camp.is_awake()
        except cambc.Error:
            awake = False
        if awake and position.chebyshev_distance(camp.position()) <= 3:
            return True
    return False


def _recall(me):
    # The engine raises 'Champion cannot act' if a channel is already running
    # or the champion was stunned this turn; that must not end the turn.
    try:
        me.recall()
    except cambc.Error:
        pass


class Bot:
    def __init__(self):
        self.state = ChampionState()

    def _farmable(self, camps):
        me = cambc.me()
        allow_monolith = farming._team_ready_for_monolith(me)
        farmable = []
        for camp in camps:
            try:
                if allow_monolith or not camp.is_monolith():
                    farmable.append(camp)
            except cambc.Error:
                continue
        return farmable

    def play_turn(self):
        me = cambc.me()

        # Dead champions still get a turn: use it to shop.
        if not me.is_alive():
            economy.buy_items(self.state)
            return
        if _is_busy(me):
            return

        if navigation.at_spawn():
            economy.buy_items(self.state)

        combat.support()

        # Low health away from spawn: step out of danger, then recall
        # (damage interrupts a recall, so do not start one under fire).
        if not navigation.at_spawn() and me.health() < me.max_health() * config.RECALL_HEALTH:
            if _threatened(me):
                navigation.move_home()
            else:
                _recall(me)
            return

        # Enemy champions in range take priority: kills steal their gems.
        enemies = combat.enemies_in_attack_range()
        if enemies:
            combat.fight(enemies)
            return

        if economy.should_bank(me):
            economy.bank_gems()
            return

        # Nothing to bank and a full purse: recall to buy power.
        if (me.gold_count() >= config.SHOP_TRIP_GOLD and not navigation.at_spawn()
                and not _threatened(me)):
            _recall(me)
            return

        camps = self._farmable(combat.camps_in_attack_range())
        if camps:
            combat.fight(camps)
            # Melee champions may still walk after attacking; ranged may not.
            return

        moved = farming.advance_to_camps(self.state)
        if moved:
            camps = self._farmable(combat.camps_in_attack_range())
            if camps:
                combat.fight(camps)
