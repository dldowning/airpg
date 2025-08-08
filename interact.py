import telnetlib
import time
import sys

HOST = "localhost"
PORT = 4000
TIMEOUT = 10

COMMANDS = [
    b"connect testuser testpassword",
    b"look",
    b"help",
    b"quit"
]

try:
    print(f"Connecting to {HOST}:{PORT}...")
    with telnetlib.Telnet(HOST, PORT, TIMEOUT) as tn:
        print("Connection successful.")

        # Read and print the welcome message
        time.sleep(2) # wait for welcome message
        welcome_message = tn.read_very_eager().decode('utf-8', 'ignore')
        print("--- Welcome Message ---")
        print(welcome_message)
        print("-----------------------")

        for command in COMMANDS:
            print(f"Sending command: {command.decode('utf-8')}")
            tn.write(command + b"\n")
            time.sleep(2) # wait for response
            response = tn.read_very_eager().decode('utf-8', 'ignore')
            print(f"--- Response to '{command.decode('utf-8')}' ---")
            print(response)
            print("------------------------------------")

except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)
