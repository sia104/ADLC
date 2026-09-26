# ADLC Evidence

This directory contains a reusable, filesystem-based evidence bundle for ADLC
runs. It stores structured metadata and small text artifacts without requiring a
database or adding an evidence-collection agent.

## Layout

```text
.adlc/
|-- evidence.py
|-- schema/
|   |-- run-manifest.schema.json
|   |-- candidate-lesson.schema.json
|   `-- lesson-status.schema.json
`-- evidence/
    |-- runs/<run-id>/
    |   |-- manifest.json
    |   |-- raw/
    |   |   |-- inputs/ outputs/ tests/ ci/ decisions/ logs/ observations/
    |   |   `-- manifest-history/
    |   `-- derived/
    |       `-- summaries/ traceability/ failures/
    `-- lessons/<lesson-id>/
        |-- candidate.json
        `-- status/
```

Raw files are source evidence. Derived summaries, traceability, classifications,
and candidate lessons are interpretations and must reference raw evidence where
practical. They never automatically change policy, skills, CI, tests, or product
requirements.

## Start And Record A Run

Run the CLI from the repository root. A caller may provide a stable run ID, or
omit it to generate a timestamp-and-random-suffix ID.

```bash
python .adlc/evidence.py create \
  --adlc-version V0.2 \
  --base-branch master \
  --request-file /path/to/sanitized-request.txt

python .adlc/evidence.py attach RUN_ID outputs specs/example.md
python .adlc/evidence.py specification RUN_ID raw/outputs/example.md
python .adlc/evidence.py stage RUN_ID spec-it pass \
  --evidence raw/outputs/example.md
python .adlc/evidence.py decision RUN_ID specification approved
python .adlc/evidence.py verification RUN_ID test unit-suite pass
python .adlc/evidence.py gate RUN_ID ruff pass
python .adlc/evidence.py close RUN_ID
python .adlc/evidence.py validate RUN_ID
```

The manifest records run identity, project and Git context, constitution and
skill hashes, available harness/runtime information, stage outcomes,
verification, human decisions, failures, interventions, and evidence references.
Use `reference` instead of `attach` for large, binary, or externally retained CI
artifacts.

Use `derive` for summaries, traceability, and failure classifications. The
command requires one or more registered raw evidence paths and stores those
links in the manifest. Structured commands also record test/runtime results,
unverified criteria, CI runs, pull requests, merge status, and final commits.

## Raw Evidence Safety

`attach` accepts only UTF-8 text up to 1 MB, creates files exclusively, makes
them read-only, hashes them, and refuses likely secret-bearing names or content.
It never overwrites a raw artifact. Manifest updates are explicit and preserve
the complete previous revision in `raw/manifest-history/` before replacement.

Do not collect credentials, tokens, private keys, environment files, signed URLs,
or irrelevant personal data. Sanitize evidence before capture. External
references must not contain credentials, query strings, or fragments.

## Candidate Lessons

Create a proposal from registered raw evidence:

```bash
python .adlc/evidence.py lesson-create stable-lesson-id \
  --observation "Observed behaviour" \
  --support RUN_ID:raw/observations/example.txt \
  --why "Why the pattern matters" \
  --target deterministic-adlc-control
```

Candidates are immutable proposals with status `proposed`. A human decision can
be appended with `lesson-status`; it requires a registered decision-evidence
file. Status records remain append-only and never apply the lesson automatically.

## Reuse

Copy `.adlc/` and the evidence tests into another repository. The collector uses
only the Python standard library, discovers repository and skill metadata when
available, and contains no product-specific fields. Adapt the repository's test
command to run the copied tests; no application dependency is required.
