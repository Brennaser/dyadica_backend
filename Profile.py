"""
Profile class for Dyadica.

author: Brenn Sermania
version: 11/20/2025
"""
from Field import Field

class Profile:

    def __init__(self, id: int, name: str, fields: list[Field], blocked: list[int], events: list):
        self.id = id
        self.name = name
        self.fields = fields
        self.blocked = blocked
        self.events = events

