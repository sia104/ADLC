# ADLC V0.6 Hardening Specification

Status: Approved

Evidence run: `20261010T163019041655Z-77f5bdc9`

## Request

Upgrade the canonical reusable ADLC from V0.5 to V0.6 as a workflow-hardening release based on the MedianView4 V0.5 run. Preserve working V0.5 behavior unless a listed V0.6 requirement explicitly requires a change.

## Scope

This specification covers reusable ADLC infrastructure and skills, including lifecycle, evidence capture, preflight, Git/GitHub automation, quality-gate handling, bootstrap/distribution metadata, tests, CI workflow definitions, and the repo-local Codex skills.

The V0.6 release version is `v0.6.0`; the canonical ADLC runtime version is `V0.6`.

## Inspection Summary

The current V0.5 implementation includes:

1. Manual quality-gate recording through `evidence.py gate RUN NAME STATUS`, which permits a caller to declare pass/fail without executing the command.
2. Optional original-request capture during run creation; `context.original_request` may be `null`.
3. Preflight quality-gate checks based on raw command substring matching against workflow YAML text.
4. Local-evidence protection in `.gitignore` and one test, but no lifecycle/publication invariant that blocks tracked `.adlc/evidence/` files.
5. `test-it` guidance that maps acceptance criteria to verification, but not every mandatory requirement, and does not require a persisted derived traceability artifact.
6. Retrospective support after run closure, but no automatic workflow prompt or deterministic transition into retrospective.
7. PR title generation in `gitops.py` from the latest commit subject.
8. Bootstrap distribution versioned at `0.5.0`/`V0.5`, with installation but no upgrade implementation.

## Requirements

### R1. Versioning

1. The canonical ADLC version must be `V0.6`.
2. The bootstrap package release version must be `0.6.0`.
3. Documentation, install metadata generation, tests, current-version checks, and compatibility constants must use `V0.6` consistently for new runs.
4. Historical V0.3 through V0.5 run manifests may remain valid where compatibility is explicitly required.

### R2. Authoritative Deterministic Quality Gates

1. Required deterministic gates must be read from `.adlc/quality-gates.json`.
2. The ADLC evidence subsystem must execute required deterministic gate commands itself.
3. For each executed gate, the evidence record must capture:
   - exact command;
   - start timestamp;
   - end timestamp;
   - exit code;
   - status derived directly from the exit code;
   - stdout and stderr, or immutable evidence artifacts/hashes when output is large;
   - Git commit;
   - current branch;
   - working-tree status context.
4. Each deterministic quality-gate result must be bound to the exact tested repository state by recording `HEAD` plus a deterministic working-tree fingerprint.
5. If either `HEAD` or the working-tree fingerprint changes after gate execution, the gate result is stale and must be rerun before it can authorize lifecycle progression.
6. A required deterministic gate must not be recordable as `pass` unless its recorded command exited with code `0` in the recorded repository state.
7. The existing manual gate-recording path must not allow callers to claim a required deterministic gate passed without execution evidence.
8. Manually recorded gate-like results may remain for external or human-controlled processes only if they are explicitly distinguished from deterministic executed gates.
9. Lifecycle progression that depends on deterministic gates must reject required gates that are missing, stale for the current repository state, failed, or manually declared.
10. Required deterministic quality gates should normally execute using argument-vector execution rather than unrestricted implicit shell execution.
11. Shell interpretation may be used only where explicitly required by the gate definition.
12. The evidence record must state the execution mode used for each deterministic gate.

### R3. Evidence Run Before Specification

1. A normal development run must start with an active evidence run before `spec-it` creates or saves a project specification.
2. New normal development runs must include a non-empty initiating request artifact.
3. `context.original_request` must not be `null` for new V0.6 normal development runs.
4. `spec-it` must instruct Codex not to create or save a specification unless an active ADLC run exists and contains the initiating request.
5. A saved specification must reference the active evidence run.
6. Compatibility for historical V0.5 and older evidence must not weaken V0.6 behavior for new runs.

### R4. Robust Quality-Gate/Preflight Comparison

1. Preflight must compare configured required gate commands against workflow definitions in a way that tolerates semantically irrelevant whitespace and YAML folded multiline `run` blocks.
2. The comparison must correctly recognize the current folded ADLC mypy command as unchanged.
3. The comparison must still report genuinely removed or weakened required commands.
4. The solution should remain small and deterministic; a large YAML-analysis framework is out of scope unless required.

### R5. Local Evidence Invariant

1. For projects using local filesystem evidence, `.adlc/evidence/` must be ignored by Git.
2. No file under `.adlc/evidence/` may be tracked by Git.
3. Violations must block at least:
   - implementation completion;
   - feature publication/push;
   - pull-request creation.
4. A violation must be recorded as a failure or publication blocker rather than allowing lifecycle progression.

### R6. Requirement-to-Verification Traceability

1. `test-it` must require a persisted derived traceability artifact for every mandatory requirement in the approved specification.
2. The traceability mapping must include, for each mandatory requirement:
   - requirement;
   - related acceptance criterion or direct verification;
   - verification evidence;
   - status.
3. Status values must distinguish at least `verified`, `failed`, and `unverified`.
4. Passing written acceptance criteria must not be treated as sufficient when a mandatory requirement lacks verification.
5. `test-it` remains OBSERVE / REPORT ONLY and must not repair production code.
6. Skill changes must be made using `$skill-creator` guidance.

### R7. Retrospective After Successful Closure

1. After a valid run closes successfully, the workflow must proceed to retrospective handling rather than leaving it purely manual.
2. Successful run closure must make retrospective the explicit required next workflow state/action.
3. The Codex workflow must invoke `retrospect-it`; if it does not complete, retrospective must remain visibly pending.
4. Retrospective handling must analyse the completed evidence bundle and create evidence-backed candidate lessons where justified.
5. It must be valid to record no candidate lesson when there is no meaningful reusable lesson.
6. `retrospect-it` remains OBSERVE / PROPOSE ONLY.
7. Candidate lessons remain proposal-only and require human promotion.
8. Retrospective handling must never automatically modify or promote changes to `AGENTS.md`, skills, CI, ADLC tooling, tests, schemas, or product code.

### R8. Pull-Request Title Generation

1. Pull-request title generation must prefer stable run intent over latest commit subject.
2. Title selection order must be:
   - approved specification title or project objective;
   - concise initiating request summary;
   - feature branch purpose;
   - latest commit subject as fallback only.
3. Pull-request body generation must remain concise and evidence-based.

### R9. Subsequent Run Base Preparation

1. Before starting a new development run in an existing project, ADLC must fetch the configured remote.
2. ADLC must determine whether the configured base branch is behind its remote.
3. ADLC must safely perform or require a fast-forward-only base update.
4. ADLC must not silently overwrite local changes.
5. ADLC must not use destructive reset as the normal path.
6. If the working tree or base branch cannot be safely prepared, ADLC must stop with a clear blocker.
7. First-run Git bootstrap behavior must remain undisturbed.

### R10. Product CI Reproducibility Where ADLC Controls It

1. Where ADLC creates or recommends product CI, it must prefer explicit supported runner versions instead of `ubuntu-latest`.
2. It must prefer explicit supported tool/action versions where practical.
3. It must not silently weaken existing product CI.
4. It must not impose Python-specific product CI on non-Python projects.
5. Reusable ADLC CI must remain separate from product CI.

### R11. Bootstrap and Distribution

1. Bootstrap package metadata must be updated for release `v0.6.0`.
2. Bootstrap managed-file manifests and installation tests must reflect `V0.6`.
3. Distribution behavior must continue excluding local evidence, virtual environments, caches, and `__pycache__`.
4. Existing V0.5 bootstrap installation behavior must be preserved unless a V0.6 requirement explicitly changes it.

## Acceptance Criteria

1. Creating a normal V0.6 run without a request artifact fails.
2. Creating a normal V0.6 run with a non-empty request artifact records that artifact and the original request remains recoverable from the evidence bundle after closure.
3. `spec-it` cannot validly create/save a specification before an active run with an initiating request exists.
4. Executing a required deterministic gate through ADLC records command, timestamps, exit code, stdout/stderr or immutable output evidence, Git commit, branch, and working-tree context.
5. Executing a required deterministic gate records `HEAD`, a deterministic working-tree fingerprint, and execution mode.
6. A deliberately failing required deterministic gate is recorded as `fail`, and lifecycle progression cannot treat it as passed.
7. The manual gate CLI cannot record a required deterministic gate as passed without execution evidence.
8. A stale deterministic gate result cannot authorize implementation completion or publication after `HEAD` or the working-tree fingerprint changes.
9. Preflight accepts the folded multiline mypy command currently used by `.github/workflows/adlc.yml`.
10. Preflight still flags a genuinely removed required command as a quality-gate weakening requiring human approval.
11. If `.adlc/evidence/` is not ignored or any evidence file is tracked, implementation completion and publication are blocked.
12. `test-it` produces a derived traceability artifact mapping every mandatory requirement to verification evidence and status.
13. A mandatory requirement with no verification is recorded as `unverified` even when all acceptance criteria pass.
14. Closing a valid run proceeds to a visibly pending retrospective state/action, and completed retrospective handling records whether candidate lessons were proposed.
15. PR title generation selects specification title/objective before latest commit subject.
16. A subsequent run from an existing repository performs or requires a fetch and fast-forward-only base update without destructive reset.
17. Version checks, docs, tests, install metadata, and bootstrap package metadata consistently report `V0.6` and `v0.6.0`.

## Required Tests

1. Unit or integration tests for deterministic gate execution pass/fail recording.
2. Regression test proving a failing ADLC gate cannot be recorded as pass.
3. Tests proving deterministic gate freshness is invalidated by either `HEAD` or deterministic working-tree fingerprint changes.
4. Tests for run creation requiring original request artifacts.
5. Tests for preflight folded YAML command comparison.
6. Tests for `.adlc/evidence/` ignore/tracked-file invariants at implementation completion and publication.
7. Tests for PR title selection precedence.
8. Tests for base-branch preparation with fast-forward and blocked unsafe states.
9. Tests for bootstrap metadata/version updates.
10. Skill contract tests for `spec-it`, `test-it`, and `retrospect-it` reflecting the new V0.6 workflow constraints.

## Out of Scope

1. Automatic human review or merge.
2. Automatic promotion of retrospective lessons.
3. A general-purpose CI-generation framework.
4. A broad YAML-analysis framework beyond what is needed for robust command comparison.
5. Destructive Git reset as normal workflow behavior.
