import os
import sys

from twisted.internet import reactor, defer

# Add the evennia root to the python path, assuming the script is run from there.
sys.path.insert(0, os.getcwd())

# Set Django settings module to use the template settings.
os.environ['DJANGO_SETTINGS_MODULE'] = 'evennia.game_template.server.conf.settings'

import django
django.setup()

import evennia
evennia._init()

from evennia.contrib.rpg.llm.llm_client import LLMClient

@defer.inlineCallbacks
def main():
    """
    Main function to run the LLM client test.
    """
    client = LLMClient()
    print("Sending prompt to Ollama...")
    try:
        response = yield client.get_response("Do you think you could write a MUD?")
        print("Response from Ollama:")
        print(response)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        reactor.stop()

if __name__ == "__main__":
    if reactor.running:
        reactor.callWhenRunning(main)
    else:
        reactor.callWhenRunning(main)
        print("Starting Twisted reactor...")
        reactor.run()
    print("Twisted reactor stopped.")
