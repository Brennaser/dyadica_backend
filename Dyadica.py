from flask import Flask, jsonify, request, redirect

from extensions import db

from Field import Field, Field_Type
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
    else:
        # TODO: error handling
        pass

    return redirect('/')


# @app.route('/block_user', methods=[])
# def block_user(user_id_a: int, user_id_b: int):
#     pass


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
    t = db.session.get(Profile, 1)
    print(t.__repr__())
    return t.__repr__()

@app.route('/update_event', methods=[])
def update_event(event_id: int):

    # Q: same q as update_profile, how we getting that data???
    # TODO
    pass


@app.route('/start_event', methods=['POST'])
def start_event(event_id: int):

    event_info = request.get_json()
    event_id = event_info['event_id']

    event = db.session.get(Event, event_id)

    if event:
        event.start_event()
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
    else:
        # TODO: error handling
        pass

    return redirect('/')

@app.route('/make_pairs', methods= ["GET"])
def make_pairs():

    # TODO make better lmao
    event = Event("name", "date", 'location', 1)
    db.session.add(event)
    lead = [1, 0]
    follow = [0, 1]
    lead_follow = [1 ,1]

    style = [1, 1]
    style1 = [1, 0]

    pos = [1, 1, 1]
    pos1 = [0, 1, 0]

    # TODO: test magnetic fields
    p = Profile(name="1", fields={"style": style1, "position": pos, "lead/follow": lead_follow})
    db.session.add(p)
    p2 = Profile(name="2", fields={"style": style, "position": pos, "lead/follow": follow})
    db.session.add(p2)
    p3 = Profile(name="3", fields={"style": style, "position": pos, "lead/follow": lead})
    db.session.add(p3)
    p4 = Profile(name="4", fields={"style": style1, "position": pos1, "lead/follow": follow})
    db.session.add(p4)

    db.session.commit()

    event.attendees.append(p)

    event.attendees.append(p2)

    event.attendees.append(p3)

    event.attendees.append(p4)

    # NOTE: in liue of checking-in
    for i in range(1, 5):
        px = db.session.get(Profile, i)
        px.toggle_break()

    event.start_event()

    event = db.session.get(Event, 1)
    pairs = event.make_pairs()

    for _ in range(5):
        print(pairs)
        event.adjust_scores(pairs)
        # p2.toggle_break()
        pairs = event.make_pairs()
    print(pairs)

    return jsonify({"pairs": [(int(a), int(b)) for a, b in pairs]})


# TODO: figure out the logistics on this
# @app.route()
def accept_decline():
    # Q: What happens on decline? Repaired? just not paired?
    pass


# Q: how does starting a dance fit with accept/decline??? esspecially if you don't get the location detection going
# is it really needed?


if __name__ == "__main__":
    # app.run(host='0.0.0.0', debug=True)

    with app.app_context():
        db.create_all()

    app.run(debug=True)

    # Save all changes made
    db.session.commit()
