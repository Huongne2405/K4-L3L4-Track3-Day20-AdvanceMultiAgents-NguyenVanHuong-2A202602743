---
name: write-regression-tests
description: Use when fixing bugs to ensure regression tests are added to prevent reoccurrence.
---
1. Create or open the file `tests/test_regressions.py` in the test directory.
2. For each bug fixed, write a test function that reproduces the bug and verifies the fix. Name the function descriptively, e.g., `test_<bug_description>`.
3. Ensure there are at least three test functions if multiple bugs are fixed.
4. Run the test suite to ensure all regression tests pass.

Completion Check:
- `tests/test_regressions.py` contains a test function for each bug fixed.
- The test suite runs without errors, confirming that all regression tests pass.
