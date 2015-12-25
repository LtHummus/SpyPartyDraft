import json


class Map:
    def __init__(self, name, slug, family):
        self.name = name
        self.slug = slug
        self.family = family

    def __repr__(self):
        return self.name

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
    data = Map.generate_map_pool('map_pools.json', 'scl_season_1')
    print data

