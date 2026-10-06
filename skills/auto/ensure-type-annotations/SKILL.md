---
name: ensure-type-annotations
description: Use when writing or reviewing public functions to ensure they have type annotations for all parameters and return values.
---
1. Identify all public functions in the codebase. A public function is one whose name does not start with an underscore ('_').
2. For each public function, ensure that every parameter has a type annotation. If a parameter can accept multiple types, use a union type.
3. Ensure the return value of each public function is annotated with its type. If the function does not return a value, use `None` as the return type.
4. Verify that the code passes static type checks using a tool like `mypy`.

Completion Check:
- All public functions have type annotations for parameters and return values.
- Static type checks pass without errors.
