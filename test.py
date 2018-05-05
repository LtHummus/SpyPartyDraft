from draft.upload_draft_to_manager import Uploader
from room import Room
from draft.draft import Draft
import json

def get_map_by_name(name, pool):
    return [x for x in pool if x.slug == name][0]

if __name__ == '__main__':
    from draft.map import Map
    from draft.drafttype import DraftType

    # (self, room_id, player_one, player_two, map_pool, draft_type):
    map_pool = Map.generate_map_pool('config/map_pools.json', "scl_season_4")
    draft_types = DraftType.get_draft_type('config/draft_types.json')
    print draft_types

    draft = Draft("foo", "lthummus", "cameraman", map_pool, draft_types['REGULAR'])

    print draft.flip_coin("LtHummus")
    draft.start_player = "LtHummus"
    draft.first_spy = "LtHummus"
    print draft.state
    draft.start_draft()
    print draft.state
    print draft.user_readable_state()

    draft.mark_map(get_map_by_name('library58', map_pool))
    draft.mark_map(get_map_by_name('highrise35', map_pool))
    print draft.user_readable_state()

    draft.mark_map(get_map_by_name('moderne58', map_pool))
    draft.mark_map(get_map_by_name('veranda58', map_pool))
    draft.mark_map(get_map_by_name('pub47', map_pool))
    draft.mark_map(get_map_by_name('terrace35', map_pool))
    print draft.user_readable_state()

    r = Room('sp123456', None, None, draft_types['REGULAR'])
    r.player_list = ['lthummus', 'cameraman']
    r.draft = draft

    print json.dumps(r.serialize())

    u = Uploader()
    u.upload_room(r)

    # Hummus after you verify that this is a valid payload for Season 4, we should assert that the json dumps equals == 
    # {"first_spy": "LtHummus", "player_one": "lthummus", "draft_type": "Regular Season Match", "coin_flip_winner": "LtHummus", "start_player": "LtHummus", 
    # "picked_maps": [{"picker": "LtHummus", "map": "Moderne Any 5/8"}, {"picker": "lthummus", "map": "Veranda Any 5/8"}, {"picker": "cameraman", "map": "Pub Any 4/7"}, {"picker": "lthummus", "map": "Terrace Any 3/5"}], 
    # "current_player": "cameraman", "user_readable_state": "Draft complete", "coin_flip_loser": "lthummus", "player_two": "cameraman", "state": "COMPLETE", 
    # "room_id": "sp123456", "banned_maps": [{"picker": "LtHummus", "map": "Library Any 5/8"}, {"picker": "lthummus", "map": "High-Rise Any 3/5"}], 
    # "map_pool": [{"name": "Balcony Any 2/3", "family": "balcony", "slug": "balcony23"}, {"name": "Ballroom Any 4/8", "family": "ballroom", "slug": "ballroom48"}, {"name": "Courtyard Any 4/7", "family": "courtyard", "slug": "courtyard47"}, 
    # {"name": "Gallery Any 4/8", "family": "gallery", "slug": "gallery48"}, {"name": "High-Rise Any 3/5", "family": "highrise", "slug": "highrise35"}, {"name": "Library Any 5/8", "family": "library", "slug": "library58"}, 
    # {"name": "Moderne Any 5/8", "family": "moderne", "slug": "moderne58"}, {"name": "Pub Any 4/7", "family": "pub", "slug": "pub47"}, {"name": "Terrace Any 3/5", "family": "terrace", "slug": "terrace35"}, {"name": "Veranda Any 5/8", "family": "veranda", "slug": "veranda58"}]}
