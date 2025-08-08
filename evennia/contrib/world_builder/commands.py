# -*- coding: utf-8 -*-
"""
Commands for the world builder.
"""

from django.conf import settings
from evennia.utils import utils
from evennia.commands.default.muxcommand import MuxCommand
from evennia.contrib.world_builder.world_builder import WorldBuilder

COMMAND_DEFAULT_CLASS = utils.class_from_module(settings.COMMAND_DEFAULT_CLASS)

class CmdWorldBuilder(COMMAND_DEFAULT_CLASS):
    """
    Build a world from a world map.

    Usage:
        @worldbuilder <path.to.world.map> <path.to.world.legend> <path.to.world.data>

    Example:
        @worldbuilder evennia.contrib.world_builder.world_maps.TETHYSIA_MAP evennia.contrib.world_builder.world_maps.TETHYSIA_LEGEND evennia.contrib.world_builder.world_maps.TETHYSIA_DATA
    """

    key = "@worldbuilder"
    locks = "cmd:superuser()"
    help_category = "Building"

    def func(self):
        """Starts the processor."""

        caller = self.caller
        args = self.args.split()

        # Check if arguments passed.
        if not self.args or (len(args) != 3):
            caller.msg("Usage: @worldbuilder <path.to.world.map> <path.to.world.legend> <path.to.world.data>")
            return

        # Set up base variables.
        world_map = None
        world_legend = None
        world_data = None

        # OBTAIN MAP FROM MODULE
        path_to_map = args[0]
        try:
            world_map = utils.variable_from_module(*path_to_map.rsplit('.', 1))
        except Exception as e:
            caller.msg(f"Error loading world map: {e}")
            return

        # OBTAIN LEGEND FROM MODULE
        path_to_legend = args[1]
        try:
            world_legend = utils.variable_from_module(*path_to_legend.rsplit('.', 1))
        except Exception as e:
            caller.msg(f"Error loading world legend: {e}")
            return

        # OBTAIN DATA FROM MODULE
        path_to_data = args[2]
        try:
            world_data = utils.variable_from_module(*path_to_data.rsplit('.', 1))
        except Exception as e:
            caller.msg(f"Error loading world data: {e}")
            return

        # Create the world builder and run it
        builder = WorldBuilder(caller, world_map, world_legend, world_data)
        builder.build()
        # builder.visualize("world_map") # we are not testing this for now
        builder.generate_player_guide("player_guide.md")
        builder.generate_developer_guide("developer_guide.md")

        caller.msg("World built successfully.")
