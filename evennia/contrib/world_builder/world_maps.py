# -*- coding: utf-8 -*-
"""
Example world maps for the world builder.
"""

# Tethysia World Map
#
#  ~ - Ocean
#  F - Forest Zone
#  M - Mountain Zone
#  C - City Zone

TETHYSIA_MAP = """
~~~~~~~~
~F-M-C~
~~~~~~~~
"""

TETHYSIA_LEGEND = {
    "F": {
        "map": """
# Forest Zone Map
#
# f - forest
# r - river
#
fffrfff
fffrfff
fffrfff
""",
        "legend": {
            "f": "evennia.contrib.world_builder.world_maps.build_forest_room",
            "r": "evennia.contrib.world_builder.world_maps.build_river_room",
        },
    },
    "M": {
        "map": """
# Mountain Zone Map
#
# m - mountain
# c - cave
#
mmcmmmm
mmcmmmm
mmcmmmm
""",
        "legend": {
            "m": "evennia.contrib.world_builder.world_maps.build_mountain_room",
            "c": "evennia.contrib.world_builder.world_maps.build_cave_room",
        },
    },
    "C": {
        "map": """
# City Zone Map
#
# s - street
# h - house
#
shshs
shshs
shshs
""",
        "legend": {
            "s": "evennia.contrib.world_builder.world_maps.build_street_room",
            "h": "evennia.contrib.world_builder.world_maps.build_house_room",
        },
    },
}

def build_forest_room(x, y, **kwargs):
    from evennia import create_object
    from evennia.objects.objects import DefaultRoom as Room
    room = create_object(Room, key=f"Forest ({x},{y})")
    room.db.desc = "A quiet part of the forest."
    return room

def build_river_room(x, y, **kwargs):
    from evennia import create_object
    from evennia.objects.objects import DefaultRoom as Room
    room = create_object(Room, key=f"River ({x},{y})")
    room.db.desc = "A river flows here."
    return room

def build_mountain_room(x, y, **kwargs):
    from evennia import create_object
    from evennia.objects.objects import DefaultRoom as Room
    room = create_object(Room, key=f"Mountain ({x},{y})")
    room.db.desc = "A rocky mountain path."
    return room

def build_cave_room(x, y, **kwargs):
    from evennia import create_object
    from evennia.objects.objects import DefaultRoom as Room
    room = create_object(Room, key=f"Cave ({x},{y})")
    room.db.desc = "A dark cave."
    return room

def build_street_room(x, y, **kwargs):
    from evennia import create_object
    from evennia.objects.objects import DefaultRoom as Room
    room = create_object(Room, key=f"Street ({x},{y})")
    room.db.desc = "A bustling city street."
    return room

def build_house_room(x, y, **kwargs):
    from evennia import create_object
    from evennia.objects.objects import DefaultRoom as Room
    room = create_object(Room, key=f"House ({x},{y})")
    room.db.desc = "A cozy little house."
    return room

TETHYSIA_DATA = {
    "quests": [],
    "lore": [],
}
