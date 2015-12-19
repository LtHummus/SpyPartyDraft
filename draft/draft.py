import random

STATE_NOT_STARTED = "NOT_STARTED"
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

    def start_draft(self):
        self.start_player = random.choice([self.player_one, self.player_two])
        self.current_player = self.start_player
        self.state = STATE_BAN_ONE

    def mark_map(self, map):
        if self.state.startswith("BAN"):
            self.banned_maps.append(map)
        else:
            self.picked_maps.append(map)


