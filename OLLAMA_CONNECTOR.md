# Experimental Ollama connector

This optional reference assistant connects Correction Checker to Ollama's chat endpoint. It does **not** connect to Evo, OpenAI, or an existing application's memory. No live model validation has been performed. Offline tests use scripted outputs or mocked transports, not recorded or generated model responses.

## Free offline smoke test

Requires Python 3.10+. From this branch's repository root:

```sh
python -m unittest discover -s . -p "test_*.py"
python checker.py --out runs/ollama-offline -- python ollama_adapter.py
```

Open `runs/ollama-offline/REPORT.md`. Expected outcome: passed, exit 0. This only verifies the reference fixture. Use a new output directory for every run. Offline mode makes no network requests, reads no credentials, and requires no model installation.

## Optional local inference, run by the developer

Install Ollama separately and provision a local model yourself. This connector never downloads models or starts servers. Configure the **Ollama server** with `OLLAMA_NO_CLOUD=1` and restart it, then verify your chosen model is local. Setting that variable only on the connector does not configure an already running server. See [Ollama's FAQ](https://docs.ollama.com/faq).

With a suitable local model already installed and serving on port 11434:

```sh
python checker.py --out runs/ollama-local -- python ollama_adapter.py --live --model llama3.2 --local-only-confirmed
```

Use your installed model's exact name. The confirmation flag is your attestation, not independent verification of server configuration. Cloud-tag names are rejected as an additional guard, but names alone cannot prove locality. Only use a trusted local Ollama server. There is no API key or hosted-service integration; local inference uses your hardware and electricity.

The connector posts non-streaming requests to `http://127.0.0.1:11434/api/chat`, following the [Ollama chat API](https://docs.ollama.com/api/chat). It disables environment proxies and redirects, makes no automatic retries, limits runs to five probe attempts by default, and requests at most 64 generated tokens per probe. The HTTP timeout is 40 seconds; slow cold starts may fail. A client timeout does not guarantee server computation has stopped. Failed attempts remain counted. No response regeneration was performed during development.

## What this actually tests

- Exact fixture parsing accepts Friday, then Tuesday. Acquisition is scripted, not model-based.
- SQLite stores current memory and a summary, reopened on each operation.
- Each probe supplies current memory and the possibly stale summary, with explicit precedence, to a stateless model call. No conversational history is carried over, even for the learning checkpoint.
- Restart means reopening the reference memory in a fresh adapter process. It **does not restart Ollama**, unload a model, clear server caches, or test a production lifecycle.
- Summary refresh deterministically copies the current value. It does not test AI summarization.
- Only the default schedule fixture is supported. Unsupported custom cases stop rather than pretending to work.

The answer is compared exactly after whitespace trimming. `Tuesday.` differs from `Tuesday`; inspect the raw response before interpreting a failure. Incomplete, length-truncated, empty, or tool-call responses are unavailable. A failed check returns exit 1; missing evidence without a scored failure returns exit 2. A pass establishes only this reference assistant's behavior for this case, not general Llama memory reliability.

## Connecting your own memory system

Replace the teach/correct, SQLite storage, retrieval, restart, and summary operations with calls to your actual application under the existing [adapter contract](ADAPTER_CONTRACT.md). Preserve raw evidence and report unavailable checkpoints honestly. Never label a reference-store test as a test of your production memory. Avoid sharing runs until you have reviewed them for private data.

This extension is separate from the submitted paper and archived research results. The new connector, tests, and this guide use the repository's MIT license; model weights retain their own licenses.

