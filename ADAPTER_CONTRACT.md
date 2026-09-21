# Adapter contract v1

The checker invokes a trusted local command with shell=False, supplies one JSON request on stdin, and expects one JSON object on stdout. Diagnostics go to stderr. There is a 60-second operation timeout. A nonzero exit, invalid JSON or wrong schema stops the run and preserves partial events. No retry occurs. stdout/stderr are recorded: never print keys or authorization headers.

Every request includes schema="correction-check/1", operation, namespace, state_dir. Use the namespace to isolate data; don't point the tool at a real user's memory. state_dir is a disposable local test directory. The adapter must not destroy data outside it.

Operations:
- capabilities: return isolated_test_namespace=true only if implemented. Include architecture/version/scope and unsupported operations.
- teach: session and text. Run the actual assistant's learning path.
- correct: session and text. Run actual correction acquisition; return observations.accepted with the captured canonical value, its source and ideally raw acquisition record.
- probe: session and question. Reuse session only for the learning conversation; other IDs are new conversations. Return observations.storage (durably read), retrieval (effective target value in supplied context), answer (canonicalized actual response). Include raw_context and raw_output. If context contains conflicting values that cannot be unambiguously canonicalized, mark retrieval unavailable with a reason; do not quietly pick the expected value. Full prompts and model settings should be attached for reproducibility, excluding secrets.
- restart: restart the actual owned backend or return status="unavailable" and reason. Connector launch alone is not backend restart. Include lifecycle evidence describing what restarted and what state persisted.
- refresh_summary: execute the real summary refresh or return unavailable with reason. Don't synthesize the expected new summary just to pass.

Every reply: schema="correction-check/1", status="completed" or unavailable. For probe and acquisition observations:

```
{"status":"observed","value":"Tuesday","source":"reopened memory row id=123","raw_record":{"day":"Tuesday"}}
```

When unavailable:

```
{"status":"unavailable","reason":"Backend does not expose durable state"}
```

The checker retains the acquisition observation from correction and combines it with each later probe. This does not imply acquisition is rerun at every checkpoint. Sources are adapter declarations, not cryptographic attestations. This first version has no independent semantic grader, timing study, authentication check or cost enforcement. Future adapters need provider-specific budget controls before paid runs.

## v0.2 evidence and status requirements

Non-completed top-level status suppresses every observation even if stale values are present. For inspectable evidence attach raw_record for acquisition/storage, raw_context for retrieval, and raw_output for answer. Empty evidence does not qualify. A source label alone is connector_report_only and cannot yield an overall passed outcome. Evidence presence does not prove authenticity or validate canonicalization. Overall failed means at least one reported value mismatch; inconclusive covers gaps and absent raw evidence. Existing integrations must expect nonzero exits for failures and incomplete evidence.
