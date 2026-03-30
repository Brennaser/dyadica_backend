from flask import Flask, jsonify, request, redirect, render_template
from flask_socketio import SocketIO

from extensions import db

import json

from Event import Event
from Profile import Profile

# TODO update
"""
Main executable for Dyadica.

author: Brenn Sermania
version: 11/20/2025
"""

# ---------- Setup ----------
app = Flask(__name__)

# https://www.geeksforgeeks.org/python/connect-flask-to-a-database-with-flask-sqlalchemy/
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.config['SECRET_KEY'] = 'vnajdsf;adjaodlkd;jkavds'

socket = SocketIO(app)

active_users = {}

# Variables for tracking data during the study
dyadica_data = {}
round = 0


def find_active_user(sid):

    for uid in active_users.keys():
        if active_users[uid] == sid:
            return uid
        
    return -1


@socket.on('update_profile')
def update_profile(profile_info):

    user_id = profile_info['user_id']
    print(user_id)
    name = profile_info['name']
    fields = profile_info['fields']

    profile = db.session.get(Profile, user_id)

    if profile:
        profile.update_name(name)
        profile.update_fields(fields)
        db.session.commit()
    else:
        # TODO: error handling
        pass

    return redirect('/')


@socket.on('rsvp')
def rsvp(data):

    # request_info = request.get_json()
    user_id = data['user_id']
    event_id = data['event_id']

    profile = db.session.get(Profile, user_id)
    event = db.session.get(Event, event_id)

    if (profile and event) and profile not in event.attendees:
        event.attendees.append(profile)
        profile.dancing = True
        db.session.commit()
        # profile.events.append(event)
        print(f"RSVPed User {user_id} {profile.name} for Event {event_id} {event.name}")
        print(f"{len(event.attendees)} attendees RVSPed for {event.name}")
    else:
        # TODO: error handling
        pass
    
    return redirect('/')


# @app.route('/check_in', methods=['POST'])
# def check_in():
    
#     request_info = request.get_json()
#     user_id = request_info['user_id']
#     event_id = request_info['event_id']

#     profile = db.session.get(Profile, user_id)
#     event = db.session.get(Event, event_id)

#     if profile and event:
#         # FIX: check in needs to be reworked
#         event.check_in_attendee(user_id)
#         db.session.commit()
#     else:
#         # TODO: error handling
#         pass

#     return redirect('/')


@socket.on("toggle_user_break")
def toggle_user_break():

    global dyadica_data
    global round
    
    user_id = find_active_user(request.sid)

    if user_id == -1:
        return redirect('/')

    profile = db.session.get(Profile, user_id)

    if profile:
        profile.toggle_break()
        db.session.commit()
        socket.emit("toggle_user_break",
                    {"dancing": profile.dancing},
                    to=request.sid)
        
        if user_id not in dyadica_data['opt_outs']:
            dyadica_data['opt_outs'][user_id] = []

        dyadica_data['opt_outs'][user_id].append((round, profile.dancing))
        print(dyadica_data)
    else:
        # TODO: error handling
        pass

    return redirect('/')

# TODO?: rework with sockets
# FIX?: rework with the split app model
# @app.route('/block_user', methods=['POST'])
# def block_user():
#     request_info = request.get_json()
#     user_a_id = request_info['user_a_id']
#     user_b_id = request_info['user_b_id']

#     user_a = db.session.get(Profile, user_a_id)
#     user_b = db.session.get(Profile, user_b_id)

#     # FIX: the blocked list is broken in the database
#     user_a.block_user(user_b)
#     db.session.commit()


@app.route('/new_event', methods=['POST'])
def make_event():
    event_info = request.get_json()
    name = event_info['name']
    date = event_info['date']
    location = event_info['location']
    owner = event_info['owner']

    if name != '' and date != '' and location != '' and owner is not None:
        event = Event(name=name, date=date, location=location, owner=owner)
        db.session.add(event)
        db.session.commit()
        pass
    else:
        # TODO: error handling
        pass

    return redirect('/')


@app.route('/active_users')
def list_active_users():

    users = db.session.query(Profile).filter(Profile.id.in_(active_users.keys())).all()
    return [user.__repr__() for user in users]


@app.route('/test')
def test():
    t = db.session.query(Event).all()
    print(t.__repr__())
    return [temp.__repr__() for temp in t]


@socket.on('get_events')
def get_events():
    events = db.session.query(Event).all()

    serialize = lambda event: {"event_id": event.id,
                               "event_owner": event.owner,
                               "event_name": event.name,
                               "event_location": event.location,
                               "event_date": event.date,
                               }

    # [print(serialize(event)) for event in events]

    socket.emit('get_events',
                {"events": [serialize(event) for event in events]},
                to=request.sid)


@app.route('/update_event', methods=['POST'])
def update_event():
    event_info = request.get_json()
    event_id = event_info['event_id']
    name = event_info['name']
    date = event_info['date']
    location = event_info['location']

    if event_id is not None:
        event = db.session.get(Event, event_id)
        event.name = name
        event.date = date
        event.location = location
        db.session.commit()
        pass
    else:
        # TODO: error handling
        pass

    return redirect('/')


# @app.route('/start_event', methods=['POST'])
# def start_event():

#     event_info = request.get_json()
#     event_id = event_info['event_id']

#     event = db.session.get(Event, event_id)

#     if event:
#         event.start_event()
#         db.session.commit()
#     else:
#         # TODO: error handling
#         pass

#     return redirect('/')


# @app.route('/end_event', methods=[])
# def end_event(event_id: int):

#     event_info = request.get_json()
#     event_id = event_info['event_id']

#     event = db.session.get(Event, event_id)

#     if event:
#         event.end_event()
#         db.session.commit()
#     else:
#         # TODO: error handling
#         pass

#     return redirect('/')


@app.route('/make_pairs', methods=['POST'])
def make_pairs():

    global dyadica_data
    global round

    request_info = request.get_json()
    event_id = request_info['event_id']

    event = db.session.get(Event, event_id)

    if len(event.pair_scores) == 0:
        event.start_event()
        # _, pair_scores = event.scores_to_df()
        dyadica_data['max_pair_scores'] = event.max_pair_scores

    [print(attendee) for attendee in event.attendees]

    round += 1
    pairs = event.make_pairs()
    event.adjust_scores(pairs)
    db.session.commit()

    format_profile = lambda p: {"user_id": p.id,
                                "name": p.name,
                                "fields": p.fields,
                                "dancing": p.dancing}
    
    dyadica_data['pairs_made'][round] = []
    print(dyadica_data)
    for a, b in pairs:

        dyadica_data['pairs_made'][round].append((int(a), int(b)))

        a_sid = active_users[int(a)]
        b_sid = active_users[int(b)]

        profile_a = db.session.get(Profile, int(a))
        profile_b = db.session.get(Profile, int(b))

        socket.emit('send_pair',
                {"pair": format_profile(profile_b)},
                    to=a_sid
                    )
        
        socket.emit('send_pair',
                    {'pair': format_profile(profile_a)},
                    to=b_sid
                    )

    return redirect('/')


@socket.on("decline")
def decline(data):

    global dyadica_data

    pair_id = data['pair_id']
    pair_sid = active_users[pair_id]

    socket.emit("decline",
                to=pair_sid)
    
    user_id = find_active_user(request.sid)

    if round not in dyadica_data['pairs_declined']:
        dyadica_data['pairs_declined'][round] = []

    dyadica_data['pairs_declined'][round].append((user_id, pair_id))

    print("Pairing Declined")


@socket.on('user_id')
def user_id(data):

    profile = db.session.get(Profile, data['user_id'])

    if profile:
        active_users[profile.id] = request.sid
        socket.emit('profile_data',
                    {'user_id': profile.id,
                    'name': profile.name,
                    'fields': profile.fields},
                    to=request.sid)
        print(f'Logged in User {profile.id}')
    else:
        default_fields = {"lead/follow": {'Lead': False, 'Follow': False},
                          "style": {'Lindy Hop': False, "Westie": False, "Balboa": False},
                          "position": {"Open": False, "Closed": False, "Close Embrace": False}}

        profile = Profile('', default_fields)
        db.session.add(profile)
        db.session.commit()

        socket.emit('profile_data',
                    {'user_id': profile.id,
                    'name': profile.name,
                    'fields': profile.fields},
                    to=request.sid)

        active_users[profile.id] = request.sid
        print(profile)
        print(f'Made new Profile: {profile.id}')


@socket.on('connect')
def connect():
    print(f"Connected on Socket: {request.sid}")


@socket.on('disconnect')
def disconnect(_):
    user_id = find_active_user(request.sid)
    active_users.pop(user_id)
    print(f'Disconnected {request.sid}')

    # Ignore "AssertionError: write() before start_response"
    # Harmless race condition caused by the dev server's limitations when 
    # dealing with WebSockets


def make_json_data():

    # make sure all data is being saved
    with open('dyadica_data.json', 'w+') as f:
        json.dump(dyadica_data, f, indent=4)
        print('dyadica_data saved')

    return dyadica_data


# TODO: link sources
if __name__ == "__main__":

    round = 0

    dyadica_data['max_pair_scores'] = []
    dyadica_data['pairs_made'] = {}
    dyadica_data['pairs_declined'] = {}
    dyadica_data['opt_outs'] = {}

    with app.app_context():
        db.create_all()

    socket.run(app, debug=False, host="0.0.0.0", allow_unsafe_werkzeug=True)

    # Save all changes made
    with app.app_context():

        print('here')
        db.session.commit()

        print(dyadica_data)

        make_json_data()
