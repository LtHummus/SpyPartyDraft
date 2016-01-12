#!/usr/bin/env python

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on available packages.
async_mode = None

if async_mode is None:
    try:
        import eventlet
        async_mode = 'eventlet'
    except ImportError:
        pass

    if async_mode is None:
        try:
            from gevent import monkey
            async_mode = 'gevent'
        except ImportError:
            pass

    if async_mode is None:
        async_mode = 'threading'

    print('async_mode is ' + async_mode)

# monkey patching is necessary because this application uses a background
# thread
if async_mode == 'eventlet':
    import eventlet
    eventlet.monkey_patch()
elif async_mode == 'gevent':
    from gevent import monkey
    monkey.patch_all()

import time
import random
import datetime
import uuid
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from room import Room
from draft.draft_type import Draft_type

import boto3

#dynamodb = boto3.resource('dynamodb')
#table = dynamodb.Table('spypartydraft_test')
table = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
dynamo_db_table_name = "spypartydraft_test"


ROOM_LENGTH = 5

room_map = {}
draft_types = Draft_type.get_draft_type('config/draft_types.json')


def generate_room_id():
    return 'sp' + ''.join(random.choice('0123456789abcdef') for i in range(ROOM_LENGTH))


def create_room(id, draft_type_id):
    room_map[id] = Room(id, broadcast_to_room, broadcast_to_spectator, draft_types[draft_type_id])


def broadcast_to_spectator(spectator_id, data):
    emit('spectator_update', data, room=spectator_id)


def tell_clients_draft_has_started(room):
    print 'dumping draft info'
    emit('draft_start',
         {
             'map_pool': room.serializable_map_pool(),
             'player_one': room.draft.player_one,
             'player_two': room.draft.player_two,
             'state': room.draft.state,
             'room_id': room.id
         }, room=room.id)


def background_thread():
    print 'cleanup thread started'
    while True:
        time.sleep(300)
        cleanable = [k for k, v in room_map.iteritems() if room_map[k].should_be_cleaned()]
        for x in cleanable:
            del room_map[x]
            print "cleaned room {}".format(x)
            # we probably want to close the room here...?
        print "should really clean things up here"


@app.route('/')
def index():
    global thread
    if thread is None:
        thread = Thread(target=background_thread)
        thread.daemon = True
        thread.start()
    return render_template('index.html')


@socketio.on('my event', namespace='/test')
def test_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']})


@socketio.on('my broadcast event', namespace='/test')
def test_broadcast_message(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': message['data'], 'count': session['receive_count']},
         broadcast=True)


@socketio.on('create', namespace='/test')
def create(message):
    print "got create message"
    print "username: " + message['data']
    username = message['data']
    id = generate_room_id()
    create_room(id,message['draft_type_id'])
    room_map[id].player_list.append(username)
    room_map[id].post_event("{} has joined the room!".format(username))
    join_room(id)
    emit('create_success',
         {
             'room_id': id,
             'draft_type' : room_map[id].draft_type.name
         })
    broadcast_to_room(id, "{} has joined the room!".format(username))
    broadcast_to_room(id, "Players currently in room: {}".format(' and '.join(room_map[id].player_list)))


def broadcast_to_room(room_id, msg):
    print 'broadcasting: ' + msg
    emit('room_broadcast',
         {'msg': msg,
          'room': room_id
         },
         room=room_id)


@socketio.on('join_draft', namespace='/test')
def join_draft(message):
    room_to_join = message['room_id']
    if room_to_join not in room_map:
        emit('join_error',
             {
                 'message': 'Room {} does not exist'.format(room_to_join)
             })
        return
    room = room_map[room_to_join]
    if len(room.player_list) >= 2:
        emit('join_error',
             {
                 'message': 'Room {} already has two players in it'.format(room.id)
             })
        return

    room.touch()
    join_room(room.id)
    room.player_list.append(message['username'])
    room.post_event("{} has joined the room!".format(message['username']))
    emit('join_success',
         {
             'room_id': room.id,
             'draft_type': room.draft_type.name
         })
    broadcast_to_room(room.id, "{} has joined the room!".format(message['username']))
    broadcast_to_room(room.id, "Players currently in room: {}".format(' and '.join(room.player_list)))
    if len(room.player_list) == 2:
        room.start_draft()
        print "back from draft started"
        tell_clients_draft_has_started(room)


@socketio.on('join', namespace='/test')
def join(message):
    join_room(message['room'])
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('leave', namespace='/test')
def leave(message):
    leave_room(message['room'])
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response',
         {'data': 'In rooms: ' + ', '.join(rooms()),
          'count': session['receive_count']})


@socketio.on('close room', namespace='/test')
def close(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    emit('my response', {'data': 'Room ' + message['room'] + ' is closing.',
                         'count': session['receive_count']},
         room=message['room'])
    close_room(message['room'])


@socketio.on('coin_flip', namespace='/test')
def coin_flip(message):
    print 'got coinflip {}'.format(message['choice'])
    print message
    room = room_map[message['room_id']]
    room.touch()
    user_flip = message['choice']
    our_flip = random.choice(['heads', 'tails'])
    if user_flip == our_flip:
        winner = room.draft.player_two
    else:
        winner = room.draft.player_one

    room.post_event("{} has won the coin flip".format(winner))
    room.draft.coin_flip_winner = winner

    emit('flip_winner', {
        'message': '{} has won the coin toss'.format(winner),
        'winner': winner
    }, room=room.id)


@socketio.on('get_draft_types', namespace='/test')
def get_draft_types():
    dts = []
    for dt_id, dt in draft_types.items():
        dts.append({'id': dt_id,'name': dt.name,'selected': dt.is_default_draft})

    emit('draft_types_update', dts)


def ask_spy_order(room, msg):
    data = {
        'username': room.draft.coin_flip_loser(),
        'message': msg
    }
    emit('select_spy_order', data, room=room.id)


def ask_pick_order(room, msg):
    data = {
        'username': room.draft.coin_flip_loser(),
        'message': msg
    }
    emit('select_pick_order', data, room=room.id)


def persist_draft(room):
    data = {
        'picks': room.draft.picked_maps,
        'bans': room.draft.banned_maps,
        'player1': room.draft.player_one,
        'player2': room.draft.player_two,
        'time': int(time.mktime(datetime.datetime.now().timetuple())),
        'first_pick': room.draft.start_player,
        'first_spy': room.draft.first_spy,
        'uuid': str(uuid.uuid4()),
        'room_id': room.id
    }

    if table is not None:
        table.put_item(Item=data)
        print "persisted item for room: {}".format(room.id)


def dump_draft(room):
    response_type = 'draft_info'
    if room.draft.draft_complete():
        # set draft over if it's over
        response_type = 'draft_over'
        persist_draft(room)

    room.touch()
    emit(response_type, room.serialize(), room=room.id)


@socketio.on('second_option_pick', namespace='/test')
def second_option_pick(message):
    # choice was made by the coin-flip-loser
    room = room_map[message['room_id']]
    choice = message['choice']
    if choice == 'pickfirst':
        room.post_event("{} has opted to pick first".format(room.draft.coin_flip_loser()))
        room.draft.start_player = room.draft.coin_flip_loser()
    else:
        room.post_event("{} has opted to pick second".format(room.draft.coin_flip_loser()))
        room.draft.start_player = room.draft.coin_flip_winner
    room.draft.start_draft()
    dump_draft(room)


@socketio.on('second_option_spy', namespace='/test')
def second_option_spy(message):
    room = room_map[message['room_id']]
    choice = message['choice']
    if choice == 'spyfirst':
        room.post_event("{} has opted to spy first".format(room.draft.coin_flip_loser()))
        room.draft.first_spy = room.draft.coin_flip_loser()
    else:
        room.post_event("{} has opted to spy second".format(room.draft.coin_flip_loser()))
        room.draft.first_spy = room.draft.coin_flip_winner
    room.draft.start_draft()
    dump_draft(room)


@socketio.on('first_option_form', namespace='/test')
def first_option_form(message):
    choice = message['choice']
    room = room_map[message['room_id']]
    room.touch()
    print "got choice {}".format(choice)
    if choice == "pickfirst":
        room.draft.start_player = room.draft.coin_flip_winner
        room.post_event("{} has opted to pick first".format(room.draft.coin_flip_winner))
        ask_spy_order(room, "You opponent has opted to pick first")
    elif choice == "picksecond":
        room.draft.start_player = room.draft.coin_flip_loser()
        room.post_event("{} has opted to pick second".format(room.draft.coin_flip_winner))
        ask_spy_order(room, "Your opponent has opted to pick second")
    elif choice == "spyfirst":
        room.draft.first_spy = room.draft.coin_flip_winner
        room.post_event("{} has opted to spy first".format(room.draft.coin_flip_winner))
        ask_pick_order(room, "Your opponent has opted to spy first")
    elif choice == "spysecond":
        room.draft.first_spy = room.draft.coin_flip_loser()
        room.post_event("{} has opted to spy second".format(room.draft.coin_flip_winner))
        ask_pick_order(room, "Your opponent has opted to spy second")
    elif choice == "defer":
        # we're going to pretend the other player won the flip, but
        # don't let them defer
        room.post_event("{} has opted to defer".format(room.draft.coin_flip_winner))
        room.draft.coin_flip_winner = room.draft.coin_flip_loser()
        emit('winner_deferred', {
            'room_id': room.id,
            'picker': room.draft.coin_flip_winner
        }, room=room.id)


@socketio.on('disconnect_request', namespace='/test')
def disconnect_request(message):
    print 'disconnecting'
    disconnect()


@socketio.on('draft_map', namespace='/test')
def draft_map(message):
    room = room_map[message['room_id']]
    chosen_map = None
    chosen_map_name = "nothing"

    if message['choice'] != 'nothing':
        chosen_map = [x for x in room.draft.map_pool if x.slug == message['choice']][0]
        chosen_map_name = chosen_map.name
        if room.draft.state.startswith('PICK') and not chosen_map.slug.endswith('k2'):
            chosen_map_name = chosen_map.map_mode_name(message['is_pick'])

    if room.draft.state.startswith('BAN'):
        room.post_event("{} has banned {}".format(room.draft.current_player, chosen_map_name))
    else:
        room.post_event("{} has picked {}".format(room.draft.current_player, chosen_map_name))
    room.draft.mark_map(chosen_map, message['is_pick'])
    dump_draft(room)


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


@socketio.on('spectate_draft', namespace='/test')
def spectate_draft(message):
    room_to_join = message['room_id']
    if room_to_join not in room_map:
        print "'{}' doesn't exist as a room".format(room_to_join)
        emit('spectate_error',
             {
                 'message': 'Room {} does not exist'.format(room_to_join)
             })
        return
    room = room_map[room_to_join]
    room.spectator_list.append(request.sid)
    emit('spectate_join_success', {
        'room_id': room_to_join,
        'sid': request.sid
    })
    broadcast_to_spectator(request.sid, room.get_spectator_data())

@socketio.on('chat_message', namespace='/test')
def chat_message(message):
    room = room_map[message['room_id']]
    print 'got chat message ' + message['chat_text']
    data = {
        'room_id': room.id,
        'talker': message['username'],
        'text': message['chat_text']
    }
    emit('chat_event', data, room=room.id)


if __name__ == '__main__':
    socketio.run(app)
