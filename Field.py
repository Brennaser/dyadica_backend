"""
Field class for Dyadica.

author: Brenn Sermania
version: 11/20/2025
"""
from enum import Enum

class Field_Type(Enum):
    Lead_Follow = 0
    Style = 1
    Position = 2

class Field:

    def __init__(self, name: Field_Type, options: list, magnetic: bool, selected: list):
        self.name = name
        self.options = options
        self.magnetic = magnetic
        self.selected = selected

    def get_score(self, other: Field):

        if self.name is other.name:
            score = 0 

            if self.magnetic:
                # TODO: finish
                pass
            else:
                for i in len(self.selected):
                    if self.selected[i] == other.selected[i]:
                        score += 1
                
            return score

        return -1
