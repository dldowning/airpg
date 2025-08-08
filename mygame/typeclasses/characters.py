"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia.objects.objects import DefaultCharacter
from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    This has been augmented with LLM-driven combat system attributes and methods.
    """

    def at_object_creation(self):
        """
        Called only when the object is first created.
        """
        super().at_object_creation()

        # Combat-related attributes
        self.db.max_hp = 100
        self.db.hp = 100
        self.db.effects = []  # For status effects like 'Poisoned', 'Stunned'

        # Non-combat attributes for variety
        self.db.strength = 5
        self.db.dexterity = 5
        self.db.intelligence = 5

    @property
    def rules(self):
        """
        This property allows the rules to be accessed on the character,
        but initializes the rules class only once needed.
        """
        if not hasattr(self, "_rules"):
            from world.combat_llm.llm_rules import LLMCombatRules
            self._rules = LLMCombatRules()
        return self._rules

    @property
    def is_in_combat(self):
        """
        Returns True if the character is currently in combat.
        This is determined by the presence of a combat handler.
        """
        return hasattr(self.ndb, 'combat_handler') and self.ndb.combat_handler is not None

    @property
    def is_defeated(self):
        """
        Returns True if the character's HP is 0 or less.
        """
        return self.db.hp <= 0

    def get_display_hp(self):
        """
        Returns a string showing current and max HP.
        """
        return f"({self.db.hp}/{self.db.max_hp})"

    def get_display_effects(self):
        """
        Returns a comma-separated string of active effects.
        """
        if not self.db.effects:
            return ""
        return ", ".join(self.db.effects)

    def apply_damage(self, amount):
        """
        Applies damage to the character, clamping HP at 0.
        """
        self.db.hp -= amount
        if self.db.hp < 0:
            self.db.hp = 0

        self.location.msg_contents(f"{self.key} takes {amount} damage!")
        if self.is_defeated:
            self.location.msg_contents(f"|r{self.key} has been defeated!|n")
