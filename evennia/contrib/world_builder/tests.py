# -*- coding: utf-8 -*-
"""
Tests for the world builder.
"""

import os
from unittest.mock import patch
from evennia.utils.test_resources import BaseEvenniaCommandTest
from evennia.contrib.world_builder.commands import CmdWorldBuilder
from evennia.objects.models import ObjectDB

class TestWorldBuilder(BaseEvenniaCommandTest):
    def setUp(self):
        super().setUp()
        self.account.is_superuser = True

    @patch("evennia.contrib.world_builder.world_builder.WorldBuilder._call_ollama")
    def test_world_builder(self, mock_call_ollama):
        # Mock the Ollama API call
        mock_call_ollama.return_value = "This is a test guide."

        # Run the command
        self.call(
            CmdWorldBuilder(),
            "evennia.contrib.world_builder.world_maps.TETHYSIA_MAP "
            "evennia.contrib.world_builder.world_maps.TETHYSIA_LEGEND "
            "evennia.contrib.world_builder.world_maps.TETHYSIA_DATA",
            caller=self.char1,
        )

        # Check that the rooms were created
        self.assertTrue(ObjectDB.objects.filter(db_key__startswith="Forest").exists())
        self.assertTrue(ObjectDB.objects.filter(db_key__startswith="Mountain").exists())
        self.assertTrue(ObjectDB.objects.filter(db_key__startswith="Street").exists())
        self.assertTrue(ObjectDB.objects.filter(db_key__startswith="House").exists())

        # Check that the exits were created
        forest_room = ObjectDB.objects.filter(db_key__startswith="Forest").first()
        mountain_room = ObjectDB.objects.filter(db_key__startswith="Mountain").first()
        self.assertTrue(forest_room.exits)
        self.assertTrue(mountain_room.exits)

        # Check that the output files were created
        self.assertTrue(os.path.exists("player_guide.md"))
        self.assertTrue(os.path.exists("developer_guide.md"))

    def tearDown(self):
        super().tearDown()
        if os.path.exists("player_guide.md"):
            os.remove("player_guide.md")
        if os.path.exists("developer_guide.md"):
            os.remove("developer_guide.md")
