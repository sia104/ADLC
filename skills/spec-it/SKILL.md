---
name: spec-it
description: Convert a user request into a precise, testable specification without writing implementation code.
---

# spec-it

Use this skill to convert a user request into a precise, testable specification.

Rules:
- Do not write implementation code.
- Capture the requested behavior, constraints, acceptance criteria, and test expectations.
- Do not silently add reasonable-but-unrequested product requirements. Add only
  requirements necessary to make the user's intent precise and testable.
- Put optional improvements in a separate optional or recommendations section;
  do not make them mandatory.
- Keep requirements explicit and deterministic where possible.
- Save specifications under `specs/`.
- Mark the specification as pending human approval until the human approves it.
- Do not proceed to implementation from this skill.
