import json


class Map:
    def __init__(self, name, slug, family):
        self.name = name
        self.slug = slug
        self.family = family

    def __repr__(self):
        return self.name

    def map_mode_name(self, is_pick):
        if self.slug.endswith('k2'):
            return self.name
        parts = self.name.split(' ')
        return parts[0] + (' PICK ' if is_pick else ' ANY ') + parts[1]

    def as_map(self):
        return {
            'name': self.name,
            'slug': self.slug,
            'family': self.family
        }

    @staticmethod
    def generate_map_pool(file_name, tourney):
        with open(file_name) as f:
            data = json.load(f)
            tourney_json = data[tourney]
            return [Map(x['name'], x['slug'], x['family']) for x in tourney_json]

if __name__ == '__main__':
    m = Map("Balcony 2/3", "balcony23", "balcony")
    print m.map_mode_name(False)
    print m.map_mode_name(True)

