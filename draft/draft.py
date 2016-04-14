STATE_NOT_STARTED = "NOT_STARTED"
STATE_COIN_FLIPPED = "COIN_FLIPPED"
STATE_DRAFT_COMPLETE = "COMPLETE"
STATE_BANNING = "BANNING"
STATE_PICKING = "PICKING"
STATE_FIRST_ROUND_BANNING = "FIRST_ROUND_BANNING"
STATE_FIRST_ROUND_PICKING = "FIRST_ROUND_PICKING"
STATE_SECOND_ROUND_BANNING = "SECOND_ROUND_BANNING"
STATE_SECOND_ROUND_PICKING = "SECOND_ROUND_PICKING"

USER_READABLE_STATE_MAP = {
    STATE_NOT_STARTED: "Not started",
    STATE_BANNING: "{} Ban",
    STATE_PICKING: "{} Pick",
    STATE_DRAFT_COMPLETE: "Draft complete",
    STATE_FIRST_ROUND_BANNING: "{} First Round Ban",
    STATE_FIRST_ROUND_PICKING: "{} First Round Pick",
    STATE_SECOND_ROUND_BANNING: "{} Second Round Ban",
    STATE_SECOND_ROUND_PICKING: "{} Second Round Pick"
}

NEXT_STATE = {
    STATE_BANNING: STATE_PICKING,
    STATE_PICKING: STATE_DRAFT_COMPLETE
}

MULTI_PHASE_NEXT_STATE = {
    STATE_FIRST_ROUND_BANNING: STATE_FIRST_ROUND_PICKING,
    STATE_FIRST_ROUND_PICKING: STATE_SECOND_ROUND_BANNING,
    STATE_SECOND_ROUND_BANNING: STATE_SECOND_ROUND_PICKING,
    STATE_SECOND_ROUND_PICKING: STATE_DRAFT_COMPLETE
}


class Draft:
    def __init__(self, room_id, player_one, player_two, map_pool, draft_type):
        self.room_id = room_id
        self.banned_maps = []
        self.picked_maps = []
        self.player_one = player_one
        self.player_two = player_two
        self.map_pool = map_pool
        self.current_player = None
        self.state = STATE_NOT_STARTED
        self.start_player = None
        self.coin_flip_winner = None
        self.first_spy = None
        self.draft_type = draft_type

    def flip_coin(self, winner):
        self.coin_flip_winner = winner
        self.state = STATE_COIN_FLIPPED

    def coin_flip_loser(self):
        if self.coin_flip_winner == self.player_one:
            return self.player_two
        return self.player_one

    def set_start_player(self, player_no):
        if player_no == 1:
            self.start_player = self.player_one
        else:
            self.start_player = self.player_two

    def _swap_player(self):
        if self.current_player == self.player_one:
            self.current_player = self.player_two
        else:
            self.current_player = self.player_one

    def _banning_complete(self):
        return len(self.banned_maps) < self.draft_type.nr_bans * 2

    def _picking_complete(self):
        return len(self.picked_maps) < self.draft_type.nr_picks * 2

    def _multi_phase_advance_state(self):
        print "Picks %d Bans %d" % (len(self.picked_maps), len(self.banned_maps))
        if len(self.banned_maps) == 4 and self.state == STATE_FIRST_ROUND_BANNING \
                or (len(self.picked_maps) == 2 and self.state == STATE_FIRST_ROUND_PICKING) \
                or (len(self.banned_maps) == 8 and self.state == STATE_SECOND_ROUND_BANNING) \
                or (len(self.picked_maps) >= self.draft_type.nr_picks * 2 and self.state == STATE_SECOND_ROUND_PICKING):
            self.state = MULTI_PHASE_NEXT_STATE[self.state]

    def _advance_state(self):
        if not(self.state == STATE_BANNING and self._banning_complete()
                or self.state == STATE_PICKING and self._picking_complete()):
            self.state = NEXT_STATE[self.state]

    def mark_map(self, map_):
        if map_ is None:
            self.banned_maps.append("Nothing")
        elif self.state.endswith("BANNING"):
            self.banned_maps.append(map_.name)
            self.map_pool.remove(map_)
        else:
            map_name = map_.map_mode_name()
            if self.draft_type.multi_phase and len(self.picked_maps) < 2:
                map_name = "*DOUBLED* " + map_name
            self.picked_maps.append(map_name)
            for x in [x for x in self.map_pool if x.family == map_.family]:
                self.map_pool.remove(x)
        if self.draft_type.multi_phase:
            self._multi_phase_advance_state()
        else:
            self._advance_state()
        self._swap_player()

    def start_draft(self):
        self.current_player = self.start_player
        if self.draft_type.multi_phase:
            self.state = STATE_FIRST_ROUND_BANNING
        else:
            self.state = STATE_BANNING

    def user_readable_state(self):
        if self.state.endswith("BANNING"):
            return USER_READABLE_STATE_MAP[self.state].format(self.ordinal((len(self.banned_maps)+1)))
        elif self.state.endswith("PICKING"):
            return USER_READABLE_STATE_MAP[self.state].format(self.ordinal((len(self.picked_maps)+1)))
        else:
            return USER_READABLE_STATE_MAP[self.state]

    def serializable_bans(self):
        bans = []
        curr = self.start_player
        for x in self.banned_maps:
            bans.append({
                'picker': curr,
                'map': x
            })
            if curr == self.player_one:
                curr = self.player_two
            else:
                curr = self.player_one

        return bans

    def serializable_picks(self):
        picks = []
        curr = self.start_player
        for x in self.picked_maps:
            picks.append({
                'picker': curr,
                'map': x
            })
            if curr == self.player_one:
                curr = self.player_two
            else:
                curr = self.player_one

        return picks

    def draft_complete(self):
        return self.state == STATE_DRAFT_COMPLETE

    ordinal = lambda self, n: "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10:: 4])
