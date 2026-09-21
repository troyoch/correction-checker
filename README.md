# Correction Checker

Experimental, provider-independent developer tooling for checking whether a correction persists across conversations. Version **0.2.1**.

**Implemented:** a local adapter interface, configurable single durable corrections, checkpoint reports, evidence files, and passed/failed/inconclusive exit codes.

**Not established:** compatibility with every AI system, a complete Evo integration, production reliability, independent validation, or faster human debugging. The bundled assistant is a deterministic SQLite demonstration, not an AI model. A developer must write a connector for a real system. Systems without persistent memory require a suitable test design; this tool does not certify chatbot quality.

## Run locally

Requires Python 3.10 or newer. No third-party packages or API key are required for demonstrations. Download the [v0.2.1 source ZIP](https://github.com/troyoch/correction-checker/archive/refs/tags/v0.2.1.zip) for the unchanged checker release, or use **Code > Download ZIP** on this branch for the proposed research supplement. Extract the ZIP, open a terminal in the extracted folder (the one containing checker.py), and run:

```sh
python -m unittest discover -s . -p "test_*.py"
python checker.py --out runs/healthy -- python demo_adapter.py healthy
```

Open `runs/healthy/REPORT.md`. Every run needs a new output directory. Other demonstration modes:

```sh
python checker.py --out runs/save-fault -- python demo_adapter.py skip_save
python checker.py --out runs/summary-fault -- python demo_adapter.py stale_summary
python checker.py --out runs/missing -- python demo_adapter.py missing_storage
```

Exit codes: **0 passed**, **1 failed**, **2 inconclusive**. The failure demonstrations intentionally return nonzero. Execution status “completed” is distinct from the test outcome. See the [healthy sample report](examples/healthy.md) and [all four reports](examples). Expected outcomes are healthy=passed, skip_save=failed, stale_summary=failed, missing_storage=inconclusive.

## Connect your assistant

See [the adapter contract](ADAPTER_CONTRACT.md). The checker invokes your command with one JSON request per process. Operations are capabilities, teach, correct, probe, restart, and refresh_summary. Use an isolated synthetic test namespace. It must call your actual system rather than fabricate expected observations.

```sh
python checker.py --out runs/custom --case example-case.json -- python your_adapter.py
```

The example custom case tests a prose-to-bullets preference. The bundled demo parser supports only the default schedule fixture; it cannot run arbitrary cases. Temporary exceptions and repeated-correction histories are not supported yet.

## What gets checked

Teach an initial value, establish a baseline, correct the value, and probe the learning conversation, a fresh conversation, after restart, and after summary refresh. Probe questions contain neither candidate answer in the supplied default case. Custom question leakage is the case author's responsibility. Later checkpoints include earlier interventions; this is not an isolated causal ablation.

The report distinguishes accepted, saved, retrieved, and answered values. Missing checkpoints remain unverified. Unavailable replies cannot earn passes from leftover observations. Connector-only claims are explicitly labeled and cannot produce an overall pass without raw evidence. Attached evidence remains adapter-supplied: presence does not verify authenticity or interpretation. Manually inspect actual records, context, and answers for a real integration.

Fresh connector processes do not prove that a remote backend restarted or forgot its session. Those operations are the adapter's responsibility. Earliest observed divergence is not proof of software root cause. Exact-value scoring does not independently evaluate semantics.

## Evidence and privacy

Each run saves its plan, requests/replies, results, report and hashes. Hashes detect later byte changes, not independent preregistration. External adapters may incur charges; the core has no provider budget control. Never print credentials into adapter output. Use fictional data and review logs before sharing them. The demonstration is entirely local and free of API calls.

## Research status

This tool accompanies the draft *Tracing Corrections Through AI Companion Memory* by Troy Ochowicz. Scripted demonstrations are engineering checks, not natural failures discovered in a complete assistant. A real-system pilot and independent developer evaluation remain future work. No peer-review acceptance is claimed.

## License and contribution

The checker and its developer documentation are MIT licensed. Historical research materials and the manuscript are excluded from that blanket license; see [license scope](research/LICENSE_SCOPE.md). No Evo source code or private conversations are included. To contribute a connector, document actual reset behavior, unavailable evidence, cost controls, synthetic test results and limitations. Do not claim universal compatibility from interface support alone.

## Research supplement (proposed)

Start with the [research-evidence guide](research/README.md) for the table-to-file map, preserved model responses, privacy review and offline reproduction commands. The nine checker tests do not reproduce every paper experiment.

```sh
python research/verify.py
python research/verify.py --offline
```

The first verifies recorded evidence; the second also reruns the applicable synthetic research checks in temporary directories. Neither calls a model. A research-supplement release is being prepared as a **draft**, not a published release. The existing v0.2.1 tag is unchanged. See [CONTRIBUTING.md](CONTRIBUTING.md) to propose a connector; no paid integration is included.
