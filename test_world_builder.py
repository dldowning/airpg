# This is a test script for the world builder.
# It is not intended to be part of the final submission.

import os
import sys

# This is a hack to get the Evennia environment set up
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from evennia.server.initial_setup import django_init
django_init()


from evennia.contrib.world_builder.commands import CmdWorldBuilder
from evennia.objects.models import ObjectDB

class MockCaller:
    def __init__(self):
        self.db = ObjectDB()
        self.db.key = "TestCaller"
        self.db.save()

    def msg(self, text):
        print(text)

def main():
    caller = MockCaller()
    cmd = CmdWorldBuilder()
    cmd.caller = caller
    cmd.args = "evennia.contrib.world_builder.world_maps.TETHYSIA_MAP evennia.contrib.world_builder.world_maps.TETHYSIA_LEGEND evennia.contrib.world_builder.world_maps.TETHYSIA_DATA"
    cmd.func()

if __name__ == "__main__":
    main()
