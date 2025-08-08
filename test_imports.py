print("Attempting to import llm_rules...")
try:
    from mygame.world.combat_llm import llm_rules
    print("Successfully imported llm_rules.")
except Exception as e:
    print(f"An error occurred importing llm_rules: {e}")

print("Attempting to import llm_handler...")
try:
    from mygame.world.combat_llm import llm_handler
    print("Successfully imported llm_handler.")
except Exception as e:
    print(f"An error occurred importing llm_handler: {e}")
