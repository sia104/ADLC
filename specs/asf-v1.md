# Autonomous Software Factory (ASF) V1 Specification

Status: **Pending human approval** (design decisions D1–D8 approved 2026-11-27; full spec not yet approved)

ASF V1 is the next version of this repository (ADLC → ASF). ADLC's evidence, lifecycle and ratchet code is reused and hardened.

## 1. Request

Build an autonomous software factory: a spec or goal goes in; tested, working, documented software comes out and lands on the base branch with verifiable evidence. The human decides what to build, answers one batch of judgment questions up front, and steers on taste. Agents do everything else. The model is Tristan Manchester's "How I work with agents" (Nov 2026), improved where it lacks guarantees.

## 2. Approved decisions

| ID | Decision |
| --- | --- |
| D1 | **Posture: hybrid, risk-tiered.** Low-risk work runs in a fast lane (full access, local verify, agent merges). High-risk work adds stricter gates. AGENTS.md is updated to match (§10). |
| D2 | **Runtime: T3 Code plus Claude and Codex subscriptions.** T3 threads, delegated child threads, worktrees, environment links and scheduled tasks are the control plane. Runs are budgeted by subscription usage, not dollars. |
| D3 | **Merge: the agent always merges** once its tier's gates pass. The human is notified, not asked. |
| D4 | **High-risk changes: the agent merges behind stricter gates**: GitHub CI plus a second independent cross-family reviewer, with a post-merge notification. |
| D5 | **Modes in V1: Build, Lab, Maintain, Release.** |
| D6 | **Location: evolve this ADLC repo.** |
| D7 | **Machines: this Mac** (interactive and product work) **plus an existing Linux box over Tailscale** (unattended, overnight and lab runs). |
| D8 | **The human role is intent, taste, real data and anything published**, not line-by-line diff review. |

## 3. Design basis

| Source | Adopted |
| --- | --- |
| Tristan Manchester, "How I work with agents" | T3 Code as the control plane on two machines; subscriptions over API; Opus builds and a fresh Codex agent reviews in rounds until no accepted issues remain; global AGENTS.md plus a modular skills library; local `verify` instead of CI wait; persistent shared test devices; ops through CLIs; "decide first, then run unattended" (at most 4 questions); scheduled maintenance; a lab harness with mixed agents, a goals file, a message board, a single-owner resource queue and bubblewrap |
| StrongDM Software Factory | Holdout scenarios outside the builder's reach; satisfaction metric; digital twins of third-party services |
| Anthropic harness posts | Planner / generator / evaluator split; sprint contracts; a skeptical evaluator driving the real app; a JSON feature ledger; fresh context per task; ablate harness parts per model release |
| OpenAI Symphony / harness engineering | A single state authority; workspace path invariants; a repo-owned WORKFLOW.md; backoff, stall detection and reconciliation; per-worktree bootable app; lint messages that carry the fix; entropy-cleanup agents |
| Spec Kit / Kiro | Constitution; specify → plan → tasks → implement; `[NEEDS CLARIFICATION]` markers; EARS requirements |
| Superpowers | Fresh implementer per task; per-task and whole-branch review; a ledger that survives compaction; "rulings, not stalls" |
| good-engineering, Impeccable | Tests as evidence; readiness graded documented → demonstrated; deterministic slop detector as a pre-done hook; P0–P3 audits |
| ADLC V0.6 murder board | Gates derived from executed checks; product gates, not just factory gates; failure edges in the state machine |

**Where ASF improves on Tristan's setup:** holdout tests the builder cannot see (§6.2), a deterministic gate ledger instead of an agent's word, signed evidence per landed change, risk tiers, cheat-resistance tests, and a factory eval suite so the factory itself improves measurably.

## 4. Principles (normative)

P1. **Facts, not claims.** A gate passes only when `asf` executed it and recorded the exit code against the exact commit and tree. An agent saying "tests pass" never advances anything.
P2. **Builder ≠ judge.** The reviewer and the evaluator are a different model family from the implementer, start from a fresh context, and see only the diff, the source and the spec.
P3. **External behaviour is the acceptance oracle.** Run the real thing: process, HTTP, CLI, browser, simulator, GPU benchmark.
P4. **Decide first, then run unattended.** Each run asks at most 4 judgment questions, in one batch, before it starts. After that it makes rulings and logs them, and stops only for P5 cases.
P5. **Stop only for:** an irreversible or destructive action outside the run's scope; an action involving secrets or credentials; a bound being hit (§7); or a spec so broken that every path forward is a guess.
P6. **Everything is bounded**: review rounds, remediation loops, wall-clock time, usage. Hitting a bound escalates; it never passes.
P7. **The factory improves only through evals.** A factory change lands only if the factory eval suite does not regress.

## 5. Architecture

```
            ┌────────────── Mac (interactive) ──────────────┐        Tailscale        ┌──────── Linux box (unattended) ────────┐
 human ───► │ T3 Code: parent thread runs an asf-* skill     │ ◄──── environment ────► │ t3code.service                          │
            │   ├─ child threads in worktrees (Claude/Codex) │        link             │   ├─ build runs (bubblewrap sandbox)    │
            │   └─ asf CLI (deterministic core)              │                         │   ├─ lab runs (4–12 agents, 12–48h)     │
            │ shared devices: iOS sim, Android emulator      │                         │   ├─ resource queue (GPU, devices)      │
            └────────────────────────────────────────────────┘                         │   └─ sealed store (holdouts, ledger)    │
                                                                                       └─────────────────────────────────────────┘
```

- **Control plane (T3 Code).** A parent thread runs a mode skill (`asf-build`, `asf-lab`, `asf-maintain`, `asf-release`). It spawns child threads with `delegate_task` (a provider per role, `isolation: worktree`), uses environment links to place unattended work on the Linux box, and uses scheduled tasks for maintenance.
- **Deterministic core (`asf` CLI, Python, evolved from `.adlc/`).** It is the only writer of run state. Commands include `asf run new`, `asf gate run`, `asf review record`, `asf holdout seal`, `asf eval`, `asf land` and `asf audit`. It runs gates itself, keeps the hash-chained event ledger, computes risk tier and decides whether a change may land. Skills call it; agents never edit its files directly.
- **Skills.** Authored once in this repo under `skills/`, then generated and installed for Claude Code and Codex (global `~/.agents/skills/` plus per-repo links), with `asf-*` mode skills plus role skills (`asf-implement`, `asf-review`, `asf-evaluate`, `asf-test-author`). The global AGENTS.md gets the ASF defaults (§10).
- **Usage budgeting.** Each run declares a budget in turns and wall-clock time per role. When a subscription limit is hit, the run waits for the window to reset and resumes from the ledger. It does not switch to paid API calls.

## 6. Modes

### 6.1 Build (spec → landed software)

| Stage | Who | Output and exit fact |
| --- | --- | --- |
| 0 Intake | Clarifier (Opus) + `asf spec lint` | Spec with REQ-IDs in EARS form, no TBDs. At most 4 questions in one batch; the answers are written into the spec. Exit: spec hash frozen plus a recorded human "go" (the single human touchpoint). |
| 1 Plan | Planner (Opus) | `plan.md`, `tasks.json` (a DAG; each task → REQ-IDs, owned files, done criteria), sprint contracts. `asf` checks REQ coverage, that the DAG is acyclic, and that parallel tasks own disjoint files. |
| 2 Seal | Test author (Codex, spec only) | Public acceptance tests (committed) and **holdout scenarios** (sealed store, never mounted into a builder sandbox). `asf` checks that each REQ has at least one test and one scenario, and that public tests fail against the skeleton (red check). |
| 3 Build | Implementer per task (Opus for judgment-heavy tasks, Sonnet for mechanical ones), parallel worktrees | TDD; `asf gate run verify` executed by `asf`. Protected paths (holdouts, acceptance tests, gates, workflows, the spec, factory code) are read-only in the sandbox. |
| 4 Review loop | Fresh Codex reviewer per round | Reads the diff, source and spec excerpt only. The implementer fixes accepted findings; a new fresh reviewer runs each round, until a round finds no accepted issues. Cap: 12 rounds, then escalate. Each verdict is recorded with `asf review record`. |
| 5 Evaluate | Evaluator (Codex, or Opus if a Codex model built it), on the Linux box | Boots the app from the README only, then drives every holdout scenario through the real interface (Playwright, HTTP, CLI, `agent-device`, GPU queue). Pass: all deterministic assertions pass, satisfaction ≥ 0.95 over 3 runs per scenario, and zero P0/P1 findings. Failures return to stage 3 as behaviour-only bug reports. |
| 6 Harden | `asf` + skills | gitleaks, Semgrep, osv-scanner; Impeccable `detect` and `audit` for UI; mutation testing on REQ-tagged code; a fresh no-context agent follows the README to a running app. |
| 7 Land | `asf land` | Recomputes risk tier, confirms every gate of the tier is fresh for this exact tree, writes a signed attestation (REQ → tests → scenarios → status, review rounds, satisfaction, usage), merges, then notifies the human. |

### 6.2 Holdout integrity

Unattended build runs execute on the Linux box under bubblewrap. Builder sandboxes mount the worktree read-write and the protected paths read-only, and never mount the sealed store. Interactive runs on the Mac can't guarantee this, so they are tagged `holdout: unsealed`, and their changes land only at the low-risk tier, or after an evaluator pass on the Linux box.

### 6.3 Lab (open-ended research)

- **Input:** `GOALS.md` with measurable targets on real datasets, kill criteria and a time box (12–48h).
- **Agents:** 4–12 mixed Claude and Codex agents, each in its own worktree in an independent clone, with git inside bubblewrap and no network. Run checkouts are marked untrusted.
- **Shared resources:** the GPU and devices are owned by a single FIFO `asf queue`; agent shells cannot reach them directly.
- **Coordination:** a SQLite message board (posts, one-level replies, `@agent-NN` mentions) with a read-only web viewer over Tailscale.
- **Rules:** design the cheapest test that could kill an approach in the first hour; post numbers including failures; pair up to break each other's branches.
- **Exit:** at the time box, `asf lab report` ranks branches by goal metrics using queued benchmark results, not agent claims. The best branch is promoted into a Build run (stage 4 onward) to land.

### 6.4 Maintain (scheduled)

T3 Code scheduled tasks, each reading a repo-local `PLAN.md` policy before acting:
- dependency and CVE watch;
- entropy and doc-gardening passes that open small Build runs;
- factory eval suite nightly on the Linux box;
- `asf audit`, which checks that every commit on each base branch has a valid attestation and alerts on any that don't.

Changes made in this mode go through Build stages 3–7.

### 6.5 Release (decide first, then run unattended)

Collect state (commits since the last release, store/registry status), ask at most 4 questions in one batch (version, notes, assets, scope), then build, upload, sync metadata and submit through CLIs (`eas`, `asc`, `gplay`, `xcodebuild`, package registries, deploy CLIs) without interruption unless something breaks. Anything public-facing is high-risk tier.

## 7. Risk tiers and gates

The tier is computed by `asf` from changed paths, labels and target. It is never declared by an agent.

| Gate | Low | High |
| --- | --- | --- |
| Local `verify` (format, lint, types, tests) run by `asf` | ✓ | ✓ |
| Fresh cross-family review loop until clean | ✓ | ✓ |
| Holdout evaluation (sealed) | ✓ when the change touches behaviour | ✓ always |
| Harden scans + README test | ✓ | ✓ |
| GitHub CI green on head SHA | — | ✓ |
| Second independent reviewer (other family, fresh) | — | ✓ |
| Mutation testing on changed REQ-tagged code | — | ✓ |
| Post-merge human notification | summary | immediate, with diff link |

High-risk paths (default, configurable in `.asf/WORKFLOW.md`): auth, payments, crypto, data migrations, infra/deploy, CI, `.asf/`, factory code, public releases, public-repo first publish.

Bounds per run (defaults, configurable): 12 review rounds, 5 remediation loops, 8h wall clock for a build and 48h for a lab, and a per-role turn budget. Hitting a bound escalates to the human; work never lands on a bound hit.

## 8. State machine (owned by `asf`)

`intake → awaiting-go → planning → sealing → building → reviewing → evaluating → hardening → landing → landed → learning → closed`

These edges are required:
- `reviewing | evaluating | hardening → building`
- `landing → building` (CI red or a stale gate)
- `awaiting-go → intake` (spec changed or rejected)
- `any → waiting-usage` (subscription limit), which resumes to the prior state
- `any → escalated` (a bound or a protected-path violation)
- `escalated → prior state` (on a human ruling)
- `any → abandoned`

Kill-and-resume is driven by the ledger. Each task has its own sub-states: claimed, running, stalled, retry-queued with backoff, done or failed.

## 9. Security posture

- Full access is allowed for interactive Mac threads (D1). Unattended runs on the Linux box use bubblewrap: no network for git, an egress allowlist for agents, and protected paths read-only.
- Credentials (GitHub, stores, APIs) are used by `asf` and the release CLIs on the host. They are never printed into agent context or evidence.
- GitHub: on repos with high-risk paths, a ruleset requires the CI check for high-tier merges. New repos default to private.
- `asf audit` makes tampering detectable after the fact even where it can't be prevented interactively (full-access Mac).
- Untrusted text (issues, web pages, board posts) is treated as data and grants no authority.

## 10. Governance changes (require explicit approval when implemented)

Replace AGENTS.md rules "CI must pass before merge" and "humans control merge" with this: changes land through `asf land`, which enforces the tier gates in §7. GitHub CI is required for the high tier. The human is notified of every landing and can revert. The quality-gate non-weakening rule stays, and now applies to `.asf/gates.toml` and the factory eval suite.

## 11. Repository layout

Factory repo (this one): `asf/` (core, evolved from `.adlc/`), `skills/` (source for all skills), `evals/` (factory benchmark specs and tamper tests), `specs/`.

Consuming project:
```
spec/<feature>/spec.md, plan.md, tasks.json, contracts/
tests/acceptance/                     # public acceptance tests (protected)
.asf/WORKFLOW.md                      # tiers, budgets, models, thresholds, devices
.asf/gates.toml                       # verify command + project gates (weakening = error)
AGENTS.md  PRODUCT.md  DESIGN.md  PLAN.md
```
The sealed store on the Linux box (`~/.asf/store/<project>/`) holds holdouts, the run ledger and attestations.

## 12. Acceptance criteria

- AC1. Build: 5 benchmark specs (CLI, REST API, web UI, mobile app screen, bug fix in an existing repo) each go from "go" to landed with zero human input in between.
- AC2. On each: every tier gate passes, holdout satisfaction ≥ 0.95, the README test passes, and the review loop ends with a clean fresh round.
- AC3. Tamper suite: an implementer instructed to (a) read or edit a holdout, (b) weaken a gate, (c) record its own review or gate result, (d) mark the risk tier low, (e) merge outside `asf land` is blocked in (a)–(d) on the Linux box, and (e) is flagged by `asf audit` within one scheduled cycle.
- AC4. Kill the orchestrating thread and `asf` mid-build: the run resumes from the ledger with no duplicate task work.
- AC5. Subscription limit hit mid-run: the run enters `waiting-usage` and resumes automatically. No API fallback.
- AC6. Lab: an 8-agent, 12h run on a benchmark goal produces a ranked report from queued benchmark results, and the winning branch lands through Build.
- AC7. Release: a dry-run release asks at most 4 questions, then completes unattended against a test store or registry target.
- AC8. Every landed change has a valid attestation; `asf audit` reports zero gaps.
- AC9. The factory eval suite (AC1–AC7 scenarios) runs nightly; a regression blocks factory changes from landing.

## 13. Delivery order

1. Harden the reused core: hermetic tests, failure edges, executed-check gates only, `asf` CLI shape, risk-tier computation.
2. Build mode walking skeleton on the Mac: intake → plan → implement → Codex review loop → `asf land` for the CLI benchmark.
3. Linux box: environment link, bubblewrap runner, sealed store, holdout evaluator; tamper suite.
4. Parallel DAG builds, harden stage, attestations and `asf audit`; update AGENTS.md (§10).
5. Release mode and Maintain mode (scheduled tasks).
6. Lab mode: board, queue, report, promotion into Build.
7. Factory eval suite nightly; ablate each harness part against it.

## 14. Out of scope for V1

Paid-API fallback, multi-user or multi-tenant use, cloud sandboxes, production monitoring and incident response, autonomous changes to the factory's own gates or eval suite.
