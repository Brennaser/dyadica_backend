"""
Event class for Dyadica.

author: Brenn Sermania
version: 11/20/2025
"""
# ---------- Imports ----------
import numpy as np
import pandas as pd 

from Field import Field

class Event:

    def __init__(self, name, date, location, owner, id):

        self.name = name
        self.date = date
        self.location = location
        self.owner = owner
        self.id = id

        # Key: Profile.id, Value: Fields
        self.attendees = {}

        # TODO: Research pandas.MultiIndex and/or xarray
        # Depth of 6 -> three fields + recent penalty + attending + pairing
        self.pair_matrix = np.zeros(shape=(-1, -1, 6))

        # TODO: Figure this out
        self.access_code = None

        self.ongoing = False
        self.pairing = False

    
    def add_attendee(self, id: int, fields: list[Field]):
        self.attendees[id] = fields


    def check_in_attendee(self):
        pass


    def make_pairs(self):
        pass


