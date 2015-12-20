class Room:
    def __init__(self, id, server):
        self.id = id
        self.player_list = []
        self.draft = None
        self.server = server

    def add_user_to_room(self, username):
        self.player_list.append(username)
        self.broadcast('{} has joined the room!'.format(username))

    def broadcast(self, message):
        self.server(self.id, message)
