from Field import Field, Field_Type
from Event import Event
from Profile import Profile

"""
Main executable for Dyadica.

author: Brenn Sermania
version: 11/20/2025
"""
def save_event_data():
    pass


def save_profile_data():
    pass


def load_event_data():
    pass


def load_profile_data():
    pass


if __name__ == "__main__":
    event = Event("name", "date", 'location', 1, 1)

    lead = Field(Field_Type.Lead_Follow, ["lead", "follow"], True, [1, 0])
    follow = Field(Field_Type.Lead_Follow, ["lead", "follow"], True, [0, 1])
    lead_follow = Field(Field_Type.Lead_Follow, ["lead", "follow"], True, [1 ,1])

    style = Field(Field_Type.Style, ["lindy", "westie"], False, [1, 1])
    style1 = Field(Field_Type.Style, ["lindy", "westie"], False, [1, 0])

    pos = Field(Field_Type.Position, ['open', 'closed', 'close embrace'], False, [1, 1, 1])
    pos1 = Field(Field_Type.Position, ['open', 'closed', 'close embrace'], False, [0, 1, 0])

    # TODO: test magnetic fields
    p = Profile(1, "1", {"style": style1, "position": pos, "lead\follow": lead_follow})
    p.add_event(1)
    p2 = Profile(2, "2", {"style": style, "position": pos, "lead\follow": follow})
    p2.add_event(1)
    p3 = Profile(3, "3", {"style": style, "position": pos, "lead\follow": lead})
    p3.add_event(1)
    p4 = Profile(4, "4", {"style": style1, "position": pos1, "lead\follow": follow})
    p4.add_event(1)


    event.add_attendee(p)
    event.check_in_attendee(1)

    event.add_attendee(p2)
    event.check_in_attendee(2)

    event.add_attendee(p3)
    event.check_in_attendee(3)

    event.add_attendee(p4)
    event.check_in_attendee(4)

    event.start_event()

    for i in range(5):
        print(f"Round {i}:")

        pairs = event.make_pairs()

        [print(f"\t{a} {b}") for a, b in pairs]

        event.adjust_scores(pairs)
