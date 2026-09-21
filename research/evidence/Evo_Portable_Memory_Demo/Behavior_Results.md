# Restored memory: natural-language behavior check

Six independent API requests using gpt-5.6-luna completed. Three received the exact text in restored-memory.txt; three received no saved memory. Questions and scoring criteria were frozen beforehand. No conversation continuation or tools were used.

| Question | With restored memory | Without memory |
|---|---|---|
| Concert suitable for Rowan | “A quiet concert would suit Rowan best.” | Did not know Rowan's preferences |
| Current project | “Rowan is building a miniature observatory.” | “I don’t know.” |
| Exact private note | Said the note was not provided | Said no saved memory contained the note |

Manual inspection against the predefined criteria found all six responses consistent with expectations. This inspection was not blinded or independently scored. The restored context carried the corrected preference and selected project detail; no request included the excluded note's text. The model did not invent that text.

This completes a small local export → fresh-process restore → model-response demonstration. It is not live Evo, a general privacy guarantee, deletion from previous storage, a test of identity, or a novel scientific finding. There is one fictional user and one response per condition/question, with explicit instructions to acknowledge missing information.

Batch usage: 467 input tokens and 98 output tokens. Estimated cost $0.000211 at previously checked rates, not an invoice. Combined conservative reservations now $2.96 of the authorized $4 ceiling. No retries.

Frozen requests and protocol are in the workspace's evo-pilot/portable-behavior-v1-prepared folder. Raw requests, responses, usage and request IDs are included here in behavior-evidence. The shared archive contains only fictional test data and no API credentials.
