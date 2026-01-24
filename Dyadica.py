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

def save_event_data():
    # TODO
    pass


def save_profile_data():
    # TODO
    pass


def load_event_data():
    # TODO
    pass


def load_profile_data():
    # TODO
    pass


def get_profile(user_id: int) -> Profile:
    # TODO
    pass


def new_profile_id():
    # TODO
    pass

def get_event(event_id: int) -> Event:
    # TODO
    pass


def new_event_id():
    # TODO
    pass

@app.route('/update_profile', methods=[])
def update_profile(user_id: int):

    # Q: How is info being passed? what format???
    # Q: how to identify and make new profiles??? or i guess know when to allocate a new user id
    # you plan on using local (phone storge) to keep the id linked to the device
    # if that local data does not exist, make a new proofile
    # does introduc the issue of how can users log in on other devices, but ya know what?
    # it'll work for a user study

    profile = get_profile(user_id)

    if profile:
        # TODO
        pass
    else:
        # TODO: error handling
        pass

    pass


@app.route('/rsvp', methods=[])
def rsvp(user_id: int, event_id: int):

    profile = get_profile(user_id)
    event = get_event(event_id)

    if profile and event:
        event.add_attendee(profile)
    else:
        # TODO: error handling
        pass


@app.route('/check_in', methods=[])
def check_in(user_id: int, event_id: int):
    
    profile = get_profile(user_id)
    event = get_event(event_id)

    if profile and event:
        event.check_in_attendee(user_id)
    else:
        # TODO: error handling
        pass


@app.route('/toggle_user_break', methods=[])
def toggle_user_break(user_id: int):

    # bro, wires, everywhere. the flag for this is in the event class, but you get the user id
    # maybe add a current event attr in Profile?
    # Or loop over profile event list for the first (and theoretically only) active one <- <- <-
    # TODO
    pass


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
        print(event.id)
        pass
    else:
        # TODO: error handling
        pass

    return redirect('/')

@app.route('/test')
def test():
    t = db.session.get(Event, 7)
    print(t.__repr__())
    return t.__repr__()

@app.route('/update_event', methods=[])
def update_event(event_id: int):

    # Q: same q as update_profile, how we getting that data???
    # TODO
    pass


@app.route('/start_event', methods=[])
def start_event(event_id: int):

    event = get_event(event_id)

    if event:
        event.start_event()
    else:
        # TODO: error handling
        pass


@app.route('/end_event', methods=[])
def end_event(event_id: int):
    
    event = get_event(event_id)

    if event:
        event.end_event()
    else:
        # TODO: error handling
        pass


@app.route('/make_pairs', methods= ["GET"])
def make_pairs():

    # TODO make better lmao
    event = Event("name", "date", 'location', 1, 1)

    lead = Field(Field_Type.Lead_Follow, ["lead", "follow"], True, [1, 0])
    follow = Field(Field_Type.Lead_Follow, ["lead", "follow"], True, [0, 1])
    lead_follow = Field(Field_Type.Lead_Follow, ["lead", "follow"], True, [1 ,1])

    style = Field(Field_Type.Style, ["lindy", "westie"], False, [1, 1])
    style1 = Field(Field_Type.Style, ["lindy", "westie"], False, [1, 0])

    pos = Field(Field_Type.Position, ['open', 'closed', 'close embrace'], False, [1, 1, 1])
    pos1 = Field(Field_Type.Position, ['open', 'closed', 'close embrace'], False, [0, 1, 0])

    # TODO: test magnetic fields
    p = Profile(1, "1", {"style": style1, "position": pos, "lead\follow": lead_follow})
    p.add_event(1)
    p2 = Profile(2, "2", {"style": style, "position": pos, "lead\follow": follow})
    p2.add_event(1)
    p3 = Profile(3, "3", {"style": style, "position": pos, "lead\follow": lead})
    p3.add_event(1)
    p4 = Profile(4, "4", {"style": style1, "position": pos1, "lead\follow": follow})
    p4.add_event(1)


    event.add_attendee(p)
    event.check_in_attendee(1)

    event.add_attendee(p2)
    event.check_in_attendee(2)

    event.add_attendee(p3)
    event.check_in_attendee(3)

    event.add_attendee(p4)
    event.check_in_attendee(4)

    event.start_event()


    pairs = event.make_pairs()


    event.adjust_scores(pairs)

    return jsonify({"pairs": int(pairs[0][0])})


# TODO: figure out the logistics on this
# @app.route()
def accept_decline():
    # Q: What happens on decline? Repaired? just not paired?
    pass


# Q: how does starting a dance fit with accept/decline??? esspecially if you don't get the location detection going
# is it really needed?


if __name__ == "__main__":
    # TODO: Load events
    # TODO: load profiles
    # app.run(host='0.0.0.0', debug=True)

    with app.app_context():
        db.create_all()

    app.run(debug=True)

