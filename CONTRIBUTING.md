# Contributing a connector

1. Read ADAPTER_CONTRACT.md and identify which actual operations your system exposes. Report unsupported operations or missing evidence explicitly. A new connector process is not proof of backend restart.
2. Use a separate synthetic test namespace. Implement the six operations against actual acquisition, storage, retrieval, summaries and response paths; do not insert expected answers into observations.
3. Keep authentication outside recorded output. Explain session isolation, reset behavior, canonicalization and raw-evidence provenance. Never commit real conversations or credentials.
4. Validate locally with a small declared case and inspect raw memory/context/answers manually. Keep successes, failures and inconclusive cases. Mark injected faults clearly. Include version and dependencies. Do not claim support for an untested provider.
5. Submit a pull request with setup instructions and observed limitations. Paid integrations require explicit cost controls and user authorization; the project does not authorize API spending by accepting a contribution.

Run the checker tests with `python -m unittest discover -s . -p "test_*.py"`. Changes affecting packaging should also pass `python research/verify.py --offline`. Keep generated runs under ignored `runs/` or temporary directories. Do not alter historical records or scoring to obtain a pass: report scientific concerns and propose a separate prospective change.

The current core only handles single durable exact-value corrections. Temporary exceptions, repeated corrections and evidence interpretation require additional design. Demonstrations are scripted; independent usefulness evaluation and real-system validation remain future work.
