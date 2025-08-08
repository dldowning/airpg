# Evennia Startup Troubleshooting Guide

This document outlines a series of steps to diagnose and resolve silent startup failures in an Evennia server environment.

## Symptom

You run `evennia start` and the command appears to succeed, but the server is not actually running. Subsequent commands like `evennia shell` or `evennia stop` fail with errors like "Could not connect to Evennia server" or "pidfile does not contain a valid pid". No log files are created in `mygame/server/logs/`.

This indicates a fatal error is occurring very early in the startup process, before Evennia's logging system can be initialized.

## Diagnostic Steps

1.  **Check for Missing Dependencies:** A common cause is a missing Python package that is imported by one of your custom modules.
    *   Use `pip freeze` to list all installed packages.
    *   Carefully review all `import` statements in your custom code (especially code loaded via `settings.py`) and ensure every required package is installed.
    *   In this case, the `requests` library was missing. Install it with `pip install requests`.

2.  **Check for Incorrect Imports:** Absolute imports that assume a different project structure can cause failures.
    *   **Symptom:** An `ImportError` like `No module named 'world'`.
    *   **Cause:** A module is using an absolute path like `from world.foo import bar` instead of a relative one like `from .foo import bar` when the module is inside the same package.
    *   **Solution:** Correct the import to be relative (`.`) or relative to the game directory root (e.g. `mygame.world.foo`).

3.  **Isolate the Problematic Module:** If the crash is silent, you need to find which module is causing it.
    *   Create a standalone Python script (`test_imports.py`) outside the `mygame` directory.
    *   In this script, add the `mygame` directory to the Python path (`sys.path.insert(0, ...)`).
    *   Import your custom modules one by one, with a `print` statement between each, to see which one causes the script to fail.

4.  **Check for Circular Imports with the Framework:** This is the most likely cause of a silent crash that produces a `NoneType takes no arguments` error when you try to debug it with an external script.
    *   **Symptom:** The server crashes silently. An external test script that imports your modules fails with `NoneType takes no arguments` on a line like `class MyClass(DefaultCharacter):`.
    *   **Cause:** Evennia's startup process loads your custom typeclass from `settings.py`. Your custom typeclass file then tries to `from evennia import DefaultCharacter`. The Evennia framework is not fully initialized at this point, so `DefaultCharacter` is `None`, leading to the error.
    *   **Solution:** Structure your code according to Evennia's conventions. Instead of creating a new character module in a separate directory, modify the existing `mygame/typeclasses/characters.py`. Inherit from the `Character` class in that file, which is already correctly set up to inherit from `evennia.DefaultCharacter`. Then, ensure your `settings.py` points to the standard path: `BASE_CHARACTER_TYPECLASS = "typeclasses.characters.Character"`.

5.  **Check for C-Extension Crashes:** If all of the above fail, the issue may be a low-level crash in a C extension library.
    *   **Symptom:** The Python interpreter exits with no error message, even when using manual file I/O for logging.
    *   **Diagnosis:** This is very difficult to debug. The most likely cause is a dependency conflict or a library that is not compatible with the underlying operating system or Python version.
    *   **Solution:** Systematically remove dependencies from your code (like `requests` in this case) to see if the server starts. If it does, the problem is with that dependency or one of its sub-dependencies. At this point, it may be necessary to try a different environment or version of the problematic library.

In the case of this specific task, even after following all these steps, the server continued to crash silently, pointing to a fundamental environment incompatibility that could not be resolved.
