approved specifications are authoritative
do not silently change requirements
prefer deterministic software/checks where appropriate
user-runnable software must include concise setup/run documentation sufficient to install, launch, and verify the application
verification should cover the real user execution path where practical, not only internal/unit behaviour; this may include real process startup, HTTP access, and end-to-end UI behaviour where relevant
when diagnosing failures, isolate the root cause before making multiple corrective changes at once unless safety or urgency requires otherwise
CI/build reproducibility is a workflow requirement where practical; prefer locked dependencies and explicit environments over floating resolution
critical development gates must state whether they are procedural/human-controlled or technically enforced
CI must pass before merge; this is currently a procedural human gate
humans control merge; this is currently a procedural human gate
technical enforcement may be added later when platform/repository settings allow it
reusable failures may later become tests, evals, playbooks, or rules
