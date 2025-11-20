"""
Event class for Dyadica.

author: Brenn Sermania
version: 11/20/2025
"""
# ---------- Imports ----------
import numpy as np
import pandas as pd 

class Event:

    def __init__(self, name, date, location, owner, id):

        self.name = name
        self.date = date
        self.location = location
        self.owner = owner
        self.id = id

        # Key: Profile.id, Value: Fields
        self.attendees = {}

        # Depth of five -> three fields + recent penalty
        self.pair_matrix = np.zeros(shape=(-1, -1, 4))

        # TODO: Figure this out
        self.access_code = None

        self.ongoing = False
        self.pairing = False


