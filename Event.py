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

        # Key: Profile.id, Values: {Fields, Attending}
        self.attendees = {}

        # TODO: Research pandas.MultiIndex and/or xarray
        # Depth of 5 -> three fields + recent penalty  + pairing
        self.pair_matrix = np.zeros(shape=(-1, -1, 5))

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


