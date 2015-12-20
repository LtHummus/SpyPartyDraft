import random

KEY_LENGTH = 16


class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.key = ''.join(random.choice('0123456789abcdef') for i in range(KEY_LENGTH))

    def __repr__(self):
        return '{} ({})'.format(self.name, self.key)