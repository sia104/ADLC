# ADLC

Canonical reusable **AI-assisted Application Development Life Cycle (ADLC)**.

Current version: **V0.5**

Repository: `https://github.com/sia104/ADLC`

The ADLC is designed to provide a small, deterministic, evidence-driven development workflow that can be installed into new or existing software projects and progressively improved using observed failures and lessons from real development runs.

The design intentionally separates:

* deterministic workflow controls;
* reusable Codex skills;
* human approval gates;
* application/product code;
* evidence and retrospective analysis.

The ADLC should evolve incrementally rather than becoming a large agent-orchestration framework.

---

## ADLC evolution

The current development history is:

* **V0** — initial `spec-it` and `implement-it` workflow with deterministic CI.
* **V0.1** — improved specification discipline after observing silent requirement expansion.
* **V0.2** — added independent `test-it`, runtime verification, documentation requirements, and structured evidence capture.
* **V0.3** — added deterministic lifecycle orchestration, repository preflight, evidence improvements, Git workflow governance, and `retrospect-it`.
* **V0.4** — automated Git/GitHub bootstrap, feature-branch publication, pull-request creation, and public-repository safety checks.
* **V0.5** — added versioned ADLC bootstrap distribution so the reusable ADLC can be installed into projects without manually copying files.

---

# Architecture

The reusable ADLC consists of four main components:

```text
.adlc/
.codex/skills/
.github/workflows/adlc.yml
AGENTS.md
```

Their responsibilities are intentionally separate.

## `.adlc/`

Contains deterministic ADLC infrastructure, including:

* lifecycle state machine;
* evidence capture;
* repository preflight;
* Git/GitHub operations;
* configuration;
* quality-gate definitions;
* schemas;
* ADLC tests;
* ADLC version information.

The ADLC runtime should perform deterministic work wherever practical rather than delegating predictable operations to an LLM.

## `.codex/skills/`

Contains reusable AI skills:

```text
spec-it
implement-it
test-it
retrospect-it
```

### `spec-it`

Turns a user request into a minimally sufficient, testable product specification.

Mandatory requirements should originate from:

* the user's explicit request;
* a requirement necessary to remove material ambiguity;
* an explicit human-approved design choice.

Unrequested enhancements should normally remain optional rather than silently becoming requirements.

### `implement-it`

Implements an approved specification.

It must not silently redefine or weaken requirements.

It creates or updates appropriate deterministic tests and user-facing setup/run documentation.

### `test-it`

Independently verifies the implementation against the approved specification.

It operates separately from implementation and reports:

* verified acceptance criteria;
* failures;
* unverified criteria;
* verification gaps.

It does not silently repair production code.

### `retrospect-it`

Analyses a completed ADLC evidence run and proposes evidence-backed lessons.

Trust level:

```text
OBSERVE / PROPOSE ONLY
```

It may propose changes to future ADLC versions, but it must never directly modify or promote changes to:

* `AGENTS.md`;
* skills;
* CI;
* tests;
* ADLC tooling;
* application code.

Human approval is required before a proposed lesson becomes an ADLC change.

---

# Lifecycle

The normal development lifecycle is:

```text
user request
    ↓
preflight
    ↓
evidence run creation
    ↓
spec-it
    ↓
HUMAN SPECIFICATION APPROVAL
    ↓
feature branch
    ↓
implement-it
    ↓
test-it
    ↓
remediation loop if required
    ↓
push feature branch
    ↓
create pull request
    ↓
CI
    ↓
HUMAN REVIEW
    ↓
HUMAN MERGE
    ↓
close evidence run
    ↓
retrospect-it
    ↓
candidate lessons
    ↓
HUMAN RATCHeT DECISION
```

The lifecycle controller rejects invalid transitions where practical.

For example:

* implementation should not begin before specification approval;
* implementation should not occur directly on the base branch;
* CI should not be treated as complete before a pull request exists;
* merge should not be recorded before the required preceding gates;
* retrospective analysis should operate on completed runs.

Human review and merge remain human-controlled gates.

---

# Bootstrap a new project

V0.5 introduces the `adlc-bootstrap` command.

This removes the need to manually copy `.adlc`, `.codex`, `.github`, and `AGENTS.md` into every new project.

## Requirements

Bootstrap requires:

* Git;
* Python 3.12 or newer;
* `uv`.

For full GitHub automation during an ADLC run, also install and authenticate:

* GitHub CLI (`gh`).

---

## Create a new project

Install ADLC V0.5 into a new directory:

```bash
uvx --from git+https://github.com/sia104/ADLC@v0.5.0 \
  adlc-bootstrap init my-project
```

Then:

```bash
cd my-project
```

The project should contain approximately:

```text
my-project/
├── .adlc/
│   ├── VERSION
│   ├── install.json
│   ├── config.json
│   ├── evidence.py
│   ├── lifecycle.py
│   ├── preflight.py
│   ├── gitops.py
│   ├── quality-gates.json
│   ├── schema/
│   ├── tests/
│   ├── pyproject.toml
│   └── uv.lock
├── .codex/
│   └── skills/
│       ├── spec-it/
│       ├── implement-it/
│       ├── test-it/
│       └── retrospect-it/
├── .github/
│   └── workflows/
│       └── adlc.yml
├── .gitignore
└── AGENTS.md
```

---

## Install into an existing project

From the existing project's root:

```bash
uvx --from git+https://github.com/sia104/ADLC@v0.5.0 \
  adlc-bootstrap init .
```

The bootstrapper does not silently overwrite conflicting existing files.

If an existing managed file differs from the ADLC version being installed, bootstrap stops and reports the conflict.

Identical files may be reused safely.

---

# Version provenance

Every installed ADLC records its installation provenance in:

```text
.adlc/install.json
```

This includes information such as:

* installed ADLC version;
* source repository;
* release/tag;
* source commit;
* installation timestamp;
* hashes of managed files.

This allows development evidence to be tied to the exact ADLC version that produced it.

The canonical ADLC version is stored in:

```text
.adlc/VERSION
```

For this release:

```text
V0.5
```

The corresponding Git release/tag is:

```text
v0.5.0
```

Projects should normally bootstrap from an immutable release tag rather than from `master`.

---

# Managed versus project-owned files

The bootstrapper installs only reusable ADLC components.

It does **not** copy canonical-repository-only files such as:

```text
specs/
README.md
root canonical pyproject.toml
root canonical uv.lock
.git/
```

Application requirements, source code, tests, and product documentation remain owned by the consuming project.

This separation is deliberate.

---

# Configuration

Reusable configuration lives in:

```text
.adlc/config.json
```

The current default configuration is:

```json
{
  "base_branch": "master",
  "repository_visibility": "public"
}
```

The configuration is intentionally small.

Do not expand it into a general configuration framework without demonstrated need.

---

# Git and GitHub automation

During an ADLC run, deterministic tooling can:

* detect whether Git is already configured;
* initialise a repository when necessary;
* verify Git identity;
* detect or create an `origin`;
* create a GitHub repository when needed;
* use the configured repository visibility;
* create and use a feature branch;
* push the feature branch;
* create a pull request;
* record Git and GitHub context in evidence.

The ADLC must not silently replace an existing Git repository or remote.

Human review and merge are not automated.

---

# Public repository safety

The default repository visibility is currently:

```text
public
```

Before first publication to a public repository, the ADLC performs deterministic checks for obvious publication hazards such as:

* private keys;
* credentials;
* tokens;
* `.env` files;
* common secret-bearing configuration;
* content already rejected by evidence secret protections.

The scanner is intentionally narrow.

It does not attempt to determine whether source code is commercially, legally, or personally sensitive.

Users remain responsible for deciding whether a project is suitable for public publication.

---

# Evidence

Each ADLC development run creates structured evidence under:

```text
.adlc/evidence/
```

Run evidence is local and is ignored by Git by default.

Evidence may include:

* original user request;
* approved specification;
* skill and constitution versions;
* Git context;
* stage outcomes;
* deterministic verification;
* CI results;
* human decisions;
* failures;
* interventions;
* derived observations;
* candidate lessons.

Raw evidence and derived interpretation are kept separate.

Evidence is designed to support:

```text
development run
      ↓
evidence
      ↓
retrospective
      ↓
candidate lesson
      ↓
human review
      ↓
future ADLC improvement
```

The ADLC must never automatically promote an AI-generated lesson into workflow policy.

---

# ADLC verification

The reusable ADLC has its own environment under:

```text
.adlc/
```

This keeps ADLC verification separate from the application's dependencies.

Synchronise the ADLC verification environment with:

```bash
uv sync --project .adlc --frozen --extra dev
```

Run ADLC tests:

```bash
uv run --project .adlc --frozen pytest .adlc/tests
```

Run ADLC linting:

```bash
uv run --project .adlc --frozen ruff check .adlc
```

Run ADLC type checking:

```bash
uv run --project .adlc --frozen mypy \
  .adlc/evidence.py \
  .adlc/lifecycle.py \
  .adlc/preflight.py \
  .adlc/adlc_config.py \
  .adlc/gitops.py
```

---

# CI

A consuming project receives:

```text
.github/workflows/adlc.yml
```

This workflow verifies the reusable ADLC infrastructure.

Product/application CI should remain separate and should be created or extended according to the application's technology and approved specification.

The ADLC must not assume that every application is a Python application.

---

# Canonical repository development

The canonical repository itself contains additional development infrastructure required to build and verify `adlc-bootstrap`.

Set up the canonical repository environment with:

```bash
uv sync --frozen --extra dev
```

Run bootstrap tests:

```bash
uv run --frozen pytest
```

Run all lint checks:

```bash
uv run --frozen ruff check .
```

Run canonical type checking:

```bash
uv run --frozen mypy \
  src/adlc_bootstrap \
  .adlc/evidence.py \
  .adlc/lifecycle.py \
  .adlc/preflight.py \
  .adlc/adlc_config.py \
  .adlc/gitops.py
```

Build the bootstrap package:

```bash
uv build
```

Test the CLI:

```bash
uv run adlc-bootstrap --help
```

---

# Starting a development run

Once the ADLC is installed, the intended interaction is deliberately minimal.

For example:

```text
MedianView5 is a simple Python web application where a user uploads an image,
a fixed 3x3 median filter is applied, and the original and filtered images are
displayed side-by-side.
```

The ADLC should handle the reusable lifecycle itself rather than requiring the user to repeatedly restate instructions such as:

* start evidence capture;
* invoke `spec-it`;
* create a feature branch;
* invoke `test-it`;
* push the branch;
* create a pull request.

The user should normally need to intervene only for genuine human decisions such as:

* specification approval;
* remediation approval where appropriate;
* final review;
* merge;
* lesson promotion.

---

# Design principles

The ADLC follows several principles.

## Deterministic before agentic

Use deterministic software for operations that are:

* predictable;
* testable;
* repeatable;
* stateful;
* safety-critical.

Use AI skills primarily where judgement, interpretation, generation, or analysis is useful.

## Minimum sufficient specification

Specifications should be precise enough to remove important ambiguity and support objective verification, but should not invent unnecessary product requirements.

## Human-controlled promotion

Evidence and AI analysis may propose improvements.

They must not autonomously modify the ADLC.

## Evidence-driven ratchet

New controls, tests, skills, or automation should preferably be introduced in response to observed failures or repeated friction rather than speculative future requirements.

## Preserve working components

Existing working parts of the ADLC should remain unchanged unless there is evidence supporting a modification.

## Avoid unnecessary agentification

Do not introduce an AI agent when deterministic software, a reusable skill, or a simple human gate is sufficient.

---

# Current limitations

V0.5 intentionally does not provide:

* automatic ADLC upgrades;
* automatic conflict merging;
* automatic human review;
* automatic merge;
* autonomous ADLC self-modification;
* a database-backed evidence system;
* a dashboard;
* a general workflow engine;
* plugin management;
* dependency resolution between ADLC components.

`adlc-bootstrap upgrade` is deliberately not implemented yet.

The information recorded in `.adlc/install.json` is intended to support a future upgrade mechanism if real project usage demonstrates the need.

---

# Release policy

Canonical releases should use Git tags such as:

```text
v0.5.0
v0.6.0
v0.7.0
```

Consuming projects should normally install a tagged release rather than the current `master` branch.

Example:

```bash
uvx --from git+https://github.com/sia104/ADLC@v0.5.0 \
  adlc-bootstrap init my-project
```

This makes ADLC usage reproducible and allows development evidence to be associated with a specific workflow version.

---

# Goal

The long-term objective is not simply to automate software development.

The objective is to create an ADLC that becomes progressively:

* more reliable;
* more measurable;
* more reproducible;
* more reusable;
* more autonomous where evidence supports autonomy;
* easier for humans to supervise.

Each software project acts as an experiment that produces evidence for improving the development process itself.
