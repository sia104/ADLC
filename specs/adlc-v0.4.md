# ADLC V0.4 Upgrade Specification

Status: Approved by human on 2026-09-26

ADLC run: `20260926T175356395644Z-855f908b`

## Purpose

Upgrade the reusable ADLC from V0.3 to V0.4 while preserving its existing
specification, implementation, independent-testing, CI, human-review, merge,
closure, evidence, and retrospective behavior. V0.4 deterministically automates
Git and GitHub bootstrap, feature publication, and pull-request creation. It
does not add an AI skill or agent and does not automate human review or merge.

## Minimal configuration

1. Add `.adlc/config.json` with exactly the reusable settings needed by this
   upgrade:

   - `base_branch`: a non-empty valid Git branch name.
   - `repository_visibility`: either `public` or `private`.

2. This installation uses `master` as `base_branch` and `public` as
   `repository_visibility`.
3. Missing, malformed, or unsupported configuration is a clear blocking error;
   tooling does not silently invent or replace configured values.

## Startup and local Git bootstrap

1. Keep `.adlc/preflight.py` inspection-only. Add deterministic bootstrap
   tooling and invoke it from new-run creation before preflight evidence is
   captured. This preserves the V0.3 preflight contract while satisfying
   automated startup.
2. Resolve the project root explicitly and determine whether that directory is
   the top level of a Git work tree. A parent-directory repository does not
   count as a project repository.
3. Deterministic preflight verifies that both `user.name` and `user.email` are
   available whenever the workflow may need to create commits, including for
   every run in an existing repository. Missing identity is a blocker before
   implementation begins. Do not invent identity values.
4. When the project is not a Git repository, bootstrap also checks identity
   before initialisation and then initialises the project using the configured
   base branch.
5. Never reinitialise, delete, replace, or rewrite an existing project Git
   repository.
6. If the configured base branch has no commit, run the public-publication
   safety check when visibility is public, stage non-ignored project content,
   and create a deterministic initial commit. If identity is unavailable or
   the safety check fails, stop before creating a commit.
7. Existing commits, branches, remotes, and working-tree content are preserved.

## Local-only evidence

1. `.adlc/evidence/` is local run state and must not be uploaded to GitHub.
2. Add `.adlc/evidence/` to Git ignore rules. Bootstrap, commit, publication,
   and PR automation must never stage evidence contents.
3. During this upgrade, remove any already tracked `.adlc/evidence/` paths from
   the Git index while preserving the local files on disk. The resulting PR may
   remove historical evidence from the remote repository, but must not delete
   the local evidence directory.
4. Evidence validation and lifecycle behavior continue to operate against the
   local directory even though it is untracked.

## GitHub repository bootstrap

1. If a usable `origin` exists, preserve and use it. Never replace its URL.
2. If `origin` is absent, verify `gh` is installed and authenticated before
   changing remote state.
3. Derive the repository name from the project directory name and create it in
   the authenticated GitHub account using `gh repo create`, the configured
   visibility, and the existing local repository as the source.
4. Configure the created repository as `origin` and push the configured base
   branch with upstream tracking.
5. Name conflicts, missing CLI, failed authentication, creation failures, and
   push failures produce clear blockers. They do not replace remotes or record
   later lifecycle steps as successful.

## Public-publication safety

1. Before the first push to a public repository, run a deterministic scan of
   project publication candidates and obvious secret-bearing files. Exclude
   Git internals and generated tool caches, but do not exempt an `.env` or
   similarly obvious secret file merely because it is ignored by Git.
2. Block publication when detecting at least:

   - private-key headers or private-key filenames;
   - common credential, token, secret, or environment filenames;
   - credential/token assignment patterns already protected by the evidence
     subsystem;
   - protected evidence inputs that the evidence subsystem would reject.

3. Report paths and hazard classes without printing secret values.
4. The scan is deterministic and narrow. It does not classify commercial
   sensitivity or use an AI model.
5. A failed scan prevents repository creation or public push and leaves the
   lifecycle/evidence state short of publication success.

## Feature publication and pull requests

1. Add one deterministic publication command to the reusable ADLC tooling. It
   operates only for an active run whose independent-testing stage passed and
   whose lifecycle is ready for `pull-request`.
2. Verify the current branch is not the configured base branch, the working
   tree is clean, and `HEAD` contains committed changes. The command does not
   create implementation commits implicitly.
3. Ensure `origin` is usable, run public safety preflight when required, push
   the current feature branch, and establish upstream tracking when absent.
4. Record the pushed remote name, branch, and exact commit in the active
   evidence manifest before attempting PR creation.
5. Create a PR non-interactively with `gh pr create`, targeting the configured
   base branch and using the current branch as head. Generate a concise title
   from the latest commit subject and a concise body from the commit range and
   verification context.
6. Record the PR number and URL and advance coherently into the PR/CI lifecycle
   stage only after GitHub confirms creation. A failed push or PR command does
   not record success or advance the lifecycle.
7. Never push implementation directly to the base branch, create auto-merge,
   approve a review, or merge a PR.

## CI and human-controlled gates

1. Preserve the existing requirement for a recorded PR and pushed feature
   branch before CI.
2. Preserve explicit CI result capture. Failed or pending CI cannot advance to
   human review.
3. Preserve recorded human review approval and verified merge context before
   closure.
4. Human review and human merge remain procedural, human-controlled gates.

## Git and evidence consistency

1. Extend the local-only evidence schema only as needed to record bootstrap and
   publication state, including origin URL, remote branch, pushed commit, and PR
   context.
2. Filesystem/Git/GitHub operations complete successfully before their success
   state is appended to evidence. Failures record a blocker without claiming a
   later state.
3. Every lifecycle transition completes the stage being left. In particular,
   when merge context is recorded and run closure succeeds, the `merge` stage
   record must be `pass`, not `not_run`.
4. Manifest lifecycle, stage records, Git context, PR context, CI status, and
   merge status must remain mutually consistent under validation.
5. V0.3 evidence runs remain readable and valid; V0.4 does not rewrite prior
   immutable evidence.

## Required deterministic tests

Tests use temporary local repositories and mocked GitHub CLI behavior; the test
suite must not create real GitHub repositories or PRs.

1. A project with no Git repository is initialised on the configured base
   branch only when identity is available.
2. A project with an existing Git repository is preserved.
3. Missing identity blocks commit creation without invented values.
4. Every-run preflight blocks an existing repository with missing Git identity
   before implementation.
5. Evidence remains present locally but ignored and absent from the Git index.
6. Missing `origin` invokes authenticated GitHub bootstrap with configured
   visibility; an existing `origin` is preserved.
7. Public visibility is read correctly from configuration.
8. Each required publication hazard class blocks a public push without leaking
   the matched secret value.
9. A clean committed feature branch is pushed and records upstream branch and
   commit state.
10. A PR is created with configured base/current head and its number/URL are
   recorded.
11. The lifecycle cannot advance to CI before a PR exists or while the feature
   branch is not pushed.
12. Failed/missing GitHub CLI or authentication produces a clear blocker and
    does not corrupt Git, remote, PR, or lifecycle state.
13. Closure after a verified human merge records the merge stage as `pass`, and
    validation rejects inconsistent lifecycle/evidence Git state.
14. Existing V0.3 tests continue to pass, with compatibility updates only where
    the V0.4 contract intentionally changes behavior.

## Documentation and version

1. Set `.adlc/VERSION` and the tooling's expected canonical version to `V0.4`.
2. Update reusable ADLC documentation with configuration, startup bootstrap,
   public safety behavior, publication command, failure recovery, and remaining
   manual boundaries.
3. At completion report changed files, the resulting Git/GitHub lifecycle,
   quality gates run, and the remaining human review and merge boundaries.

## Acceptance criteria

1. All required deterministic tests above pass without live GitHub mutations.
2. All commands in `.adlc/quality-gates.json` pass unchanged or with explicit
   additive strengthening; no existing gate is weakened.
3. A V0.4 run validates with coherent stage, Git, PR, CI, and merge evidence.
4. A deterministic test demonstrates the no-repository through PR-created path
   using mocked external GitHub operations and public safety checks.
5. No new skill, agent, auto-review, auto-approval, or auto-merge capability is
   added.
