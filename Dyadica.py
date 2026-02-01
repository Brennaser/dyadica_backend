from flask import Flask, jsonify, request, redirect, render_template
from flask_socketio import SocketIO, send, emit

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


@app.route('/new_profile', methods=['POST'])
def new_profile():
    profile_info = request.get_json()
    name = profile_info['name']
    fields = profile_info['fields']

    if name != '' and fields:
        profile = Profile(name, fields)
        db.session.add(profile)
        db.session.commit()
        # TODO: send back user id
    else:
        # TODO: error handling
        pass

    return redirect('/')


@app.route('/update_profile', methods=['POST'])
def update_profile(user_id: int):

    profile_info = request.get_json()
    user_id = profile_info['id']
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

# @app.route('/test')
def test():
    t = db.session.get(Profile, 1)
    print(t.__repr__())
    return t.__repr__()

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

    request_info = request.get_json()
    request_info = request.get_json()
    event_id = request_info['event_id']

    event = db.session.get(Event, event_id)
    pairs = event.make_pairs()
    event.adjust_scores(pairs)

    return jsonify({"pairs": [(int(a), int(b)) for a, b in pairs]})


@app.route('/test_make_pairs', methods= ["GET"])
def test_make_pairs():

    # TODO make better lmao
    # event = Event("name", "date", 'location', 1)
    # db.session.add(event)
    # lead = [1, 0]
    # follow = [0, 1]
    # lead_follow = [1 ,1]

    # style = [1, 1]
    # style1 = [1, 0]

    # pos = [1, 1, 1]
    # pos1 = [0, 1, 0]

    # # TODO: test magnetic fields
    # p = Profile(name="1", fields={"style": style1, "position": pos, "lead/follow": lead_follow})
    # db.session.add(p)
    # p2 = Profile(name="2", fields={"style": style, "position": pos, "lead/follow": follow})
    # db.session.add(p2)
    # p3 = Profile(name="3", fields={"style": style, "position": pos, "lead/follow": lead})
    # db.session.add(p3)
    # p4 = Profile(name="4", fields={"style": style1, "position": pos1, "lead/follow": follow})
    # db.session.add(p4)

    # db.session.commit()

    # event.attendees.append(p)

    # event.attendees.append(p2)

    # event.attendees.append(p3)

    # event.attendees.append(p4)

    # # NOTE: in liue of checking-in
    # for i in range(1, 5):
    #     px = db.session.get(Profile, i)
    #     px.toggle_break()

    # event.start_event()

    event = db.session.get(Event, 1)
    p2 = db.session.get(Profile, 2)
    p2.toggle_break()
    db.session.commit()
    print("*"*20)
    pairs = event.make_pairs()

    print(p2.dancing)
    for _ in range(5):
        print(pairs)
        event.adjust_scores(pairs)
        p2.toggle_break()
        db.session.commit()
        pairs = event.make_pairs()
    print(pairs)
    db.session.commit()
    return jsonify({"pairs": [(int(a), int(b)) for a, b in pairs]})


# TODO: figure out the logistics on this
# @app.route()
def accept_decline():
    # Q: What happens on decline? Repaired? just not paired?
    pass


# Q: how does starting a dance fit with accept/decline??? esspecially if you don't get the location detection going
# is it really needed?
@app.route('/')
def index():
    return render_template('index.html')


@socket.on('connect')
def test():
    print("Connected")

@socket.on("my_event")
def event(data):
    socket.send(data, callback=lambda: print("it happened!"))


# Handle user messages
@socket.on('message')
def handle_message(data):
    print(data)
    socket.emit("message", f"You said: {data}")  # Send to everyone


if __name__ == "__main__":
    # app.run(host='0.0.0.0', debug=True)

    with app.app_context():
        db.create_all()

    # app.run(debug=True)
    socket.run(app, debug=True)

    # Save all changes made
    db.session.commit()
