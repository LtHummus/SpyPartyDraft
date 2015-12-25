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
from threading import Thread
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect
from room import Room
from draft.map import Map


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None

ROOM_LENGTH = 5

room_map = {}

map_pool = Map.generate_map_pool('map_pools.json', 'scl_season_1')

def generate_room_id():
    return 'sp' + ''.join(random.choice('0123456789abcdef') for i in range(ROOM_LENGTH))

def create_room(id):
    room_map[id] = Room(id, broadcast_to_room, map_pool)


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
    """Example of how to send server generated events to clients."""
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
    create_room(id)
    room_map[id].player_list.append(username)
    join_room(id)
    emit('create_success',
         {
             'room_id': id,
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
    room.touch()
    join_room(room.id)
    room.player_list.append(message['username'])
    emit('join_success',
         {
             'room_id': room.id
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

    room.draft.coin_flip_winner = winner

    emit('flip_winner', {
        'message': '{} has won the coin toss'.format(winner),
        'winner': winner
    }, room=room.id)


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


def dump_draft(room):
    data = {
        'room_id': room.id,
        'banned_maps': room.draft.serializable_bans(),
        'picked_maps': room.draft.serializibale_picks(),
        'player_one': room.draft.player_one,
        'player_two': room.draft.player_two,
        'map_pool': room.serializable_map_pool(),
        'current_player': room.draft.current_player,
        'start_player': room.draft.start_player,
        'coin_flip_winner': room.draft.coin_flip_winner,
        'coin_flip_loser': room.draft.coin_flip_loser(),
        'first_spy': room.draft.first_spy,
        'state': room.draft.state,
        'user_readable_state': room.draft.user_readable_state()
    }

    response_type = 'draft_info'
    if room.draft.draft_complete():
        # set draft over if it's over
        response_type = 'draft_over'

    room.touch()
    emit(response_type, data, room=room.id)


@socketio.on('second_option_pick', namespace='/test')
def second_option_pick(message):
    # choice was made by the coin-flip-loser
    room = room_map[message['room_id']]
    choice = message['choice']
    if choice == 'pickfirst':
        room.draft.start_player = room.draft.coin_flip_loser()
    else:
        room.draft.start_player = room.draft.coin_flip_winner
    room.draft.start_draft()
    dump_draft(room)


@socketio.on('second_option_spy', namespace='/test')
def second_option_spy(message):
    room = room_map[message['room_id']]
    choice = message['choice']
    if choice == 'spyfirst':
        room.draft.first_spy = room.draft.coin_flip_loser()
    else:
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
        ask_spy_order(room, "You opponent has opted to pick first")
    elif choice == "picksecond":
        room.draft.start_player = room.draft.coin_flip_loser()
        ask_spy_order(room, "Your opponent has opted to pick second")
    elif choice == "spyfirst":
        room.draft.first_spy = room.draft.coin_flip_winner
        ask_pick_order(room, "Your opponent has opted to spy first")
    elif choice == "spysecond":
        room.draft.first_spy = room.draft.coin_flip_loser()
        ask_pick_order(room, "Your opponent has opted to spy second")
    elif choice == "defer":
        # we're going to pretend the other player won the flip, but
        # don't let them defer
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
    if message['choice'] != 'nothing':
        chosen_map = [x for x in room.draft.map_pool if x.slug == message['choice']][0]
        print chosen_map
    room.draft.mark_map(chosen_map)
    dump_draft(room)


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected', 'count': 0})


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected', request.sid)


if __name__ == '__main__':
    socketio.run(app)