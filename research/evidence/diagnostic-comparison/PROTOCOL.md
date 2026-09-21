# Diagnostic observability comparison — prospective local protocol

Status: development experiment, not independent validation. Saved before execution.
Question: Under a bounded executable fault model, what boundary evidence distinguishes the earliest observed divergence? Can recovery hide it from final-answer checking?

Execute two fictional old/new pairs across all 32 combinations of five switches: acquisition retains old value; storage skips commit; retrieval selects old record; response emits old value; retrieval recovery reads the authorized correction directly. Recovery takes priority over stale retrieval. This is a new synthetic SQLite adapter, not Evo and not an LLM. Reopen SQLite before reading storage. These combinations are a factorial census, not 64 independent samples.

Compare four observation policies: all four boundary values; acquisition/retrieval/response (storage missing); acquisition/storage/response (retrieval missing); response only. Compare structured JSON with ordinary timestamp-free stage=value lines containing identical fields. Both use the same exact-value rule; formatting alone is not expected to confer an information advantage.

Freeze the diagnostic: scan boundaries in order; an observed mismatch before any gap localizes that boundary; any preceding gap makes the result indeterminate; complete matching evidence yields no observed divergence. Do not jump across missing observations. Report correct localization, indeterminate results, incorrect definite claims, and cases with correct output despite earlier divergence. Separately group identical visible observations and count different first-divergence labels within each group, showing observational ambiguity under the enumerated fault family. Grouping uses labels retrospectively and is an analysis oracle, not a deployable diagnostic or accuracy baseline.

Ground truth is earliest mismatch in full executed boundary values, NOT injected software root cause. Masked faults, co-occurring faults and recovery mean these differ. Response is a deterministic stub, not language generation. Assumptions: trusted telemetry, a correct exact-value oracle, one user/key, binary old/new values. No semantic equivalence, unauthorized changes, corrupt logs, real conversations or human debugging-time claim. No held-out or blind claim; code and fault family are jointly authored. No API requests, no credentials, no spending.

Publish every execution and both successful and inconclusive outcomes. Preserve original paper and results. This study cannot establish superiority over existing research or production utility.
