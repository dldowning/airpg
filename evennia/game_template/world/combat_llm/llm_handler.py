"""
This module contains the LLMCombatHandler script, which manages
an instance of an LLM-driven combat encounter.
"""
from evennia import DefaultScript
from world.combat_llm.llm_rules import roll_d20, roll_dice

# Constants
TURN_TIMEOUT = 60  # seconds

class LLMCombatHandler(DefaultScript):
    """
    This script is created when a fight starts and is assigned to the room.
    It manages turn order, round progression, and communication with the
    LLM ruleset.
    """

    def at_script_creation(self):
        """
        Called once, when the script is first created.
        """
        self.key = "LLM Combat Handler"
        self.desc = "Manages an active combat encounter."
        self.interval = 5  # Tick every 5 seconds for timeout checks
        self.persistent = True # So it survives a server reboot

        # --- Combat State Attributes ---
        # List of character objects in the fight
        self.db.fighters = []
        # Turn order, sorted by initiative roll.
        self.db.turn_order = []
        self.db.current_turn_index = 0

        # Round tracking
        self.db.round_num = 0
        self.db.projected_rounds = 0

        # Per-round data
        self.db.turn_actions = {} # Maps char to their submitted action dict

        # Data for end-of-combat analysis
        self.db.sentiment_history = []
        self.db.initial_hp = {} # Store initial HP of all fighters

        # Timeout tracking
        self.db.turn_timer = TURN_TIMEOUT
        self.db.timeout_warning_given = False


    def _cleanup_character(self, char):
        """Removes combat state from a character."""
        if hasattr(char.ndb, 'combat_handler'):
            del char.ndb.combat_handler
        char.cmdset.delete("combat")

    def at_stop(self):
        """
        Called when the script is stopped (e.g., combat ends).
        """
        # Final cleanup for all fighters
        for char in self.db.fighters:
            if char:
                self._cleanup_character(char)

    def at_repeat(self):
        """
        Called every self.interval seconds. Used for turn timeout.
        """
        if not self.db.turn_order:
            return

        current_char = self.db.turn_order[self.db.current_turn_index]
        if not current_char.is_pc:
            # No timeout for NPCs
            return

        # Check if the player has already submitted their action
        if current_char.id in self.db.turn_actions:
            return

        self.db.turn_timer -= self.interval

        if self.db.turn_timer <= 0:
            self.msg_all(f"|y{current_char.key}'s turn has timed out! They hesitate.|n")
            # Force a neutral "pass" action
            self.add_action(current_char, "pass")

        elif self.db.turn_timer <= 15 and not self.db.timeout_warning_given:
            current_char.msg("|yYou have 15 seconds to enter your action.|n")
            self.db.timeout_warning_given = True


    # --- Combat Setup ---

    def add_character(self, character):
        """
        Adds a character to the fight. Should be called before start_combat.
        """
        if character not in self.db.fighters:
            self.db.fighters.append(character)
            character.ndb.combat_handler = self
            self.db.initial_hp[character.id] = character.db.hp

    def start_combat(self):
        """
        Kicks off the combat after all characters have been added.
        """
        self.msg_all("|rA fight has broken out!|n")

        # Roll initiative
        initiative_rolls = {char: roll_d20() + char.db.dexterity for char in self.db.fighters}
        # Sort by highest roll first
        self.db.turn_order = sorted(self.db.fighters, key=lambda char: initiative_rolls[char], reverse=True)

        turn_order_str = ", ".join(f"{char.key} ({initiative_rolls[char]})" for char in self.db.turn_order)
        self.msg_all(f"|yInitiative order: {turn_order_str}|n")

        # Get projected rounds (CR2)
        self.db.projected_rounds = self.db.fighters[0].rules.get_projected_rounds(self.db.fighters)

        # Start the first round
        self.start_new_round()

    # --- Turn and Round Management ---

    def start_new_round(self):
        """
        Begins a new round of combat.
        """
        self.db.round_num += 1
        self.db.current_turn_index = 0
        self.db.turn_actions = {}

        self.msg_all(self.get_combat_status())
        self.start_turn()

    def start_turn(self):
        """
        Starts the turn for the current character in the turn order.
        """
        if not self.db.turn_order:
            self.stop_combat("No one was left standing.")
            return

        current_char = self.db.turn_order[self.db.current_turn_index]

        # Reset turn timer
        self.db.turn_timer = TURN_TIMEOUT
        self.db.timeout_warning_given = False

        if current_char.is_defeated:
            self.msg_all(f"{current_char.key} is defeated and cannot act.")
            self.next_turn()
            return

        if current_char.is_pc:
            current_char.cmdset.add("world.combat_llm.llm_commands.CombatCmdSet", persistent=False)
            current_char.msg("|gIt's your turn! What do you do? (e.g., 'do ...')|n")
        else:
            # Simple NPC AI: attack a random player
            self.resolve_npc_turn(current_char)

    def next_turn(self):
        """
        Advances to the next character in the turn order. If at the end,
        starts a new round.
        """
        # Check for victory conditions
        pcs = [f for f in self.db.fighters if f.is_pc and not f.is_defeated]
        npcs = [f for f in self.db.fighters if not f.is_pc and not f.is_defeated]

        if not pcs:
            self.stop_combat("All players have been defeated!")
            return
        if not npcs:
            self.stop_combat("All enemies have been defeated!")
            return

        self.db.current_turn_index += 1
        if self.db.current_turn_index >= len(self.db.turn_order):
            # End of the round
            self.msg_all("|y--- End of Round ---|n")
            self.start_new_round()
        else:
            # Next character's turn
            self.start_turn()

    def stop_combat(self, message):
        """
        Stops the combat, cleans up, and provides a final message.
        """
        self.msg_all(f"|r{message}|n")
        self.msg_all("|rCombat has ended.|n")

        # In a full implementation, we would call the CR6 victory narrative here.

        self.stop()

    # --- Action Handling ---

    def add_action(self, character, action_text):
        """
        Receives an action from a command, validates it, and stores it.
        """
        # For now, we'll just accept the action.
        # In the full implementation, this will call the LLM for validation.

        self.db.turn_actions[character.id] = {
            "text": action_text,
            "char": character,
            "sentiment": "Average", # Placeholder
            "modifier": 0         # Placeholder
        }
        character.msg(f"You will: {action_text}")

        # Simple sequential resolution: resolve turn immediately
        self.resolve_pc_turn(character)

    def resolve_pc_turn(self, character):
        """
        Resolves a PC's turn using their submitted action.
        """
        action_data = self.db.turn_actions.get(character.id)
        if not action_data:
            self.next_turn()
            return

        # Simplified logic: Assume action is an attack on a random NPC
        target = self.get_random_target(character)
        if not target:
            self.msg_all(f"{character.key} looks around but finds no one to attack.")
            self.next_turn()
            return

        self.msg_all(f"--- {character.key}'s turn ---")

        # This is where we would call the LLM for narrative (CR3)
        # For now, simple text output.

        attack_roll = roll_d20() + character.db.strength
        defense_roll = 10 + target.db.dexterity # Simple defense

        if attack_roll >= defense_roll:
            damage = roll_dice(1, 8) + character.db.strength
            target.apply_damage(damage)
            outcome = "Hit"
        else:
            damage = 0
            outcome = "Miss"
            self.msg_all(f"{character.key} attacks {target.key} but misses!")

        # Display dice summary (CR3)
        roll_summary = f"Attack: d20({attack_roll - character.db.strength})+{character.db.strength}={attack_roll} vs {defense_roll} | Damage: 1d8+{character.db.strength}={damage}"
        self.msg_all(f"|y{roll_summary}|n")

        self.next_turn()

    def resolve_npc_turn(self, character):
        """
        Generates and resolves an NPC's turn.
        """
        target = self.get_random_target(character, target_pcs=True)
        if not target:
            self.next_turn() # No valid targets left
            return

        self.msg_all(f"--- {character.key}'s turn ---")
        self.msg_all(f"{character.key} attacks {target.key}!")

        attack_roll = roll_d20() + character.db.strength
        defense_roll = 10 + target.db.dexterity

        if attack_roll >= defense_roll:
            damage = roll_dice(1, 6) + character.db.strength
            target.apply_damage(damage)
            outcome = "Hit"
        else:
            damage = 0
            outcome = "Miss"
            self.msg_all(f"{character.key}'s attack misses!")

        roll_summary = f"Attack: d20({attack_roll - character.db.strength})+{character.db.strength}={attack_roll} vs {defense_roll} | Damage: 1d6+{character.db.strength}={damage}"
        self.msg_all(f"|y{roll_summary}|n")

        self.next_turn()


    # --- Helper Methods ---

    def msg_all(self, message):
        """Sends a message to all fighters."""
        for char in self.db.fighters:
            if char:
                char.msg(message)

    def get_random_target(self, attacker, target_pcs=False):
        """Gets a random, valid target."""
        targets = [
            f for f in self.db.fighters
            if f != attacker and not f.is_defeated and (f.is_pc if target_pcs else not f.is_pc)
        ]
        return random.choice(targets) if targets else None

    def get_combat_status(self):
        """
        Generates the single-line status bar for the top of the round (CR1).
        """
        status_lines = []
        pcs = [f for f in self.db.fighters if f.is_pc]
        npcs = [f for f in self.db.fighters if not f.is_pc]

        round_info = f"Round ({self.db.round_num}/{self.db.projected_rounds or '?'})"
        turn_order_str = f"[{' > '.join(c.key for c in self.db.turn_order)}]"

        for pc in pcs:
            pc_status = f"{pc.key}: {pc.get_display_hp()} {pc.get_display_effects()}"

            enemy_statuses = []
            for npc in npcs:
                enemy_statuses.append(f"{npc.key} {npc.get_display_hp()} {npc.get_display_effects()}")

            vs_str = "vs. " + ", ".join(enemy_statuses) if enemy_statuses else "vs. no one"

            status_lines.append(f"|g{pc_status} - {round_info} - {vs_str} {turn_order_str}|n")

        return "\n".join(status_lines)
