import random

STATE_NOT_STARTED = "NOT_STARTED"
STATE_COIN_FLIPPED = "COIN_FLIPPED"
STATE_BAN_ONE = "BAN_ONE"
STATE_BAN_TWO = "BAN_TWO"
STATE_BAN_THREE = "BAN_THREE"
STATE_BAN_FOUR = "BAN_FOUR"
STATE_PICK_ONE = "PICK_ONE"
STATE_PICK_TWO = "PICK_TWO"
STATE_PICK_THREE = "PICK_THREE"
STATE_DRAFT_COMPLETE = "COMPLETE"


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

    def mark_map(self, map):
        if self.state.startswith("BAN"):
            self.banned_maps.append(map)
        else:
            self.picked_maps.append(map)
        self._swap_player()



