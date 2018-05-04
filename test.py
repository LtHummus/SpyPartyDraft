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
    print draft.state
    draft.start_player = "LtHummus"
    draft.first_spy = "LtHummus"
    print draft.state
    draft.start_draft()
    print draft.state
    print draft.user_readable_state()


    draft.mark_map(get_map_by_name('gallery48', map_pool))
    draft.mark_map(get_map_by_name('highrise35', map_pool))
    print draft.user_readable_state()

    draft.mark_map(get_map_by_name('moderne58', map_pool))
    draft.mark_map(get_map_by_name('library58', map_pool))
    draft.mark_map(get_map_by_name('pub47', map_pool))
    draft.mark_map(get_map_by_name('veranda58', map_pool))
    print draft.user_readable_state()

    r = Room('sp123456', None, None, draft_types['REGULAR'])
    r.player_list = ['lthummus', 'cameraman']
    r.draft = draft

    print json.dumps(r.serialize())

    u = Uploader()
    u.upload_room(r)

