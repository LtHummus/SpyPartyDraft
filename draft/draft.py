from map import Map

STATE_NOT_STARTED = "NOT_STARTED"
STATE_COIN_FLIPPED = "COIN_FLIPPED"
STATE_BAN_ONE = "BAN_ONE"
STATE_BAN_TWO = "BAN_TWO"
STATE_BAN_THREE = "BAN_THREE"
STATE_BAN_FOUR = "BAN_FOUR"
STATE_PICK_ONE = "PICK_ONE"
STATE_PICK_TWO = "PICK_TWO"
STATE_PICK_THREE = "PICK_THREE"
STATE_PICK_FOUR = "PICK_FOUR"
STATE_DRAFT_COMPLETE = "COMPLETE"

USER_READABLE_STATE_MAP = {
    STATE_NOT_STARTED: "Not started",
    STATE_BAN_ONE: "First Ban",
    STATE_BAN_TWO: "Second Ban",
    STATE_BAN_THREE: "Third Ban",
    STATE_BAN_FOUR: "Fourth Ban",
    STATE_PICK_ONE: "First Pick",
    STATE_PICK_TWO: "Second Pick",
    STATE_PICK_THREE: "Third Pick",
    STATE_PICK_FOUR: "Fourth Pick",
    STATE_DRAFT_COMPLETE: "Draft complete"
}

NEXT_STATE = {
    STATE_BAN_ONE: STATE_BAN_TWO,
    STATE_BAN_TWO: STATE_BAN_THREE,
    STATE_BAN_THREE: STATE_BAN_FOUR,
    STATE_BAN_FOUR: STATE_PICK_ONE,
    STATE_PICK_ONE: STATE_PICK_TWO,
    STATE_PICK_TWO: STATE_PICK_THREE,
    STATE_PICK_THREE: STATE_PICK_FOUR,
    STATE_PICK_FOUR: STATE_DRAFT_COMPLETE
}


class Draft:
    def __init__(self, room_id, player_one, player_two, map_pool):
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
        self.state = NEXT_STATE[self.state]

    def mark_map(self, map):
        if map is None:
            self.banned_maps.append(Map("Nothing", "", ""))
        elif self.state.startswith("BAN"):
            self.banned_maps.append(map)
            self.map_pool.remove(map)
        else:
            self.picked_maps.append(map)
            for x in [x for x in self.map_pool if x.family == map.family]:
                self.map_pool.remove(x)
        self._advance_state()
        self._swap_player()

    def start_draft(self):
        self.current_player = self.start_player
        self.state = STATE_BAN_ONE

    def user_readable_state(self):
        return USER_READABLE_STATE_MAP[self.state]

    def serializable_bans(self):
        list = []
        curr = self.start_player
        for x in self.banned_maps:
            list.append({
                'picker': curr,
                'map': x.name
            })
            if curr == self.player_one:
                curr = self.player_two
            else:
                curr = self.player_one

        return list

    def serializibale_picks(self):
        list = []
        curr = self.start_player
        for x in self.picked_maps:
            list.append({
                'picker': curr,
                'map': x.name
            })
            if curr == self.player_one:
                curr = self.player_two
            else:
                curr = self.player_one

        return list

    def draft_complete(self):
        return self.state == STATE_DRAFT_COMPLETE

