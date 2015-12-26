from draft.draft import Draft
from draft.map import Map
import copy
import datetime

# TOOD: don't keep this hardcoded
TOURNEY = "scl_season_1"


class Room:
    def __init__(self, id, server, map_pool):
        self.id = id
        self.player_list = []
        self.spectator_list = []
        self.draft = None
        self.server = server
        self.map_pool = copy.copy(map_pool)
        self.last_touched = datetime.datetime.now()
        self.events = []

    def post_event(self, event):
        self.events.append(event)

    def add_user_to_room(self, username):
        self.touch()
        self.player_list.append(username)
        self.broadcast('{} has joined the room!'.format(username))

    def broadcast(self, message):
        self.touch()
        self.server(self.id, message)

    def serializable_map_pool(self):
        self.touch()
        return [x.as_map() for x in self.map_pool]

    def start_draft(self):
        print "starting draft"
        print self.map_pool
        self.draft = Draft(self.id, self.player_list[0], self.player_list[1], self.map_pool)
        self.touch()

    def touch(self):
        self.last_touched = datetime.datetime.now()

    def secs_since_last_touch(self):
        delta = datetime.datetime.now() - self.last_touched
        return delta.seconds

    def should_be_cleaned(self):
        if self.secs_since_last_touch() > (15 * 60):
            return True

        if self.draft is None:
            return False

        return self.draft.draft_complete()

    def serialize(self):
        return {
            'room_id': self.id,
            'banned_maps': self.draft.serializable_bans(),
            'picked_maps': self.draft.serializibale_picks(),
            'player_one': self.draft.player_one,
            'player_two': self.draft.player_two,
            'map_pool': self.serializable_map_pool(),
            'current_player': self.draft.current_player,
            'start_player': self.draft.start_player,
            'coin_flip_winner': self.draft.coin_flip_winner,
            'coin_flip_loser': self.draft.coin_flip_loser(),
            'first_spy': self.draft.first_spy,
            'state': self.draft.state,
            'user_readable_state': self.draft.user_readable_state()
        }

