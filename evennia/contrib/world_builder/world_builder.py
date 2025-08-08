# -*- coding: utf-8 -*-
"""
World builder module.

This module contains the functions and classes for building a world from a
collection of zone maps.
"""

from evennia import create_object
from evennia.utils import logger, utils
from evennia.contrib.grid.mapbuilder.mapbuilder import build_map
from evennia.objects.objects import DefaultExit as Exit

class WorldBuilder:
    """
    This class is responsible for building a world from a world map and a
    world legend.
    """

    def __init__(self, caller, world_map, world_legend, world_data=None):
        """
        Initializes the world builder.

        Args:
            caller (Object): The object calling the world builder.
            world_map (str): The ASCII representation of the world map.
            world_legend (dict): A dictionary mapping zone characters to zone
                data.
            world_data (dict, optional): A dictionary containing world-level
                data such as quests, lore, etc. Defaults to None.
        """
        self.caller = caller
        self.world_map = world_map
        self.world_legend = world_legend
        self.world_data = world_data or {}
        self.zones = {}  # Stores the created zones
        self.world_graph = None  # To be implemented

    def build(self):
        """
        Builds the world.
        """
        logger.log_info("Starting world build...")

        world_map_rows = self.world_map.strip().split('\n')
        for y, row in enumerate(world_map_rows):
            for x, zone_char in enumerate(row):
                if zone_char in self.world_legend and zone_char != '-':
                    logger.log_info(f"Building zone '{zone_char}' at ({x}, {y})...")
                    zone_data = self.world_legend[zone_char]
                    zone_map = zone_data["map"]
                    zone_legend = {}
                    for key, path in zone_data["legend"].items():
                        try:
                            zone_legend[key] = utils.variable_from_module(*path.rsplit('.', 1))
                        except Exception as e:
                            self.caller.msg(f"Error loading builder function: {e}")
                            return

                    # build_map returns a room_dict, but we need to pass a caller
                    # for now, we'll pass the world builder's caller.
                    room_dict = build_map(self.caller, zone_map, zone_legend)
                    self.zones[zone_char] = {
                        "map": zone_map,
                        "legend": zone_legend,
                        "rooms": room_dict,
                        "position": (x, y),
                    }
                    logger.log_info(f"Zone '{zone_char}' built.")

        self._connect_zones()

        logger.log_info("World build complete.")

    def _connect_zones(self):
        """
        Connects the zones based on the world map.
        """
        logger.log_info("Connecting zones...")
        world_map_rows = self.world_map.strip().split('\n')
        for y, row in enumerate(world_map_rows):
            for x, zone_char in enumerate(row):
                if zone_char == '-':
                    # Connect zones to the left and right
                    if x > 0 and x < len(row) - 1:
                        zone1_char = row[x-1]
                        zone2_char = row[x+1]
                        zone1 = self.zones.get(zone1_char)
                        zone2 = self.zones.get(zone2_char)

                        if not zone1 or not zone2:
                            logger.log_warning(f"Could not find zones for connection: {zone1_char}-{zone2_char}")
                            continue

                        room1 = next(iter(zone1["rooms"].values()), None)
                        room2 = next(iter(zone2["rooms"].values()), None)

                        if not room1 or not room2:
                            logger.log_warning(f"Could not find rooms to connect for {zone1_char}-{zone2_char}")
                            continue

                        exit_name1 = f"A path leading to {zone2['rooms'][next(iter(zone2['rooms']))].key}"
                        exit_name2 = f"A path leading to {zone1['rooms'][next(iter(zone1['rooms']))].key}"

                        create_object(Exit, key=exit_name1, location=room1, destination=room2)
                        create_object(Exit, key=exit_name2, location=room2, destination=room1)
                        logger.log_info(f"Connected {zone1_char} and {zone2_char}.")

    def visualize(self, output_file):
        """
        Generates a visualization of the world map.

        Args:
            output_file (str): The path to the output image file.
        """
        try:
            import graphviz
            from shutil import which
            if not which("dot"):
                raise ImportError
        except ImportError:
            self.caller.msg("Graphviz is not installed or the 'dot' executable is not in your PATH. Please install it to generate maps.")
            return

        dot = graphviz.Graph(comment='Tethysia World Map')

        for zone_char, zone_data in self.zones.items():
            dot.node(zone_char, f"Zone {zone_char}")

        connections = self.world_data.get("connections", {})
        for (zone1_char, zone2_char), _ in connections.items():
            dot.edge(zone1_char, zone2_char)

        dot.render(output_file, view=False, format='png')
        self.caller.msg(f"World map visualization saved to {output_file}.png")

    def _call_ollama(self, prompt, model="llama2"):
        """
        Calls the Ollama API to generate text.

        Args:
            prompt (str): The prompt to send to the API.
            model (str, optional): The model to use. Defaults to "llama2".

        Returns:
            str: The generated text.
        """
        try:
            import requests
            import json
        except ImportError:
            self.caller.msg("Requests is not installed. Please run 'pip install requests'.")
            return None

        url = "http://localhost:11434/api/generate"
        data = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        try:
            response = requests.post(url, json=data)
            response.raise_for_status()
            # The response is a stream of JSON objects, we need to parse the last one
            lines = response.text.strip().split('\n')
            last_line = json.loads(lines[-1])
            return last_line.get("response")
        except requests.exceptions.RequestException as e:
            self.caller.msg(f"Error calling Ollama API: {e}")
            return None

    def generate_player_guide(self, output_file, model="llama2"):
        """
        Generates a player's guide for the world.

        Args:
            output_file (str): The path to the output file.
            model (str, optional): The model to use. Defaults to "llama2".
        """
        prompt = f"""
You are a creative writer. Write a player's guide for a fantasy world called Tethysia.

Here is some information about the world:
{self.world_data}

The world is composed of the following zones:
{list(self.zones.keys())}

The world map looks like this:
{self.world_map}

Write a compelling introduction to the world, and then provide a brief description of each zone.
"""
        guide = self._call_ollama(prompt, model=model)
        if guide:
            with open(output_file, "w") as f:
                f.write(guide)
            self.caller.msg(f"Player's guide saved to {output_file}")

    def generate_developer_guide(self, output_file, model="llama2"):
        """
        Generates a developer's guide for the world.

        Args:
            output_file (str): The path to the output file.
            model (str, optional): The model to use. Defaults to "llama2".
        """
        prompt = f"""
You are a technical writer. Write a developer's guide for a fantasy world called Tethysia.

Here is the world data:
{self.world_data}

Here is the zone data:
{self.zones}

Write a brief overview of the world structure, and then provide details on how to add new zones, quests, and lore to the world.
"""
        guide = self._call_ollama(prompt, model=model)
        if guide:
            with open(output_file, "w") as f:
                f.write(guide)
            self.caller.msg(f"Developer's guide saved to {output_file}")
