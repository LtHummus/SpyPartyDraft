from draft.draft import Draft
from draft.map import Map

# TOOD: don't keep this hardcoded
TOURNEY = "scl_season_1"

class Room:
    def __init__(self, id, server, map_pool):
        self.id = id
        self.player_list = []
        self.draft = None
        self.server = server
        self.map_pool = map_pool

    def add_user_to_room(self, username):
        self.player_list.append(username)
        self.broadcast('{} has joined the room!'.format(username))

    def broadcast(self, message):
        self.server(self.id, message)

    def serializable_map_pool(self):
        return [x.as_map() for x in self.map_pool]

    def start_draft(self):
        print "starting draft"
        print self.map_pool
        self.draft = Draft(self.id, self.player_list[0], self.player_list[1], self.map_pool)
