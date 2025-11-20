"""
Field class for Dyadica.

author: Brenn Sermania
version: 11/20/2025
"""
class Field:

    def __init__(self, name: str, options: list, isMatching: bool, selected: list):
        self.name = name
        self.options = options
        self.isMatching = isMatching
        self.selected = selected

