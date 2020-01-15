
STATE_NOT_STARTED = "NOT_STARTED"
STATE_COIN_FLIPPED = "COIN_FLIPPED"
STATE_DRAFT_COMPLETE = "COMPLETE"
STATE_BANNING = "BANNING"
STATE_PICKING = "PICKING"
STATE_RESTRICTING = "RESTRICTING"
STATE_FIRST_ROUND_BANNING = "FIRST_ROUND_BANNING"
STATE_FIRST_ROUND_PICKING = "FIRST_ROUND_PICKING"
STATE_SECOND_ROUND_BANNING = "SECOND_ROUND_BANNING"
STATE_SECOND_ROUND_PICKING = "SECOND_ROUND_PICKING"

USER_READABLE_STATE_MAP = {
    STATE_NOT_STARTED: "Not started",
    STATE_BANNING: "{} Ban",
    STATE_PICKING: "{} Pick",
    STATE_RESTRICTING: "{} Restriction",
    STATE_DRAFT_COMPLETE: "Draft complete",
    STATE_FIRST_ROUND_BANNING: "{} First Round Ban",
    STATE_FIRST_ROUND_PICKING: "{} First Round Pick",
    STATE_SECOND_ROUND_BANNING: "{} Second Round Ban",
    STATE_SECOND_ROUND_PICKING: "{} Second Round Pick"
}

NEXT_STATE = {
    STATE_BANNING: STATE_RESTRICTING,
    STATE_RESTRICTING: STATE_PICKING,
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
        self.restricted_map_pool = []
        self.restricted_maps = []
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
        return winner

    def coin_flip_loser(self):
        if self.coin_flip_winner == self.player_one:
            return self.player_two
        return self.player_one

    def set_start_player(self, player_no):
        if player_no == 1:
            self.start_player = self.player_one
        else:
            self.start_player = self.player_two

    def is_banning(self):
        return self.state.endswith("BANNING")

    def is_picking(self):
        return self.state.endswith("PICKING")

    def is_restricting(self):
        return self.state.endswith("RESTRICTING")

    def _swap_player(self):
        if self.current_player == self.player_one:
            self.current_player = self.player_two
        else:
            self.current_player = self.player_one

    def _restricting_complete(self):
        return len(self.restricted_map_pool) < self.draft_type.nr_restrictions * 2

    def _banning_complete(self):
        return len(self.banned_maps) < self.draft_type.nr_bans * 2

    def _picking_complete(self):
        return len(self.picked_maps) < self.draft_type.nr_picks * 2

    def _multi_phase_advance_state(self):
        # print "Picks %d Bans %d" % (len(self.picked_maps), len(self.banned_maps))
        if len(self.banned_maps) == self.draft_type.nr_first_rd_bans * 2 and self.state == STATE_FIRST_ROUND_BANNING \
                or (len(self.picked_maps) == self.draft_type.nr_first_rd_picks * 2 and self.state == STATE_FIRST_ROUND_PICKING) \
                or (len(self.banned_maps) == (self.draft_type.nr_first_rd_bans + self.draft_type.nr_second_rd_bans) * 2 and self.state == STATE_SECOND_ROUND_BANNING) \
                or (len(self.picked_maps) >= (self.draft_type.nr_first_rd_picks + self.draft_type.nr_second_rd_picks) * 2 and self.state == STATE_SECOND_ROUND_PICKING):
            self.state = MULTI_PHASE_NEXT_STATE[self.state]

    def _advance_state(self):
        # check to see if we're done with our current state by looking at the number of maps in each
        # of the result lists, if we are done, then advance state
        if not (self.state == STATE_BANNING and self._banning_complete() or
                self.state == STATE_RESTRICTING and self._restricting_complete() or
                self.state == STATE_PICKING and self._picking_complete()):
            self.state = NEXT_STATE[self.state]

    def mark_map(self, map_):
        if map_ is None:
            if self.is_banning():
                self.banned_maps.append("Nothing")
            elif self.is_restricting():
                self.restricted_map_pool.append("Nothing")
            else:
                assert False
        elif self.is_banning():
            self.banned_maps.append(map_.name)
            self.map_pool.remove(map_)
        elif self.is_restricting():
            self.restricted_map_pool.append(map_)
            self.restricted_maps.append(map_.name)
            self.map_pool.remove(map_)
        else:
            map_name = map_.map_mode_name()
            if self.is_double_pick():
                map_name = "*DOUBLED* " + map_name

            self.map_pool.remove(map_)
            if not self.is_double_pick() or not self.draft_type.double_pick_hack:
                for x in [x for x in self.map_pool if x.family == map_.family]:
                    self.map_pool.remove(x)

            self.picked_maps.append(map_name)
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

    def is_double_pick(self):
        return len(self.picked_maps) < self.draft_type.nr_double_picks * 2

    def user_readable_state(self):
        true_num_picked = len(self.picked_maps) + 1
        true_num_banned = len(self.banned_maps) + 1
        true_num_restricted = len(self.restricted_map_pool) + 1
        if "SECOND" in self.state:
            true_num_banned -= self.draft_type.nr_first_rd_bans * 2
            true_num_picked -= self.draft_type.nr_first_rd_picks * 2
        if self.is_banning():
            return USER_READABLE_STATE_MAP[self.state].format(self.ordinal(true_num_banned))
        elif self.is_picking():
            plain_state = USER_READABLE_STATE_MAP[self.state].format(self.ordinal(true_num_picked))
            if self.is_double_pick():
                return plain_state + " (Picking Doubles)"
            return plain_state
        elif self.is_restricting():
            return USER_READABLE_STATE_MAP[self.state].format(self.ordinal(true_num_restricted))
        else:
            return USER_READABLE_STATE_MAP[self.state]

    def serializable_bans(self):
        return self._build_serializable_list(self.banned_maps)

    def serializable_picks(self):
        return self._build_serializable_list(self.picked_maps)

    def serializable_restrictions(self):
        return self._build_serializable_list(self.restricted_maps)

    def _build_serializable_list(self, map_list):
        res = []
        curr = self.start_player
        for x in map_list:
            res.append({
                'picker': curr,
                'map': x
            })
            if curr == self.player_one:
                curr = self.player_two
            else:
                curr = self.player_one

        return res

    def draft_complete(self):
        return self.state == STATE_DRAFT_COMPLETE

    @staticmethod
    def ordinal(n):
        return "%d%s" % (n, "tsnrhtdd"[(n / 10 % 10 != 1) * (n % 10 < 4) * n % 10:: 4])
