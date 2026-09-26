# ADLC

Canonical reusable ADLC repository.

This repository contains the reusable ADLC V0.4 governance, evidence, lifecycle,
Codex skills, CI, and deterministic tests. It is not an application project and
does not contain product requirements, product tests, or run-specific evidence.

## Contents

- `.adlc/`: reusable ADLC tooling, schemas, tests, version, and configuration.
- `.codex/skills/`: reusable Codex skills for specification, implementation,
  independent testing, and retrospective work.
- `.github/`: reusable CI workflow for deterministic quality gates.
- `specs/adlc-v0.4.md`: approved reusable V0.4 specification.
- `AGENTS.md`: concise reusable governance rules.

`.adlc/VERSION` is the canonical version authority and is set to `V0.4`.

## Bootstrap

Prerequisites:

- Python 3.12 or newer
- [uv](https://docs.astral.sh/uv/)
- Git

Install the locked development environment:

```bash
uv sync --frozen --extra dev
```

Run the reusable deterministic gates:

```bash
uv run --frozen pytest
uv run --frozen ruff check .
uv run --frozen mypy .adlc/evidence.py .adlc/lifecycle.py .adlc/preflight.py .adlc/adlc_config.py .adlc/gitops.py
```

Run ADLC preflight from a consuming repository root:

```bash
python .adlc/preflight.py --base-branch master
```

Create a new ADLC run from a sanitized request file:

```bash
python .adlc/evidence.py create --request-file /path/to/request.txt
```

## Portability

To install the reusable ADLC in an application repository, copy `.adlc/` without
local `.adlc/evidence/`, copy `.codex/skills/`, copy `.github/`, and include the
reusable governance rules from `AGENTS.md`. Keep product requirements and tests
in the consuming repository, separate from reusable ADLC governance.

Human review and merge remain procedural gates. Do not merge ADLC changes
automatically.
