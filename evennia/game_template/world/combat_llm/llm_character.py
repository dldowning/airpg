from evennia.objects.objects import DefaultCharacter
from world.combat_llm.llm_rules import LLMCombatRules


class LLMCombatCharacter(DefaultCharacter):
    """
    A character that can fight using the LLM combat system.
    """

    @property
    def rules(self):
        """
        This property holds the combat rules engine.
        It's created on-demand and cached.
        """
        if not hasattr(self, "_rules_cache"):
            self._rules_cache = LLMCombatRules()
        return self._rules_cache

    def at_object_creation(self):
        """
        Called when the character is first created.
        """
        super().at_object_creation()
        self.db.max_hp = 100
        self.db.hp = 100
        self.db.effects = []
        self.db.in_combat = False
