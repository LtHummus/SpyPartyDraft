import copy
import datetime

from draft.draft import Draft

# TODO: don't keep this hardcoded
TOURNEY = "scl_season_1"


class Room:
    def __init__(self, id_, server, spectator_broadcast, draft_type):
        self.id = id_
        self.player_list = []
        self.spectator_list = []
        self.draft = None
        self.server = server
        self.last_touched = datetime.datetime.now()
        self.events = []
        self.spectator_broadcast = spectator_broadcast
        self.draft_type = draft_type
        self.map_pool = copy.copy(draft_type.map_pool)

    def get_spectator_data(self):
        return {
            'events': self.events,
            'map_pool': self.serializable_map_pool(),
            'room_id': self.id
        }

    def post_event(self, event):
        self.events.append(event)
        data_map = self.get_spectator_data()

        for x in self.spectator_list:
            self.spectator_broadcast(x, data_map)

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

    def serializable_restrictions_pool(self):
        self.touch() # the divynals would be proud
        return [x.as_map() for x in self.draft.restricted_map_pool]

    def start_draft(self):
        print "starting draft"
        print self.map_pool
        self.draft = Draft(self.id, self.player_list[0], self.player_list[1], self.map_pool, self.draft_type)
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
        print self.serializable_map_pool()
        print self.draft.serializable_restrictions()
        print self.draft.serializable_bans()
        return {
            'room_id': self.id,
            'banned_maps': self.draft.serializable_bans(),
            'picked_maps': self.draft.serializable_picks(),
            'player_one': self.draft.player_one,
            'player_two': self.draft.player_two,
            'map_pool': self.serializable_map_pool(),
            'current_player': self.draft.current_player,
            'start_player': self.draft.start_player,
            'coin_flip_winner': self.draft.coin_flip_winner,
            'coin_flip_loser': self.draft.coin_flip_loser(),
            'first_spy': self.draft.first_spy,
            'state': self.draft.state,
            'user_readable_state': self.draft.user_readable_state(),
            'draft_type': self.draft_type.name,
            'restricted_map_pool': self.serializable_restrictions_pool(),
            'restricted_maps': self.draft.serializable_restrictions(),
            'double_pick': self.draft.is_double_pick()
        }
