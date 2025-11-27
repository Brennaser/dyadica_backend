"""
Field class for Dyadica.

author: Brenn Sermania
version: 11/20/2025
"""
class Field:

    def __init__(self, name: str, options: list, matching_or_magnetic: bool, selected: list):
        self.name = name
        self.options = options
        self.matching_or_magnetic = matching_or_magnetic
        self.selected = selected

