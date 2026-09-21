# Executable fault-localization development check

Six local executions completed: two fictional corrections crossed with healthy operation, skipped commit, and obsolete-record retrieval. The existing evidence gate was executed unchanged. A new SQLite adapter saved records, closed the database, reopened it and selected memory. No AI calls were made.

| Injected condition | Accepted correction | Reopened current storage | Retrieved value | Diagnosis, both cases |
|---|---|---|---|---|
| Healthy | New | New | New | No observed divergence |
| Skip correction commit | New | Old | Old | Storage |
| Select oldest row | New | New | Old | Retrieval |

All six diagnoses matched the injected conditions. Retrieval-only correctness saw two correct and four incorrect outputs; it could not distinguish the two causes of the incorrect outputs. The recorded intermediate states distinguish the observed failure boundaries. The diagnostic received trace values, not the injected condition label.

This is stronger than manually constructing stage traces because the values were collected from running code and reopened storage. It remains a transparent development check: the authors designed both simple faults and the diagnostic; cases were not held out or independently assessed. Single-fault exact-value comparisons are intentionally easy. This is not a six-sample estimate of general diagnostic accuracy, a complete causal root-cause analysis, or a demonstration of faults naturally occurring in Evo.

The gate takes scripted trusted evidence. Acquisition language understanding and model response behavior were not tested. SQLite here stores only the record list; this adapter is a fault-test fixture, not a production replacement for the prior atomic full-state store. No concurrency, crash recovery, summaries, multi-fault combinations, paraphrases or automatic recovery were evaluated.

Paper use: report as an executable illustrative validation of the measurement procedure, accompanied by these limits. Stronger evaluation should freeze unseen cases and test realistic overlapping stores and incomplete instrumentation before any benchmark-validation claim.

Evidence: evo-pilot/executable-fault-results contains six databases, per-run gate/storage/retrieval snapshots, diagnoses, summary and hashes. Protocol: CMAI_Executable_Fault_Protocol.md. No API charges or reservation changes; prior shared reservation total remains $3.20 of $4.
