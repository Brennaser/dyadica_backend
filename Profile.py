"""
Profile class for Dyadica.

author: Brenn Sermania
version: 11/20/2025
"""
import Event

from extensions import db, event_profile_table

class Profile(db.Model):

    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)

    events = db.relationship("Event",
                             secondary=event_profile_table,
                             back_populates='attendees')

    name = db.Column(db.String(25), unique=False, nullable=False)
    fields = db.Column(db.JSON, unique=False, nullable=False)
    dancing = db.Column(db.Boolean, unique=False, nullable=False)
    # TODO: make this one-many relationship
    # blocked = db.relationship("Profile", ForeignKey("profiles.id"))

    def __init__(self, name: str, fields: dict):
        self.name = name
        self.fields = fields
        self.dancing = False
        # NOTE: blocked is not in database atm
        self.blocked = set()


    def update_name(self, new_name: str):
        self.name = new_name


    def update_fields(self, new_fields: dict):
        self.fields = new_fields


    def block_user(self, other):
        self.blocked.append(other)


    def unblock_user(self, other_id: int):
        self.blocked.discard(other_id)


    def add_event(self, new_event: Event):
        self.events.append(new_event)


    def remove_event(self, event: Event):
        self.events.delete(event)


    def toggle_break(self):
        self.dancing =  not self.dancing
        db.session.commit()


    def __repr__(self):
        return f'{self.name}, {self.id}, dancing: {self.dancing}, rsvped: {[event.name for event in self.events]}'

