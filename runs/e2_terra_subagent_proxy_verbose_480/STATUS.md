# Status: complete — canonical verbose rerun

All 480 inputs are rendered with `build_prompt(inst, "verbose")`; each is
stored under `prompts/` with its SHA-256 in `prompt_manifest.jsonl`.

Prompt-delivery mismatches are treated as infrastructure failures, never as
model failures. Index 009's first delivery omitted three toy-example comments,
and indices 142/143 had formatting-compacted deliveries. Their raw replies were
quarantined under
`attempts/transport_mismatch/`; fresh exact-prompt solver runs produced the
canonical responses. Index 445 had two pre-response transcription mismatches
that were interrupted before a response was accepted. Index 295 had an
incorrectly configured first attempt that was also interrupted before output;
its canonical retry used no model or reasoning override.

The complete canonical response set is under `responses/` (480/480). The final
verification artifact is `verification_final_canonical_retry.jsonl`.

Final verified results (480 verified, 0 infrastructure failures):

- L1: 477/480
- L2: 460/477
- L3: 396/460
- L4: 385/396
- L4 end-to-end: 385/480

The initial eight-worker verification encountered 48 OpenMP shared-memory
infrastructure failures. Those entries were retried with two workers and merged
into the final artifact; model failures from the successful first pass were not
rerun.

Historical note: index 009's rejected first reply is at
`attempts/transport_mismatch/009_3sat-T1-s0009_attempt1_omitted_toy_comments.md`
and the rejected 142/143 replies are retained in the same directory.

The manifest records the intended prompt bytes and parameters;
platform-level byte capture of the dispatch transport is unavailable.
