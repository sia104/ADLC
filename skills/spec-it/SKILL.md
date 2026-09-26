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
- Resolve choices that materially affect deterministic output or acceptance; do
  not leave alternatives when they can produce different accepted results.
- If user intent does not determine such a choice, ask the human where necessary
  or mark it unresolved and requiring approval.
- Do not let the implementer silently choose behavior that changes expected
  outputs. Give acceptance criteria an unambiguous expected outcome wherever
  practical.
- Save specifications under `specs/`.
- When an ADLC evidence run is active, contribute the request, specification,
  status, and approval references through the shared `.adlc` mechanism; do not
  write a separate large evidence report.
- Mark the specification as pending human approval until the human approves it.
- Do not proceed to implementation from this skill.
