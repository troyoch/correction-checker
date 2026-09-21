# Packaging verification

Performed from a clean temporary copy using Python 3.12 on Windows. No paid API, credentials, model generation, live Evo connection or modification.

- `python -m unittest discover -s . -p "test_*.py"`: nine tests passed, including four demonstration modes.
- `python research/verify.py --offline`: 64 distributed-file checksums verified; 12 context and six portable recorded responses verified against saved prompts; six original synthetic fault executions reproduced (generated UUIDs normalized); 64 comparison executions and summaries matched exactly; 12 portable assertions passed; 18 request inputs regenerated identically under the historical newline convention.
- Existing checker and historical scientific/scoring code are unchanged. CI runs both commands independently on Windows and Ubuntu with Python 3.10 and 3.12; hosted CI outcomes should be checked on the PR, not inferred from this local run.
- Synthetic responses are scripted. Recorded API outputs were inspected, not regenerated. No independent validation or real-system compatibility is established.
- Original records are untouched. One personal-budget sentence in a copied narrative was redacted and logged; source hashes and new distributed hashes are available.

Known limits: historical UUID generation prevents raw-byte identity of regenerated six-fault files; original context-construction code remains private; no semantic or human-adjudication study was added. Generated results stay in temporary directories outside the source tree.
