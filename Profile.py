"""
Profile class for Dyadica.

author: Brenn Sermania
version: 11/20/2025
"""
from Field import Field

class Profile:

    def __init__(self, name: str, fields: list[Field]):
        self.name = name

        self.fields = fields

        self.pairing = False


    def toggle_pairing(self):
        self.pairing = not self.pairing

    

