import json

from map import Map


class Draft_type:
    def __init__(self, name, nr_bans, nr_picks, map_pool_key):
        self.name = name
        self.nr_bans = nr_bans
        self.nr_picks = nr_picks
        self.is_default_draft = 0
        self.map_pool = Map.generate_map_pool('config/map_pools.json', map_pool_key)

    @staticmethod
    def get_draft_type(file_name):
        draft_types = {}
        with open(file_name) as f:
            data = json.load(f)
            for dt in data["draft_types"]:
                draft_types[dt['id']] = Draft_type(dt['name'], dt['nr_bans'], dt['nr_picks'], dt['map_pool'])
            draft_types[data["default_draft"]].is_default_draft = 1
        return draft_types



