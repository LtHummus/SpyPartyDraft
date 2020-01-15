import json

from map import Map


class DraftType:
    # TODO: refactor this to not destructure?
    def __init__(self, name, nr_bans, nr_picks, nr_restrictions, map_pool_key, multi_phase,
                 nr_first_rd_bans, nr_first_rd_picks, nr_second_rd_bans,
                 nr_second_rd_picks, nr_double_picks, double_pick_hack):
        self.name = name
        self.nr_bans = nr_bans
        self.nr_picks = nr_picks
        self.nr_restrictions = nr_restrictions
        self.is_default_draft = 0
        self.multi_phase = multi_phase
        self.nr_first_rd_bans = nr_first_rd_bans
        self.nr_first_rd_picks = nr_first_rd_picks
        self.nr_second_rd_bans = nr_second_rd_bans
        self.nr_second_rd_picks = nr_second_rd_picks
        self.nr_double_picks = nr_double_picks
        self.double_pick_hack = double_pick_hack
        self.map_pool = Map.generate_map_pool('config/map_pools.json', map_pool_key)

    @staticmethod
    def get_draft_type(file_name):
        draft_types = {}
        with open(file_name) as f:
            data = json.load(f)
            for dt in data["draft_types"]:
                draft_types[dt['id']] = DraftType(dt['name'], dt['nr_bans'], dt['nr_picks'], dt['nr_restrictions'], dt['map_pool'],
                                                  dt['multi_phase'], dt['nr_first_rd_bans'],
                                                  dt['nr_first_rd_picks'],
                                                  dt['nr_second_rd_bans'],
                                                  dt['nr_second_rd_picks'],
                                                  dt['nr_double_picks'],
                                                  dt['double_pick_hack'])
            draft_types[data["default_draft"]].is_default_draft = 1
        return draft_types
