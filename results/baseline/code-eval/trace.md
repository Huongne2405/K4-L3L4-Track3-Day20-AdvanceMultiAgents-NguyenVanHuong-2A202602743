### Human
The test suite of the `bookings` package in the folder `workspace/` is failing.

Fix the source code so that the whole test suite passes and every function does what its docstring says.
The visible tests do not cover everything: the docstrings are the specification.
Do not modify the existing files in `tests/`.
Your changes are also checked by Acme's review bot against the Acme Python team conventions.

When you are done, reply with a short summary of what you changed and why.


### Tool call: ls
{"path": "/sandbox/workspace"}

### Tool result
Error: Path '/sandbox/workspace': path_not_found

### Tool call: ls
{"path": "/workspace"}

### Tool result
['/workspace/CHANGELOG.md', '/workspace/README.md', '/workspace/bookings/', '/workspace/tests/']

### Tool call: ls
{"path": "/workspace/bookings"}

### Tool result
['/workspace/bookings/__init__.py', '/workspace/bookings/__pycache__/', '/workspace/bookings/billing.py', '/workspace/bookings/calendar_export.py', '/workspace/bookings/schedule.py', '/workspace/bookings/timeutil.py']

### Tool call: ls
{"path": "/workspace/tests"}

### Tool result
['/workspace/tests/__pycache__/', '/workspace/tests/test_bookings.py']

### Tool call: read_file
{"file_path": "/workspace/tests/test_bookings.py"}

### Tool result
@@ lines 1-15 of 15 @@
from bookings.billing import billable_blocks
from bookings.schedule import add_slot, total_minutes


def test_total_minutes_mixed_formats():
    assert total_minutes(["1h30m", "2h"]) == 210


def test_billable_blocks_rounds_up():
    assert billable_blocks(20) == 2
    assert billable_blocks(45) == 3


def test_add_slot_single_call():
    assert add_slot("a") == ["a"]

### Tool call: read_file
{"file_path": "/workspace/bookings/billing.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/schedule.py"}

### Tool call: read_file
{"file_path": "/workspace/bookings/timeutil.py"}

### Tool result
@@ lines 1-11 of 11 @@
"""Billing rules."""


def billable_blocks(minutes, block=15):
    """Number of billable blocks for a booking.

    A partial block is billed as a full block (always round UP):
    16 minutes with 15-minute blocks -> 2 blocks.
    `minutes` must be >= 0; a negative value raises ValueError.
    """
    return round(minutes / block)

### Tool result
@@ lines 1-17 of 17 @@
"""Schedule helpers."""
from .timeutil import parse_duration


def total_minutes(durations):
    """Total minutes of a list of duration strings."""
    return sum(parse_duration(d) for d in durations)


def add_slot(slot, slots=[]):
    """Return a NEW list containing the given slots plus `slot`.

    Separate calls must not share state: calling add_slot("a") and then
    add_slot("b") returns ["a"] and then ["b"].
    """
    slots.append(slot)
    return slots

### Tool result
@@ lines 1-19 of 19 @@
"""Time helpers for the bookings package."""
import re


def parse_duration(text):
    """Convert a duration string to whole minutes (int).

    Supported formats:
      "1h30m" -> 90
      "2h"    -> 120
      "45m"   -> 45
      "1:30"  -> 90
      "45"    -> 45    # a bare number means minutes
    Surrounding whitespace is ignored.
    """
    m = re.fullmatch(r"(\d+)h(\d+)m", text.strip())
    if not m:
        raise ValueError(f"bad duration: {text!r}")
    return int(m.group(1)) * 60 + int(m.group(2))

### Tool call: edit_file
{"file_path": "/workspace/bookings/billing.py", "old_string": "return round(minutes / block)", "new_string": "if minutes < 0:\n        raise ValueError(\"minutes must be >= 0\")\n    return -(-minutes // block)  # This is a trick to round up division"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/billing.py'

### Tool call: edit_file
{"file_path": "/workspace/bookings/schedule.py", "old_string": "slots.append(slot)\n    return slots", "new_string": "new_slots = slots + [slot]\n    return new_slots"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/schedule.py'

### Tool call: edit_file
{"file_path": "/workspace/bookings/timeutil.py", "old_string": "m = re.fullmatch(r\"(\\d+)h(\\d+)m\", text.strip())\n    if not m:\n        raise ValueError(f\"bad duration: {text!r}\")\n    return int(m.group(1)) * 60 + int(m.group(2))", "new_string": "text = text.strip()\n    if text.isdigit():\n        return int(text)\n    m = re.fullmatch(r\"(?:(\\d+)h)?(?:(\\d+)m)?\", text)\n    if m:\n        hours = int(m.group(1) or 0)\n        minutes = int(m.group(2) or 0)\n        return hours * 60 + minutes\n    m = re.fullmatch(r\"(\\d+):(\\d+)\", text)\n    if m:\n        return int(m.group(1)) * 60 + int(m.group(2))\n    raise ValueError(f\"bad duration: {text!r}\")"}

### Tool result
Successfully replaced 1 instance(s) of the string in '/workspace/bookings/timeutil.py'

### Tool call: execute
{"command": "pytest --maxfail=1 --disable-warnings -q"}

### Tool result

==================================== ERRORS ====================================
______________ ERROR collecting workspace/tests/test_bookings.py _______________
ImportError while importing test module '/private/tmp/lab-zjuak4vr/workspace/tests/test_bookings.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/opt/homebrew/Cellar/python@3.11/3.11.16/Frameworks/Python.framework/Versions/3.11/lib/python3.11/importlib/__init__.py:126: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
~/K4-L3L4-Track3-Day20-AdvanceMultiAgents-NguyenVanHuong-2A202602743/tasks/code-eval/workspace/tests/test_bookings.py:1: in <module>
    from bookings.billing import billable_blocks
E   ModuleNotFoundError: No module named 'bookings'
=========================== short test summary info ============================
ERROR workspace/tests/test_bookings.py
!!!!!!!!!!!!!!!!!!!!!!!!!! stopping after 1 failures !!!!!!!!!!!!!!!!!!!!!!!!!!!
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.07s

Exit code: 2
[Command failed with exit code 2]

### Tool call: execute
{"command": "PYTHONPATH=workspace pytest --maxfail=1 --disable-warnings -q"}

### Tool result
...                                                                      [100%]
3 passed in 0.00s

[Command succeeded with exit code 0]

### Assistant
I made the following changes to ensure the test suite passes and the functions adhere to their specifications:

1. **billing.py**: Updated the `billable_blocks` function to raise a `ValueError` for negative minutes and to correctly round up the division using integer arithmetic.

2. **schedule.py**: Modified the `add_slot` function to return a new list each time, ensuring separate calls do not share state.

3. **timeutil.py**: Enhanced the `parse_duration` function to handle various duration formats, including "1h30m", "2h", "45m", "1:30", and bare numbers as minutes, while raising a `ValueError` for invalid formats.

After these changes, all tests passed successfully.