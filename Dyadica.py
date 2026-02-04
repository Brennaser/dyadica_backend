from flask import Flask, jsonify, request, redirect, render_template
from flask_socketio import SocketIO

from extensions import db

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


# TODO: actually do this on client end
@app.route('/rsvp', methods=['POST'])
def rsvp():

    request_info = request.get_json()
    user_id = request_info['user_id']
    event_id = request_info['event_id']

    profile = db.session.get(Profile, user_id)
    event = db.session.get(Event, event_id)

    if profile and event:
        event.attendees.append(profile)
        db.session.commit()
        # profile.events.append(event)
        # Q: is there more to it?
    else:
        # TODO: error handling
        pass
    
    return redirect('/')


@app.route('/check_in', methods=['POST'])
def check_in():
    
    request_info = request.get_json()
    user_id = request_info['user_id']
    event_id = request_info['event_id']

    profile = db.session.get(Profile, user_id)
    event = db.session.get(Event, event_id)

    if profile and event:
        # FIX: check in needs to be reworked
        event.check_in_attendee(user_id)
        db.session.commit()
    else:
        # TODO: error handling
        pass

    return redirect('/')


# TODO: Rework with socket
# FIX: rework with the split app model
@app.route('/toggle_user_break', methods=[])
def toggle_user_break():

    request_info = request.get_json()
    user_id = request_info['user_id']

    profile = db.session.get(Profile, user_id)

    if profile:
        profile.toggle_break()
        db.session.commit()
    else:
        # TODO: error handling
        pass

    return redirect('/')

# TODO?: rework with sockets
# FIX?: rework with the split app model
@app.route('/block_user', methods=['POST'])
def block_user():
    request_info = request.get_json()
    user_a_id = request_info['user_a_id']
    user_b_id = request_info['user_b_id']

    user_a = db.session.get(Profile, user_a_id)
    user_b = db.session.get(Profile, user_b_id)

    # FIX: the blocked list is broken in the database
    user_a.block_user(user_b)
    db.session.commit()


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


@app.route('/start_event', methods=['POST'])
def start_event():

    event_info = request.get_json()
    event_id = event_info['event_id']

    event = db.session.get(Event, event_id)

    if event:
        event.start_event()
        db.session.commit()
    else:
        # TODO: error handling
        pass

    return redirect('/')


@app.route('/end_event', methods=[])
def end_event(event_id: int):

    event_info = request.get_json()
    event_id = event_info['event_id']

    event = db.session.get(Event, event_id)

    if event:
        event.end_event()
        db.session.commit()
    else:
        # TODO: error handling
        pass

    return redirect('/')


@app.route('/make_pairs', methods=['POST'])
def make_pairs():

    people = db.session.query(Profile).all()

    request_info = request.get_json()
    event_id = request_info['event_id']

    event = db.session.get(Event, event_id)

    # ----- Test stuff -----
    # for p in people:
    #     event.add_attendee(p)
    #     # p.toggle_break()
    # db.session.commit()

    for p in people:
        p.dancing = True

    print(event.attendees)
    event.start_event()

    pairs = event.make_pairs()
    event.adjust_scores(pairs)
    db.session.commit()

    for a, b in pairs:
        a_sid = active_users[int(a)]
        b_sid = active_users[int(b)]

        profile_a = db.session.get(Profile, int(a))
        profile_b = db.session.get(Profile, int(b))

        socket.emit('send_pair',
                {"pair": f"a: {profile_b.name}"},
                    to=a_sid
                    )
        
        socket.emit('send_pair',
                    {'pair': profile_a.name},
                    to=b_sid
                    )

    return redirect('/')


# TODO: figure out the logistics on this
# @app.route()
def accept_decline():
    # Q: What happens on decline? Repaired? just not paired?
    pass


# Q: how does starting a dance fit with accept/decline??? esspecially if you don't get the location detection going
# is it really needed?

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
def disconnect():
    active_users.pop(request.sid)
    print(f'Disconnected {request.sid}')


# TODO: link sources
if __name__ == "__main__":

    with app.app_context():
        db.create_all()

    socket.run(app, debug=True)

    # Save all changes made
    db.session.commit()
