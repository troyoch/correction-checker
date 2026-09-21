# Correction Checker

Experimental, provider-independent developer tooling for checking whether a correction persists across conversations. Version **0.2.1**.

**Implemented:** a local adapter interface, configurable single durable corrections, checkpoint reports, evidence files, and passed/failed/inconclusive exit codes.

**Not established:** compatibility with every AI system, a complete Evo integration, production reliability, independent validation, or faster human debugging. The bundled assistant is a deterministic SQLite demonstration, not an AI model. A developer must write a connector for a real system. Systems without persistent memory require a suitable test design; this tool does not certify chatbot quality.

## Run locally

Requires Python 3.10 or newer. No third-party packages or API key are required for demonstrations. Download this repository, open a terminal in its folder, and run:

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

Exit codes: **0 passed**, **1 failed**, **2 inconclusive**. The failure demonstrations intentionally return nonzero. Execution status “completed” is distinct from the test outcome. Reports for all four modes are in [examples](examples).

## Connect your assistant

See [the adapter contract](ADAPTER_CONTRACT.md). The checker invokes your command with one JSON request per process. Operations are capabilities, teach, correct, probe, restart, and refresh_summary. Use an isolated synthetic test namespace. It must call your actual system rather than fabricate expected observations.

```sh
python checker.py --out runs/custom --case example-case.json -- python your_adapter.py
```

The example custom case tests a prose-to-bullets preference. The bundled demo parser supports only the default schedule fixture; it cannot run arbitrary cases. Temporary exceptions and repeated-correction histories are not supported yet.

## Optional Ollama reference connector

See [the Ollama connector guide](OLLAMA_CONNECTOR.md) for an offline smoke test and opt-in local inference. It uses its own demonstration SQLite memory, not Evo or your existing application's memory. Live model compatibility remains unvalidated; offline checks generate no model responses. This extension adds no results to the paper.

## What gets checked

Teach an initial value, establish a baseline, correct the value, and probe the learning conversation, a fresh conversation, after restart, and after summary refresh. Probe questions contain neither candidate answer in the supplied default case. Custom question leakage is the case author's responsibility. Later checkpoints include earlier interventions; this is not an isolated causal ablation.

The report distinguishes accepted, saved, retrieved, and answered values. Missing checkpoints remain unverified. Unavailable replies cannot earn passes from leftover observations. Connector-only claims are explicitly labeled and cannot produce an overall pass without raw evidence. Attached evidence remains adapter-supplied: presence does not verify authenticity or interpretation. Manually inspect actual records, context, and answers for a real integration.

Fresh connector processes do not prove that a remote backend restarted or forgot its session. Those operations are the adapter's responsibility. Earliest observed divergence is not proof of software root cause. Exact-value scoring does not independently evaluate semantics.

## Evidence and privacy

Each run saves its plan, requests/replies, results, report and hashes. Hashes detect later byte changes, not independent preregistration. External adapters may incur charges; the core has no provider budget control. Never print credentials into adapter output. Use fictional data and review logs before sharing them. The demonstration is entirely local and free of API calls.

## Research status

This tool accompanies the draft *Tracing Corrections Through AI Companion Memory* by Troy Ochowicz. Scripted demonstrations are engineering checks, not natural failures discovered in a complete assistant. A real-system pilot and independent developer evaluation remain future work. No peer-review acceptance is claimed.

## License and contribution

New code and documentation in this repository are MIT licensed. No Evo source code or private conversations are included. To contribute a connector, document actual reset behavior, unavailable evidence, cost controls, synthetic test results and limitations. Do not claim universal compatibility from interface support alone.
