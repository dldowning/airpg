# Evennia Launch and Troubleshooting Report

This report details the steps to launch a test Evennia world and provides solutions to common troubleshooting issues encountered during the process.

## 1. Installation

Evennia can be installed using `pip`. It is recommended to do this in a virtual environment.

```bash
pip install evennia
```

If you are working from a source checkout of the Evennia repository, you can install it in editable mode:

```bash
pip install -e .
```

## 2. Game Creation

Once Evennia is installed, you can create a new game directory. This directory will contain all the files for your game.

```bash
evennia --init <your_game_name>
```

Replace `<your_game_name>` with the desired name for your game directory. For example:

```bash
evennia --init mygame
```

## 3. Database Setup

After creating the game directory, you need to initialize the database. Change into your game directory and run the `migrate` command:

```bash
cd <your_game_name>
evennia migrate
```

This will create a new SQLite database file in your game's `server/` directory.

## 4. Server Launch

To start the Evennia server, run the `evennia start` command from within your game directory. The first time you start the server, you will be prompted to create a superuser account.

```bash
cd <your_game_name>
evennia start
```

### Non-Interactive Server Start

In a scripted or non-interactive environment, you can create the superuser by setting environment variables:

```bash
cd <your_game_name>
EVENNIA_SUPERUSER_USERNAME=<username> EVENNIA_SUPERUSER_PASSWORD=<password> evennia start
```

## 5. Troubleshooting

Several issues were encountered during the launch process. Here are the solutions:

### a. Server Fails to Start or Respond

**Problem:** The server process starts but does not respond to connections, or it fails with an error like `No module named 'server.conf.settings'`.

**Solution:** This can happen if the server is started from the wrong directory or if a previous server process is still running in a bad state.

1.  **Kill any existing Evennia server processes.** You can use `pkill` to find and kill the `twistd` process used by Evennia:
    ```bash
    pkill -f twistd
    ```
2.  **Start the server in the foreground.** This will allow you to see the server logs directly and diagnose any startup errors. Make sure you are in your game directory when you run this command.
    ```bash
    cd <your_game_name>
    evennia start
    ```

### b. Interacting with the Game in a Non-Interactive Environment

**Problem:** Standard methods of scripting `telnet` interaction, such as piping commands, may not work. The Evennia server expects a more interactive client.

**Solution:** Use a Python script with the `telnetlib` library to simulate an interactive session. This gives you more control over the connection and allows you to read the server's output.

Here is an example script that connects to the server, logs in, and runs some basic commands:

```python
# /app/interact.py
import telnetlib
import time
import sys

HOST = "localhost"
PORT = 4000
TIMEOUT = 10

COMMANDS = [
    b"connect <username> <password>",
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
            # Replace placeholders in the connect command
            if b"<username>" in command and b"<password>" in command:
                command = command.replace(b"<username>", b"testuser").replace(b"<password>", b"testpassword")

            print(f"Sending command: {command.decode('utf-8')}")
            tn.write(command + b"\n")
            time.sleep(2) # wait for response
            response = tn.read_very_eager().decode('utf-8', 'ignore')
            print(f"--- Response to '{command.decode('utf-8')}' ---")
            print(response)
            print("------------------------------------")

except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)

```

To run this script:

```bash
python3 /app/interact.py
```

This script will connect to the Evennia server, log in with the specified credentials, and execute the commands in the `COMMANDS` list. The output of each command will be printed to the console.
