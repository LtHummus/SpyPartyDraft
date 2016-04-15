import random

KEY_LENGTH = 16


class Player:
    def __init__(self, id_, name):
        self.id = id_
        self.name = name
        self.key = ''.join(random.choice('0123456789abcdef') for _ in range(KEY_LENGTH))

    def __repr__(self):
        return '{} ({})'.format(self.name, self.key)
