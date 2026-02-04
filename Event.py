"""
Event class for Dyadica.

author: Brenn Sermania
version: 11/20/2025
"""
# ---------- Imports ----------
import numpy as np
import pandas as pd 
from io import StringIO

from Profile import Profile

from extensions import db, event_profile_table

class Event(db.Model):

    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25), unique=False, nullable=False)
    date = db.Column(db.String(25), unique=False, nullable=False)
    location = db.Column(db.String(25), unique=False, nullable=False)
    owner = db.Column(db.Integer, nullable=False)

    attendees = db.relationship("Profile",
                                secondary=event_profile_table,
                                back_populates="events")
    
    ongoing = db.Column(db.Boolean, nullable=False)
    pairing = db.Column(db.Boolean, nullable=False)

    # TODO: save these values when they change
    # NOTE: do this in the main class
    # FIX: sqlalchemy.exc.StatementError: (builtins.TypeError) Object of type DataFrame is not JSON serializable
    pair_scores = db.Column(db.JSON, nullable=False)
    max_pair_scores = db.Column(db.JSON, nullable=False)

    def __init__(self, name, date, location, owner):

        self.name = name
        self.date = date
        self.location = location
        self.owner = owner

        # TODO: Figure this out
        # Probably somthing like /event_rsvp/{event_id}
        self.access_code = None

        self.ongoing = False
        self.pairing = False

        self.pair_scores = ''
        self.max_pair_scores = ''

        # FIX: checked-in flags are broken

    def scores_to_json(self, pair_scores, max_pair_scores):
        self.pair_scores = pair_scores.to_json()
        self.max_pair_scores = max_pair_scores.to_json()
    

    def scores_to_df(self):
        return pd.read_json(StringIO(self.pair_scores)), pd.read_json(StringIO(self.max_pair_scores))

    
    def add_attendee(self, attendee: Profile):
        self.attendees.append(attendee)
        # self.attendees[attendee.id] = {"profile": attendee,
        #                                "checked_in": False,
        #                                "dancing": False}


    def check_in_attendee(self, attendee_id: int):
        # TODO: make relavant wth???
        pass
        # self.attendees[attendee_id]["checked_in"] = True
        # self.attendees[attendee_id]['dancing'] = True


    def toggle_attendee_dancing(self, attendee_id: int):
        self.attendees[attendee_id]['dancing'] = not self.attendees[attendee_id]['dancing']


    def calculate_pair_score(self, a_fields: dict, b_fields: dict):

        # NOTE: fields are hard coded
        pair_score = 0

        # Check Lead/Follow (Binary Magnetic)
        a_lead_follow = a_fields["lead/follow"]
        b_lead_follow = b_fields['lead/follow']

        if (a_lead_follow["Lead"] and b_lead_follow["Follow"]) or (a_lead_follow["Follow"] and b_lead_follow["Lead"]):
            pair_score += 1
        else:
            # Invalid pairing
            return -1
        
        # Check Style
        a_style = a_fields['style']
        b_style = b_fields['style']

        for i in a_style.keys():
            if a_style[i] == b_style[i]:
                pair_score += 1

        # Check Position
        a_pos = a_fields['position']
        b_pos = b_fields['position']

        for i in a_pos.keys():
            if a_pos[i] == b_pos[i]:
                pair_score += 1
        
        return pair_score


    def start_event(self):

        dancers = self.attendees

        pair_scores = np.full(shape=(len(dancers), len(dancers)),
                                   fill_value= np.nan)
        pair_scores = pd.DataFrame(pair_scores)

        # Name columns and rows after attendee_ids
        dancer_ids = [dancer.id for dancer in dancers]
        pair_scores.index = dancer_ids
        pair_scores.columns = dancer_ids

        for dancer_a in dancers:

            a_fields = dancer_a.fields

            # drop -> do not try to partner a person with themself
            for dancer_b in dancers:

                # Skip if the same attendee
                if dancer_b.id == dancer_a.id:
                    continue
                
                # FIX: blocked is null
                # if one dancer has the other blocked, leave pair_score as np.nan
                # if dancer_b in dancer_a.blocked or \
                #     dancer_a in dancer_b.blocked:
                #     continue

                # if neither dancer has the other blocked
                if np.isnan(pair_scores[dancer_a.id][dancer_b.id]):

                    b_fields = dancer_b.fields

                    pair_score = self.calculate_pair_score(a_fields, b_fields)

                    
                    pair_scores[dancer_a.id][dancer_b.id] = pair_score
                    pair_scores[dancer_b.id][dancer_a.id] = pair_score

        # Normalize scores
        score_min = pair_scores.min().min()
        score_max = pair_scores.max().max()

        # FIX: identidy diagonal is getting set to 1 as well
        if score_max == score_min:
            # iff all scores are the same, set them all to one
            pair_scores = pd.DataFrame(1, index=pair_scores.index, columns=pair_scores.columns)
        else:
            # else, just normalize scores
            pair_scores = (pair_scores - score_min) / (score_max - score_min)



        # Deep Copy of pair_scores to serve as a baseline
        max_pair_scores = pair_scores.copy()     

        self.scores_to_json(pair_scores, max_pair_scores)
        # Tell Dyadica to start checking this event
        self.ongoing = True


    def end_event(self):
        self.ongoing = False


    def new_blocked_pair(self, dancer_a: int, dancer_b: int):

        pair_scores, max_pair_scores = self.scores_to_df()

        pair_scores[dancer_a][dancer_b] = np.nan
        pair_scores[dancer_b][dancer_a] = np.nan

        max_pair_scores[dancer_a][dancer_b] = np.nan
        max_pair_scores[dancer_b][dancer_a] = np.nan

        self.scores_to_json(pair_scores, max_pair_scores)


    # Do users even need to be able to unblock a user during an event???
    # NOTE: no, not neccessary for this user study
    def unblock_pair(self, dancer_a: int, dancer_b: int):

        a_fields = self.attendees[dancer_a]['profile'].fields
        b_fields = self.attendees[dancer_b]['profile'].fields

        pair_score = self.calculate_pair_score(a_fields, b_fields)
        
        # FIX: Not normalized!!!!!

        pair_scores, max_pair_scores = self.scores_to_df()

        pair_scores[dancer_a][dancer_b] = pair_score
        pair_scores[dancer_b][dancer_a] = pair_score

        max_pair_scores[dancer_a][dancer_b] = pair_score
        max_pair_scores[dancer_b][dancer_a] = pair_score

        self.scores_to_json(pair_scores, max_pair_scores)


    def make_pairs(self):

        pair_scores, _ = self.scores_to_df()

        # Mask out those who are not dancing
        dancing_mask = pd.DataFrame([dancer.dancing for dancer in self.attendees], index=[dancer.id for dancer in self.attendees])
        dancing_mask = dancing_mask[dancing_mask[0]].index

        dancing = pair_scores.loc[dancing_mask][dancing_mask]

        print(dancing)
        best_pair = np.nanargmax(dancing, axis=1)
        best_weights = [dancing[row].iloc[best_pair[i]] for i, row in enumerate(dancing)]
        sorted_pairs = np.argsort(best_weights)[::-1]

        paired = np.full((len(best_pair)), False)
        pairings = []

        dancer_ids = dancing.index

        for dancer_a_idx in sorted_pairs:
            dancer_b_idx = best_pair[dancer_a_idx]
            
            if not paired[dancer_a_idx] and not paired[dancer_b_idx]:
                pairings.append((dancer_ids[dancer_a_idx], dancer_ids[dancer_b_idx]))
                paired[dancer_a_idx] = True
                paired[dancer_b_idx] = True

            # TODO: FIX: No recovery if best_pair[dancer_a] is already paired
            # ^^ implies disagreement between dancers
            # best_pair[dancer_a] = next highest weight index in w[dancer_a]
            # NOTE: Greedy in this sense; could potentially account for that by changing best_pair values to try and ensure they still get a partner???
            # Even so, this algorithm is likely still going to be greedy and that's honestly fine
            # Our primary concern is making pairs; approximate solutions are acceptable

            # Could rerun the highest score stuff masking out the paired dancers

            # Finish early if all dancers have been paired
            if np.all(paired):
                break

        return pairings
    

    def adjust_scores(self, pairs):

        pair_scores, max_pair_scores = self.scores_to_df()

        for row in pair_scores.index:
            for col in pair_scores.columns:
                # <= so that even the lowest scoring possible pair has a chance
                if pair_scores[row][col] <= max_pair_scores[row][col]:
                    pair_scores[row][col] += 0.1
        
        for a, b in pairs:
            pair_scores[b][a] = 0
            pair_scores[a][b] = 0

        self.scores_to_json(pair_scores, max_pair_scores)


    def __repr__(self):
        return f"Event Name: {self.name}, Date: {self.date} {self.id} Owner: {self.owner}\nPair Scores:\n{self.pair_scores}"

