# World Builder

This contrib provides tools for building a world map from a collection of zone maps.

## How it works

The world builder takes a "world map" and a "world legend" as input. The world map is an ASCII map where each character represents a zone. The world legend is a Python dictionary that maps each zone character to a zone map and a zone legend.

The world builder then uses the existing `evennia.contrib.grid.mapbuilder` to create each zone. It also provides a mechanism for connecting zones to each other.

## Features

*   **World building**: Create a large world from smaller, more manageable zones.
*   **Zone connections**: Connect zones to each other to create a seamless world.
*   **World map visualization**: Generate a visual representation of the world map.
*   **Data tracking**: Track world-level data such as quests, lore, and politics.
*   **Content generation**: Use an LLM to generate player and developer guides for the world.

## How to use

1.  Create a world map file.
2.  Create a world legend file.
3.  Use the `@worldbuilder` command to build the world.
