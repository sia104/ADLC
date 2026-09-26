approved specifications are authoritative
do not silently change requirements
prefer deterministic software/checks where appropriate
image processing must be deterministic
CI/build reproducibility is a workflow requirement where practical; prefer locked dependencies and explicit environments over floating resolution
critical development gates must state whether they are procedural/human-controlled or technically enforced
CI must pass before merge; this is currently a procedural human gate
humans control merge; this is currently a procedural human gate
technical enforcement may be added later when platform/repository settings allow it
reusable failures may later become tests, evals, playbooks, or rules
