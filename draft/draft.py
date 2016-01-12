STATE_NOT_STARTED = "NOT_STARTED"
STATE_COIN_FLIPPED = "COIN_FLIPPED"
STATE_DRAFT_COMPLETE = "COMPLETE"
STATE_BANNING = "BANNING"
STATE_PICKING = "PICKING"

USER_READABLE_STATE_MAP = {
    STATE_NOT_STARTED: "Not started",
    STATE_BANNING: "{} Ban",
    STATE_PICKING: "{} Pick",
    STATE_DRAFT_COMPLETE: "Draft complete"
}

NEXT_STATE = {
    STATE_BANNING: STATE_PICKING,
    STATE_PICKING: STATE_DRAFT_COMPLETE
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

    def _advance_state(self):
        if (not(self.state == STATE_BANNING and len(self.banned_maps) < self.draft_type.nr_bans * 2
                or self.state == STATE_PICKING and len(self.picked_maps	) < self.draft_type.nr_picks * 2)): 
            self.state = NEXT_STATE[self.state]

    def mark_map(self, map, is_pick):
        if map is None:
            self.banned_maps.append("Nothing")
        elif self.state.startswith("BAN"):
            self.banned_maps.append(map.name)
            self.map_pool.remove(map)
        else:
            map_name = map.map_mode_name(is_pick)
            self.picked_maps.append(map_name)
            for x in [x for x in self.map_pool if x.family == map.family]:
                self.map_pool.remove(x)
        self._advance_state()
        self._swap_player()

    def start_draft(self):
        self.current_player = self.start_player
        self.state = STATE_BANNING

    def user_readable_state(self):
        if self.state == STATE_BANNING:
            return USER_READABLE_STATE_MAP[self.state].format(self.ordinal((len(self.banned_maps)+1)))
        elif self.state == STATE_PICKING:
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

    ordinal = lambda self, n: "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1)*(n % 10 < 4)*n % 10 :: 4])

