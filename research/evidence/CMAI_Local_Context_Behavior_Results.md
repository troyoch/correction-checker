# Local context-path behavior pilot

Twelve completed independent gpt-5.6-luna requests: four saved contexts by three probes, one draw per cell. This is a separate supplied-context diagnostic, not execution of CMAI v0.2 on complete Evo. The contexts came from the transcribed original PHP context function with synthetic adapters and planted memory records. Questions and interpretation criteria were frozen before collection.

| Supplied sources | Current schedule answer | Original schedule answer | Old-Friday-note response |
|---|---|---|---|
| Stale summary + corrected record | Tuesday | Friday, stated definitively | Keep Tuesday; old note outdated |
| Corrected record only | Tuesday | Original day unspecified | Keep Tuesday |
| Stale summary only | Friday | Friday, stated definitively | Keep Friday unless newer evidence |
| Neither | Unspecified | Unknown | Verify what the note refers to |

## Interpretation

Withholding the corrected record changed the current-schedule answer from Tuesday to Friday when the stale summary remained. This is grounded in the information then available to the model, but inconsistent with the external fixture's latest correction. Removing both inputs yielded uncertainty. The intact context did not produce an incorrect current-schedule answer in this draw: the wording "now sent Tuesday" gave a temporal cue. Do not describe this as a universal contradiction-induced failure or proof the intact implementation is defective.

There is also a provenance issue: both summary-containing conditions asserted that Friday was the original schedule. Their summary merely says reports are sent Friday; it does not explicitly identify an original date. Friday matches our external fixture history, but the model's certainty exceeds the chronology established by its supplied evidence. In the combined context this is a plausible inference; in the summary-only context current information was promoted to original-history status. Under the frozen criteria these are unqualified historical inferences, not wrong-day answers. The corrected-record-only condition correctly acknowledged that the original day was missing.

All 12 outputs are preserved, including the empty-context conflict answer that could not even identify what the old note concerned. No aggregate pass percentage is used: available-evidence groundedness, external correction retention, and historical provenance are distinct measures. Assessment was manual by the designing assistant, not independent or blinded.

## Limits and useful next step

One synthetic schedule and one draw per cell cannot establish reliability, novelty, or live Evo behavior. The inputs deliberately differ in information. No acquisition, full Evo prompts, automatic curation, complete retrieval helper, or repair comparison was tested. The global-off condition was omitted because its observed empty context duplicates the neither condition for these requests.

A future versioned-memory comparison should preserve explicit old/current status and source links, rather than force a choice between erasing history and keeping an ambiguous summary. It needs multiple new cases and a prospectively fixed comparison; this pilot alone does not validate such a repair. Preserve this result without launching more repetitions merely to seek surprise.

## Evidence and budget

Frozen messages, criteria and source hash: evo-pilot/context-path-v1-prepared. Exact requests, raw responses, request IDs, usage and extracted answers: evo-pilot/context-path-v1-results. All twelve completed without retry. [Personal shared-account budget details omitted from this public copy.] No website changes, publication or external messages.
