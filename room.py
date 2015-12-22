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
        self.draft = None
        self.server = server
        self.map_pool = copy.copy(map_pool)
        self.last_touched = datetime.datetime.now()

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
