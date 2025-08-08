"""
This module contains the core game logic for the LLM-based combat system.
"""

import json
import random

SENTIMENT_MODIFIERS = {
    'Very-Poor': -4,
    'Poor': -2,
    'Average': 0,
    'Good': +2,
    'Very-Good': +4
}

# --- Rules Class ---

class LLMCombatRules:
    """
    This class implements the combat logic by making calls to an LLM.
    """

    def _call_ollama(self, prompt_text):
        """
        (STUBBED FOR DEBUGGING)
        Private helper to send a prompt to the Ollama server and get a response.
        """
        print(f"|y[LLMCombatRules] STUB: Received prompt:\n{prompt_text}|n")
        # Return a safe, default response
        if "validate_action" in prompt_text:
            return {
                "classification": "Acceptable",
                "sentiment": "Average",
                "feedback": "Your action is noted (stub response)."
            }
        elif "resolve_turn_narrative" in prompt_text:
            return {"narrative": "A stubbed narrative of the turn's events unfolds."}
        elif "resolve_victory_narrative" in prompt_text:
            return {"summary": "The battle ends. This is a stubbed summary."}
        return {}

    def get_projected_rounds(self, fighters):
        """
        CR2: Secretly decide on the optimal number of rounds for the encounter.

        Args:
            fighters (list): A list of all characters in the combat.

        Returns:
            int: The projected number of rounds for the combat (3-12).
        """
        # Simple logic: more fighters = longer projected combat.
        # This could be expanded to consider character levels, boss status, etc.
        num_fighters = len(fighters)
        if num_fighters <= 2:
            return random.randint(3, 5)  # Simple duel
        elif num_fighters <= 4:
            return random.randint(5, 8)  # Standard group fight
        else:
            return random.randint(8, 12) # Large, complex battle

    def get_action_plot_percentage(self, handler):
        """
        CR2: Estimate the percentage of the combat action/plot that has unfolded.

        This is a simplified, Python-based estimation using HP totals.

        Args:
            handler (LLMCombatHandler): The combat handler script.

        Returns:
            int: An estimated percentage (0-100) of combat completion.
        """
        initial_hp = handler.db.initial_hp_total
        current_hp = sum(char.db.hp for char in handler.db.fighters if not char.is_pc)

        if initial_hp == 0:
            return 100  # Avoid division by zero; if there were no enemies, combat is over.

        damage_done = initial_hp - current_hp
        percentage = int((damage_done / initial_hp) * 100)
        return max(0, min(100, percentage)) # Clamp between 0 and 100

    def validate_action(self, character, action_text, combat_context):
        """
        CR4 & CR5: Validate player input for logic and sentiment.

        Args:
            character (Character): The character performing the action.
            action_text (str): The player's descriptive input.
            combat_context (str): A brief description of the current combat situation.

        Returns:
            dict: A dictionary containing the validation result, like:
                  {'classification': 'Acceptable', 'sentiment': 'Good',
                   'modifier': 2, 'feedback': 'A solid plan.'}
        """
        prompt = f"""
You are a game master's assistant responsible for validating a player's action in a text-based RPG.
Analyze the player's input based on the provided context.

**Combat Context:**
{combat_context}

**Player's Character:** {character.key}
**Player's Action:** "{action_text}"

**Your Tasks:**
1.  **Logic Check (CR4):** Classify the action as 'Acceptable', 'Unacceptable', or 'Vague'.
    - 'Acceptable': The action is logical, within the character's likely capabilities, and fits the game's reality.
    - 'Unacceptable': The action contradicts established facts, is nonsensical (e.g., "I fire my crossbow" when they have a sword), or breaks the game's tone.
    - 'Vague': The action is too generic to be resolved (e.g., "kill the guy").
2.  **Sentiment Analysis (CR5):** If the action is 'Acceptable', classify its sentiment into one of five categories: 'Very-Poor', 'Poor', 'Average', 'Good', or 'Very-Good'.
    - Base this on descriptiveness and tactical soundness. 'Very-Good' actions are creative, detailed, and smart. 'Very-Poor' actions are boring, nonsensical, or strategically awful (e.g., "I try to punch the fire elemental").
    - If the action is 'Unacceptable' or 'Vague', sentiment is 'Average' by default.

**Output Format:**
Respond with a single JSON object with the following keys:
- "classification": (string) "Acceptable", "Unacceptable", or "Vague".
- "sentiment": (string) "Very-Poor", "Poor", "Average", "Good", or "Very-Good".
- "feedback": (string) A brief, helpful message for the player, especially if the action is Unacceptable or Vague (e.g., "You don't have a crossbow. You could use your sword or try to negotiate."). For acceptable actions, this can be an empty string.

**Example:**
If the player says "I fire my laser rifle", but the context is a fantasy world, you would respond:
{{
    "classification": "Unacceptable",
    "sentiment": "Average",
    "feedback": "Your character doesn't know what a laser rifle is. You see a sword at your hip and a bow on your back."
}}

Now, analyze the player's action and provide your response.
"""
        response_json = self._call_ollama(prompt)

        if not response_json:
            # Default to a safe, neutral response if LLM fails
            return {
                "classification": "Acceptable",
                "sentiment": "Average",
                "modifier": 0,
                "feedback": "Your action is noted."
            }

        # Add the numerical modifier to the response
        sentiment = response_json.get("sentiment", "Average")
        response_json["modifier"] = SENTIMENT_MODIFIERS.get(sentiment, 0)

        return response_json

    def resolve_turn_narrative(self, turn_data):
        """
        CR3: Generate the narrative description for a turn's events.

        Args:
            turn_data (dict): A dictionary containing all info about the turn, e.g.:
                'character_name', 'action_text', 'target_name', 'outcome',
                'damage', 'roll_summary', 'pacing_status', 'sentiment'

        Returns:
            str: The generated narrative text.
        """
        prompt = f"""
You are a master storyteller and game master for a text-based RPG. Your task is to describe the outcome of a character's action in a combat round.

**Instructions:**
- Write 2-5 descriptive sentences.
- Write 0-2 lines of dialogue.
- The tone of the description should match the 'Action Sentiment'. A 'Very-Good' action should be described epically, while a 'Poor' action might be described as fumbling or ineffective.
- The 'Pacing Status' tells you if the fight is dragging or going quickly. Adjust the impact of the description accordingly. If the pace is 'slow', make the action feel more significant. If 'fast', it can be a quicker description.

**Turn Information:**
- **Actor:** {turn_data['character_name']}
- **Target:** {turn_data['target_name']}
- **Action Taken:** "{turn_data['action_text']}"
- **Action Sentiment:** {turn_data['sentiment']}
- **Dice Roll Summary:** {turn_data['roll_summary']}
- **Outcome:** {turn_data['outcome']} (e.g., "Hit", "Miss", "Parried")
- **Damage Dealt:** {turn_data['damage']}
- **Combat Pacing Status:** {turn_data['pacing_status']}

**Output Format:**
Respond with a single JSON object with one key, "narrative".

**Example:**
{{
    "narrative": "Grak swings his mighty axe at the goblin! The creature tries to dodge, but the blow connects with a sickening crunch, sending it sprawling to the dusty floor. 'That's for my brother!' Grak bellows."
}}

Now, generate the narrative for the provided turn information.
"""
        response_json = self._call_ollama(prompt)

        if not response_json or "narrative" not in response_json:
            # Fallback narrative
            return f"{turn_data['character_name']} attacks {turn_data['target_name']}! The attack {turn_data['outcome'].lower()}s."

        return response_json["narrative"]

    def resolve_victory_narrative(self, victory_data):
        """
        CR6: Generate the final summary description at the end of combat.

        Args:
            victory_data (dict): A dictionary summarizing the combat, e.g.:
                'outcome', 'winner', 'survivors', 'total_rounds', 'player_hp_status',
                'overall_performance'

        Returns:
            str: The final summary text (less than 5 sentences).
        """
        prompt = f"""
You are a game master concluding a combat encounter in a text-based RPG. Your task is to write a brief, qualitative summary of the combat's result.

**Instructions:**
- Write a single paragraph of less than five sentences.
- The tone should reflect the 'Overall Performance'. If performance was 'Excellent', the victory should feel heroic. If 'Poor', the outcome should feel costly or like a narrow escape, even in victory.
- Describe the immediate consequences and set the scene for what comes next.

**Combat Summary:**
- **Outcome:** {victory_data['outcome']} (e.g., "Player Victory", "Player Defeat", "Mutual Retreat")
- **Winner(s):** {victory_data['winner']}
- **Total Rounds:** {victory_data['total_rounds']}
- **Player Health Status:** {victory_data['player_hp_status']} (e.g., "Mostly healthy", "Badly wounded", "Near death")
- **Player's Overall Performance:** {victory_data['overall_performance']} (based on sentiment scores)

**Output Format:**
Respond with a single JSON object with one key, "summary".

**Example:**
{{
    "summary": "With a final, desperate lunge, you fell the last of the goblins. Panting, you look around at the carnage, your arm screaming in pain from a deep gash. The way forward is clear, but the victory feels hollow and hard-won."
}}

Now, generate the combat summary.
"""
        response_json = self._call_ollama(prompt)

        if not response_json or "summary" not in response_json:
            # Fallback summary
            return f"The combat is over. The winner is {victory_data['winner']}."

        return response_json["summary"]

# --- Dice Rolling ---

def roll_d20():
    "Rolls a 20-sided die."
    return random.randint(1, 20)

def roll_dice(num_dice, sides):
    "Rolls a given number of dice with a given number of sides."
    return sum(random.randint(1, sides) for _ in range(num_dice))
