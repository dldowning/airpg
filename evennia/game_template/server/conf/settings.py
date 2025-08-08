r"""
Evennia settings file.

The available options are found in the default settings file found
here:

https://www.evennia.com/docs/latest/Setup/Settings-Default.html

Remember:

Don't copy more from the default file than you actually intend to
change; this will make sure that you don't overload upstream updates
unnecessarily.

When changing a setting requiring a file system path (like
path/to/actual/file.py), use GAME_DIR and EVENNIA_DIR to reference
your game folder and the Evennia library folders respectively. Python
paths (path.to.module) should be given relative to the game's root
folder (typeclasses.foo) whereas paths within the Evennia library
needs to be given explicitly (evennia.foo).

If you want to share your game dir, including its settings, you can
put secret game- or server-specific settings in secret_settings.py.

"""

# Use the defaults from Evennia unless explicitly overridden
from evennia.settings_default import *

######################################################################
# Evennia base server config
######################################################################

# This is the name of your game. Make it catchy!
SERVERNAME = "MyEvenniaGame"


######################################################################
# LLM (Large Language Model) support
######################################################################
# The LLM client is used to communicate with an LLM server.
# This can be used for generating texts for AI npcs, etc.
#
# See evennia/contrib/rpg/llm/README.md for more info.
#
# Available API types are 'text-generation-webui' and 'ollama'.
LLM_API_TYPE = "ollama"
# The host and port of the LLM server.
LLM_HOST = "http://127.0.0.1:11434"
# The path to the API endpoint on the LLM server.
LLM_PATH = "/api/chat"
# The body of the request sent to the LLM server. This is API-specific.
# For ollama, this should contain the model name and other parameters.
LLM_REQUEST_BODY = {
    "model": "llama3",
    "stream": False,
}


######################################################################
# Settings given in secret_settings.py override those in this file.
######################################################################
try:
    from server.conf.secret_settings import *
except ImportError:
    print("secret_settings.py file not found or failed to import.")
