# Research evidence guide

This supplement supports the draft **Tracing Corrections Through AI Companion Memory**, not a validated AI evaluation product. All demonstrations were authored during development. No independent validation, new experiments, real-assistant compatibility or new model responses are claimed here.

## Run the free checks

Python 3.10+ and its standard library are sufficient. From the repository root (or archive root):

```sh
python research/verify.py
python research/verify.py --offline
```

The first verifies package hashes, 18 preserved request/response pairs, request manifests, and existing extracted answers. It does **not** call a model or grade the answers anew. The second additionally reruns the six synthetic fault executions, 64-case factorial comparison, 12 portable-export assertions and generation of the 18 request inputs, in automatically cleaned temporary directories. It compares results to preserved records and exits nonzero on mismatch. No credentials or API runner are included. Do not use Python's `-O` flag: some preserved historical scripts use assertions.

The checker tests are a separate command:

```sh
python -m unittest discover -s . -p "test_*.py"
```

Passing those nine tests verifies the developer tool's reporting behavior. **It does not reproduce every experiment in the paper.** CI invokes both commands separately.

## Evidence map

Table numbers refer to the 11-page manuscript source in `paper/paper.tex` (a draft, not submitted or accepted). Paths below are relative to `research/`.

| Paper result | Supporting files | What can be reproduced |
|---|---|---|
| Table 1: evidence boundaries | Paper protocol; checker adapter contract | Conceptual requirements, not an experimental result |
| Table 2 / six original fault executions | `evidence/CMAI_Executable_Fault_Protocol.md`; `evidence/evo-pilot/executable_fault_check.py`, `evidence_gate.py`, `memory_candidate.py`; `evidence/evo-pilot/executable-fault-results/*.json` | `python research/verify.py --offline`: reruns all six, checks full JSON after normalizing only generated UUIDs, and exact summary; no LLM |
| Table 3 / 64-execution comparison | `evidence/diagnostic-comparison/PROTOCOL.md`, `run.py`, `EXECUTION_NOTE.md`, `results-v1/executions.json`, `results-v1/summary.json` | Same offline command: exact JSON agreement for all 64 traces and summary. Two examples times 32 switch combinations, not 64 independent realistic problems |
| Table 4 / 12 recorded model responses | `evidence/CMAI_Local_Context_Protocol.md`, `CMAI_Local_Context_Behavior_Results.md`; `evidence/evo-pilot/context-path-v1-prepared/requests.jsonl`, `manifest.json`; `context-path-v1-results/*.json` | Free inspection and request/output integrity checks. Offline generation of identical prompts from recorded contexts, **not** new model responses |
| Context construction feeding Table 4 | `evidence/evo-pilot/local-path-diagnostic-results.json`; `CMAI_Local_Path_Findings.md`; `prepare_context_path.py` | Inspect saved contexts and helper traces. Original Evo/PHP source is not distributed or executed here; original context construction itself is **not independently reproduced** by this package |
| Supporting export/restore demonstration | `evidence/evo-pilot/portable_memory.py`, `demo_portable_memory.py`, `restart-trace-results/accepted-retrieve.json`; `evidence/Evo_Portable_Memory_Demo/` | Offline command reruns 12 assertions and compares saved package and restored state. Synthetic export only; no global deletion or identity-continuity claim |
| Supporting six recorded portability responses | `evidence/evo-pilot/portable-behavior-v1-prepared/`; `portable-behavior-v1-results/`; `prepare_portable_behavior.py`; `evidence/Evo_Portable_Memory_Demo/Behavior_Results.md` | Inspect all six responses for free, verify frozen prompts; regenerate inputs offline, not answers |
| Checker development demonstrations | Root checker tests and `examples/*.md` | Nine tests include four subprocess demonstration modes. Distinct from the six-fault and 64-execution research fixtures |

## Preserved model evidence versus regeneration

The API request bodies, recorded model identifiers, settings, responses, usage, timestamps and request identifiers are preserved as source records. They do not prove provider identity independently. The 12 context responses and six portability responses are separate batches; don't pool them into an accuracy statistic. The context batch has one response per condition/question, not repeated sampling or independent acquisition. Historical-answer judgments are interpretive; a Friday answer can be a plausible inference. No new scoring or independent adjudication was performed in packaging.

Regenerating answers would require an external service or a separate model implementation, potentially cost money and produce different answers. That activity is outside this supplement's reproduction commands and outside the current task. The historical API runner and budget/credential plumbing are intentionally excluded.

## Exactness and portability

Historical files preserve their original bytes. `MANIFEST_SHA256.json` verifies the distributed bytes, excluding itself. Legacy manifests are retained as historical evidence: request hashes were computed after universal-newline text reading; some comparison manifest keys use Windows backslashes. The current verifier handles the recorded request convention and uses the new cross-platform file inventory. It does not reinterpret historical hashes as external preregistration.

Six-fault replacement UUIDs vary between executions. Their values alone are normalized when comparing full records; all other trace fields are compared. SQLite binary files are omitted because their row contents are preserved in JSON and databases are recreated in temporary directories. Legacy hashes referring to those omitted databases remain archival references, not required files. The 64-execution comparison uses deterministic JSON and is checked exactly. Source records are never overwritten by reruns.

## Scope and concerns

- The core diagnostic compares exact values under a known scripted fault family. Correct localization is partly constructed; no prevalence, causal-root-cause or debugging-time claim follows.
- Ordinary logs use identical evidence and diagnosis rules, so ties are expected.
- The synthetic response stub can recover after earlier divergence; that is not evidence of real LLM behavior.
- Original Evo source and Springer class files are excluded. Nothing connects to, modifies or tests a live Evo deployment.
- Connector evidence remains trusted and unverified semantically. Passing raw-evidence presence checks is not proof that evidence supports the adapter's interpretation.
- The prior 162-file package had duplicate copies and successive checker example versions. This supplement selects one source copy per experiment. It is not an archive of every earlier exploratory pilot.

See [REVIEW_AND_REDACTIONS.md](REVIEW_AND_REDACTIONS.md), [PROVENANCE.json](PROVENANCE.json), and [LICENSE_SCOPE.md](LICENSE_SCOPE.md).
