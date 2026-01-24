"""
Profile class for Dyadica.

author: Brenn Sermania
version: 11/20/2025
"""
from Field import Field

from extensions import db, event_profile_table

class Profile(db.Model):

    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)

    events = db.relationship("Event",
                             secondary=event_profile_table,
                             back_populates='profile')

    def __init__(self, name: str, fields: dict):
        self.name = name
        self.fields = fields
        self.blocked = set()
        self.events = set()


    def update_name(self, new_name: str):
        self.name = new_name


    def update_fields(self, new_fields: dict):
        self.fields = new_fields


    def block_user(self, other_id: int):
        self.blocked.add(other_id)


    def unblock_user(self, other_id: int):
        self.blocked.discard(other_id)


    def add_event(self, new_event: int):
        self.events.add(new_event)


    def remove_event(self, event: int):
        self.events.discard(event)

