# ADLC V0.3

This directory is the canonical source for the reusable ADLC in this
repository. `VERSION` is the version authority. The Python tools use only the
standard library and keep product requirements separate from workflow
governance.

## Preflight

Run preflight before starting work:

```bash
python .adlc/preflight.py --base-branch master
```

It reports repository identity, remote and branch context, working-tree state,
ADLC version, required skills, CI and evidence components, tool versions, and
quality-gate concerns. It never rewrites configuration. A reduction in the
repository's recorded quality-gate baseline is flagged as requiring explicit
human approval.

## Lifecycle

V0.3 records one deterministic lifecycle in every new manifest:

```text
specification -> human-specification-approval -> feature-branch
  -> implementation -> independent-testing
  -> remediation -> implementation                 (test gap loop)
  -> pull-request -> ci -> human-review -> merge
  -> run-closure -> retrospective
```

The controller rejects transitions outside these paths. Specification approval,
remediation approval, CI success, human review, merge context, and the feature
branch are checked at their applicable boundaries. Feature-branch, CI-before-
merge, and human-merge controls are recorded as procedural unless a repository
adds technical platform enforcement.

Start a run from the repository root. The version is read from `.adlc/VERSION`;
it is not caller-selected. Creation automatically captures preflight evidence.

```bash
python .adlc/evidence.py create \
  --base-branch master \
  --request-file /path/to/sanitized-request.txt

python .adlc/evidence.py lifecycle RUN_ID
python .adlc/evidence.py attach RUN_ID outputs specs/example.md
python .adlc/evidence.py transition RUN_ID human-specification-approval pass \
  --evidence raw/outputs/example.md
python .adlc/evidence.py specification RUN_ID raw/outputs/example.md
python .adlc/evidence.py decision RUN_ID specification approved
python .adlc/evidence.py transition RUN_ID feature-branch pass
```

Create and check out the feature branch before transitioning to
`implementation`. Use `transition` to batch a completed stage's outcome,
evidence, and lifecycle advance into one manifest update.

After independent testing, a passing outcome enters `pull-request`. A failed or
incomplete outcome may enter `remediation`; a recorded human `implementation`
decision is then required before returning to implementation. There is no
repair skill.

Record PR, CI, review, and merge context before their guarded transitions:

```bash
python .adlc/evidence.py merge-context RUN_ID not_merged \
  --pull-request-number 12 --pull-request-url https://github.com/o/r/pull/12
python .adlc/evidence.py ci RUN_ID pass --workflow-run 12345
python .adlc/evidence.py decision RUN_ID merge approved
python .adlc/evidence.py merge-context RUN_ID merged --final-commit COMMIT
python .adlc/evidence.py close RUN_ID
python .adlc/evidence.py validate RUN_ID
```

The feature branch must be pushed before the pull-request stage advances to CI.
Humans remain responsible for review and merge.

## Evidence

Each V0.3 run contains a current `manifest.json`, immutable raw and derived
artifacts, and a hash-chained append-only `events/` journal. Updates are guarded
by a process lock and written atomically. The journal records compact changed-
field hashes instead of copying the complete manifest on every update. Existing
V0.2 runs retain their `raw/manifest-history/` snapshots and remain valid.

`attach` stores UTF-8 text up to 1 MB, rejects likely secrets, writes
exclusively, and deduplicates matching category/content evidence. Use `reference`
for external or binary evidence. Use `identify` for a clean, committed repository
file; it records path, commit, and content hash without copying the file.

```bash
python .adlc/evidence.py identify RUN_ID outputs specs/example.md
python .adlc/evidence.py derive RUN_ID traceability report.txt \
  --support raw/tests/test-output.txt
```

Derived evidence must cite registered raw evidence. Never collect credentials,
tokens, private keys, environment files, signed URLs, or irrelevant personal
data.

## Retrospective

`retrospect-it` operates only on closed runs. It may observe evidence and create
candidate lessons, but it cannot change policy, skills, CI, tests, schemas, ADLC
code, or product code. Candidates remain proposals until a separate human
decision is appended.

```bash
python .adlc/evidence.py lesson-create stable-lesson-id \
  --observation "Observed behaviour" \
  --support RUN_ID:raw/observations/example.txt \
  --why "Why the pattern matters" \
  --target deterministic-adlc-control
```

## Portability

Copy `.adlc/`, the four `.codex/skills/` directories, the concise constitution
rules in `AGENTS.md`, and the ADLC tests into another repository. Replace the
repository-specific entries in `quality-gates.json` with that repository's
existing deterministic gates. These entries are a local baseline, not universal
ADLC product requirements.
