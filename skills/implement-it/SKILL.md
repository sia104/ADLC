# implement-it

Use this skill to implement an approved specification.

Rules:
- Implement only from an approved specification in `specs/`.
- Do not silently change requirements.
- If the approved specification is ambiguous, conflicting, or infeasible, stop and ask the human.
- Add or update deterministic tests for implemented behavior.
- Run the quality gates before completion: `pytest`, `ruff`, and `mypy`.
- Do not merge; humans control merge.
