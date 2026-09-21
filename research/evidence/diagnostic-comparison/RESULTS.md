# Diagnostic comparison: results and implications

## What ran
64 deterministic SQLite executions: two fictional corrections × all 32 combinations of acquisition, saving, retrieval, response and recovery switches. No language model, API calls, private data or expenditure. This is a newly written synthetic adapter, not Evo. Cases and method were authored together; this is development evidence, not held-out or independent validation.

| Available observations | Correct definite diagnosis | Inconclusive | Incorrect definite diagnosis | Agreement with equivalent ordinary logs |
|---|---:|---:|---:|---:|
| All four checkpoints | 64 | 0 | 0 | 64/64 |
| Storage missing | 32 | 32 | 0 | 64/64 |
| Retrieval missing | 48 | 16 | 0 | 64/64 |
| Final answer only | 0 | 64 | 0 | 64/64 |

“Diagnosis” means earliest observed value mismatch, not the software root cause or identification of every injected fault. Counts cover a factorial construction and are not independent statistical samples. Complete observations plus exact-value comparison make localization straightforward by design; 64/64 is not evidence of general diagnostic accuracy.

## What this adds
- Equivalent ordinary logs tie structured records throughout. There is no demonstrated superiority from formatting a correction trace. The useful recommendation is retaining the necessary evidence.
- 12/64 executions produce the correct final answer despite an earlier divergence. A fallback can hide a failed correction path from final-answer scoring.
- Both answer-only patterns (correct and incorrect) correspond to multiple possible earlier-divergence labels. Within this fault family, final answers alone cannot uniquely localize the earlier failure.
- Removing storage produces three ambiguous observation patterns; removing retrieval produces one. These are direct examples of insufficient information, not failures that should receive confident labels.
- The conservative diagnostic sometimes abstains even when the bounded fault-family oracle could narrow the answer further. It does not assume that production failures belong to the enumerated family.

## Concrete example
An accepted Tuesday correction can fail to save, leaving Friday in the reopened database. Retrieval recovery supplies Tuesday directly from the correction and the response returns Tuesday. The answer is correct while the stored memory remains outdated. A healthy execution can also return Tuesday. Final-answer correctness does not distinguish them.

## What remains unproven
Realistic frequency, advantage over existing tracing methods, semantic diagnoses, trusted telemetry in deployment, human debugging benefits, full Evo behavior and external replication. Deterministic response stubs do not establish LLM behavior. Recovery deliberately overrides retrieval selection. Several injected faults can be masked, and the earliest mismatch does not identify them all.

## Manuscript recommendation
Reframe this addition as an observability and abstention example. Include the ordinary-log tie and recovery counterexample, without claiming a new diagnostic algorithm or major breakthrough. Keep the existing manuscript unchanged pending integration and author review. An accessible evidence repository, stronger external-system evaluation and author ownership review remain unresolved.

## Reproduction
Use Python's standard library to run run.py in a fresh copy of this folder without results-v1. It refuses to overwrite existing results. Read PROTOCOL.md and EXECUTION_NOTE.md first. Recorded executions, summary and hashes are in results-v1. No credentials are required. The protocol was saved before execution locally; this is not externally registered preregistration.
