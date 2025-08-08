"""
This module contains the commands for the LLM combat system.
"""

from evennia import Command, CmdSet, default_cmds
from evennia.conf import settings
from world.combat_llm.llm_handler import LLMCombatHandler

class CmdFight(Command):
    """
    Initiates combat with all valid targets in the room.

    Usage:
      fight
    """
    key = "fight"
    help_category = "Combat"

    def func(self):
        """Handle the command."""
        if not settings.USE_LLM_COMBAT:
            self.caller.msg("The LLM combat system is currently disabled.")
            return

        caller = self.caller
        location = caller.location

        if not location:
            caller.msg("You can't fight in nothingness.")
            return

        if caller.is_in_combat:
            caller.msg("You are already in a fight!")
            return

        # Find all potential fighters in the room
        fighters = [
            obj for obj in location.contents
            if hasattr(obj, 'is_character') and obj.is_character and not obj.is_defeated
        ]

        if len(fighters) < 2:
            caller.msg("There's no one else here to fight.")
            return

        # Check if a combat handler already exists
        if location.scripts.get("LLM Combat Handler"):
            caller.msg("A fight is already in progress here!")
            # Optionally, add logic to join the fight here.
            return

        # Create a new combat handler
        handler = location.scripts.add(LLMCombatHandler)
        if not handler:
            caller.msg("|rA mysterious force prevents a fight from starting.|n")
            return

        caller.msg("|rYou roar and start a fight!|n")
        location.msg_contents(f"|r{caller.key} starts a fight!|n", exclude=[caller])

        # Add all fighters to the handler
        for fighter in fighters:
            handler.add_character(fighter)

        # Kick off the combat
        handler.start_combat()

class CmdDo(Command):
    """
    Performs an action in combat.

    Usage:
      do <description of your action>
      do I swing my sword at the orc's head!
    """
    key = "do"
    aliases = ["action"]
    help_category = "Combat"

    def func(self):
        """Handle the command."""
        caller = self.caller
        args = self.args.strip()

        if not caller.is_in_combat:
            caller.msg("You can only do that in combat.")
            return

        handler = caller.ndb.combat_handler
        if not handler:
            caller.msg("|rYou are in a fight, but something is wrong. Contact an admin.|n")
            return

        if handler.db.turn_order[handler.db.current_turn_index] != caller:
            caller.msg("It's not your turn yet.")
            return

        if caller.id in handler.db.turn_actions:
            caller.msg("You have already decided on your action for this turn.")
            return

        if not args:
            caller.msg("What do you want to do?")
            return

        # Pass the action to the handler
        handler.add_action(caller, args)


class CombatCmdSet(CmdSet):
    """
    This command set is active during combat. It replaces the default
    command set and provides access to combat-specific commands.
    """
    key = "combat"
    priority = 100
    mergetype = "Replace"
    no_exits = True # Players can't walk away from a fight

    def at_cmdset_creation(self):
        """Called when the cmdset is first created."""
        self.add(CmdDo())
        # Also add some useful default commands
        self.add(default_cmds.CmdLook())
        self.add(default_cmds.CmdSay())
        self.add(default_cmds.CmdPose())
        self.add(default_cmds.CmdHelp())
        self.add(default_cmds.CmdGet())
        self.add(default_cmds.CmdDrop())
