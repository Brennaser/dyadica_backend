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

        # TODO: Figure this out
        self.access_code = None

        self.ongoing = False
        self.pairing = False

        self.pair_scores = None
        self.max_pair_scores = None

    
    def add_attendee(self, attendee_id: int, fields: list[Field]):
        self.attendees[attendee_id] = {"fields": fields,
                                       "checked_in": False,
                                       "dancing": False}


    def check_in_attendee(self, attendee_id: int):
        self.attendees[attendee_id]["checked_in"] = True
        self.attendees[attendee_id]['dancing'] = True


    def toggle_attendee_dancing(self, attendee_id: int):
        self.attendees[attendee_id]['dancing'] = not self.attendees[attendee_id]['dancing']
        

    def start_event(self):

        dancers = pd.DataFrame.from_dict(self.attendees, orient="index")

        self.pair_scores = np.full(shape= (dancers.shape[0], dancers.shape[0]),
                                   fill_value= np.nan)
        self.pair_scores = pd.DataFrame(self.pair_scores)

        # Name columns and rows after attendee_ids
        self.pair_scores.index = dancers.index
        self.pair_scores.columns = dancers.index

        for dancer_a in dancers.index:

            a_fields = dancers['fields'][dancer_a]

            # drop -> do not try to partner a person with themself
            for dancer_b in dancers.drop(dancer_a).index:
                if np.isnan(self.pair_scores[dancer_a][dancer_b]):
                    pair_score = 0

                    b_fields = dancers['fields'][dancer_b]

                    for i in range(len(a_fields)):
                        score = a_fields[i].get_score(b_fields[i])

                        # if the pair is invaild -> stop evaluating this pair
                        if score == -1:
                            pair_score = np.nan
                            break
                        else:
                            pair_score += score
                    
                    self.pair_scores[dancer_a][dancer_b] = pair_score
                    self.pair_scores[dancer_b][dancer_a] = pair_score

        # Normalize scores
        # TODO: Fix when all scores are the same, this replaces them all with NaN
        score_min = self.pair_scores.min().min()
        score_max = self.pair_scores.max().max()
        self.pair_scores = (self.pair_scores - score_min) / (score_max - score_min)

        # Deep Copy of pair_scores to serve as a baseline
        self.max_pair_scores = self.pair_scores.copy()

        # Tell Dyadica to start checking this event
        self.ongoing = True


    def make_pairs(self):

        # Mask out those who are not dancing
        dancing_mask = pd.DataFrame.from_dict(self.attendees, orient="index")
        dancing_mask = dancing_mask[dancing_mask['dancing']].index

        dancing = self.pair_scores.loc[dancing_mask][dancing_mask]


        best_pair = np.nanargmax(dancing, axis=1)
        best_weights = [dancing[row].iloc[best_pair[i]] for i, row in enumerate(dancing)]
        sorted_pairs = np.argsort(best_weights)[::-1]

        paired = np.full((len(best_pair)), False)
        pairings = []

        # TODO: refactor to attendee_ids
        names = dancing.index

        for dancer_a_idx in sorted_pairs:
            dancer_b_idx = best_pair[dancer_a_idx]
            
            if not paired[dancer_a_idx] and not paired[dancer_b_idx]:
                pairings.append((names[dancer_a_idx], names[dancer_b_idx]))
                paired[dancer_a_idx] = True
                paired[dancer_b_idx] = True

            # FIX: No recovery if best_pair[dancer_a] is already paired
            # ^^ implies disagreement between dancers
            # best_pair[dancer_a] = next highest weight index in w[dancer_a]
            # NOTE: Greedy in this sense; could potentially account for that by changing best_pair values to try and ensure they still get a partner???
            # Even so, this algorithm is likely still going to be greedy and that's honestly fine
            # Our primary concern is making pairs; approximate solutions are acceptable

            # Finish early if all dancers have been paired
            if np.all(paired):
                break

        return pairings
    

    def adjust_scores(self, pairs):

        for row in self.pair_scores.index:
            for col in self.pair_scores.columns:
                # <= so that even the lowest scoring possible pair has a chance
                if self.pair_scores[row][col] <= self.max_pair_scores[row][col]:
                    self.pair_scores[row][col] += 0.1
        
        for a, b in pairs:
            self.pair_scores[b][a] = 0
            self.pair_scores[a][b] = 0

