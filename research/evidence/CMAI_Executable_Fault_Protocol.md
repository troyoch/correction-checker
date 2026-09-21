# Executable local fault check

Freeze before execution: two fictional corrections (Friday to Tuesday; prose to bullets), crossed with healthy operation, skipped correction commit, and obsolete-record retrieval. Six runs. No API calls. This tests the existing candidate evidence gate connected to a small SQLite adapter, not original full Evo.

For each run: commit the original record, present an authorized scripted correction to the existing gate, record its actual output, normally commit the resulting records, close and reopen the database, inspect the active stored record, then retrieve. The commit fault suppresses the update transaction. The retrieval fault selects the oldest row instead of the active row. Fault labels are not supplied to the diagnostic.

The diagnostic compares the expected correction with actual gate output, reopened active storage, and selected context. Report earliest divergence or indeterminate for missing/ambiguous evidence. Expected diagnoses: no observed divergence, storage, retrieval. Model response generation is not exercised and must not be scored as healthy. Input recognition is scripted; the acquisition-stage value means accepted gate output only.

Compare retrieval correctness alone against traced stage diagnosis. These are transparent development cases with single deliberately injected faults, not independent held-out validation or estimates of naturally occurring failure rates. Keep all runs and original candidate code unchanged.
