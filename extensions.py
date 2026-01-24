"""This module exists so both Dyadica and the Event and Profile modules have access to db"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, ForeignKey, Column

db = SQLAlchemy()

# https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#many-to-many
event_profile_table = Table(
    "event_profile_table",
    db.metadata,
    Column("event", ForeignKey("events.id"), primary_key=True),
    Column("profile", ForeignKey("profiles.id"), primary_key=True)
)

