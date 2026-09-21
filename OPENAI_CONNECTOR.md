# Experimental OpenAI connector preview

Local development preview, separate from the submitted paper and published Zenodo evidence. No live API test has been performed. MIT licensed; see LICENSE.

## Free offline smoke test

Requires Python 3.10+; no dependencies or credentials.

```sh
python -m unittest discover -s . -p "test_*.py"
python checker.py --out runs/offline-example -- python openai_adapter.py
```

The output directory must not exist. `REPORT.md`, `events.json` and `result.json` are saved there. The checker exits 1 (`failed`) for the built-in fixture: the fresh baseline and fresh corrected probes answer UNKNOWN, because those sessions have no history. The learning session answers Tuesday. This is an intentional negative control, not evidence of a defect in OpenAI memory. Storage, retrieval and accepted-correction evidence are unavailable; restart and summary refresh are not run. The smoke response is scripted, not an AI response. Use only the included Friday-to-Tuesday case in offline mode.

## Optional live mode (developer-operated, costs money)

Developers supply their own OPENAI_API_KEY environment variable locally, using their own secure setup. No keys are collected by TroyMaya, and no env files are loaded automatically. Do not put credentials in command-line arguments or share run directories containing private prompts.

```sh
python checker.py --out runs/my-live-test -- python openai_adapter.py --live --model YOUR_MODEL --max-requests 5 --max-output-tokens 128 --max-input-bytes 12000 --budget 0.50 --reservation 0.10
```

The dollar numbers above are illustrative reservation settings, NOT a verified price quote. Determine a conservative per-request reservation using the selected model's current pricing and input/output limits before live use. The connector enforces request, input-byte and output-token limits and a persistent reservation ledger. It cannot guarantee an actual billing ceiling: incorrect pricing/reservations, tokenizer overhead, or other activity in the project can exceed your dollar expectation. Errors/timeouts retain reservations and are never automatically retried. Each run has its own budget; do not share a state directory between concurrent processes. Starting a new run starts a new ledger.

The endpoint is fixed to https://api.openai.com/v1/responses; redirects are refused. `store=false` is used, with explicit client-managed session transcripts. This does not promise zero provider retention. Raw prompts, responses and provider usage are included in events for inspection. Failures omit provider error text to avoid leaking sensitive data.

## What it tests

This is an API conversation/response adapter, NOT automatic connection to an existing OpenAI project's application memory, ChatGPT history, vector store, or Evo. It provides no cross-session memory. A fresh session sends only the probe and fixed instructions. Do not describe failure there as failed persistence of an existing assistant. A correct answer in an empty session is also not proof of memory transfer.

Answers are compared as exact stripped text; there is no semantic grader. Refusals, paraphrases and longer answers need human inspection. Acquisition, durable memory and retrieval remain unavailable rather than being inferred from fluent answers. To test your real assistant, implement the checker adapter contract against its actual learning, storage and retrieval paths. This preview supplies a transport starting point only.

## Verification and publication boundaries

The existing nine checker tests plus eight connector tests exercise offline behavior, isolation, budget exhaustion, failure reservations, incomplete responses, input limits, and payload construction using test doubles. They do not establish live compatibility or produce new research results. No Evo files or historical evidence were changed. Existing GitHub and Zenodo releases remain unchanged.

API schema reference, consulted September 21, 2026:
https://developers.openai.com/api/reference/python/resources/responses/methods/create
