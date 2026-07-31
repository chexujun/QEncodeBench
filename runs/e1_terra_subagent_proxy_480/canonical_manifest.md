# Canonical response manifest

The canonical identity of frozen instance `i` is its zero-based line number in
`data/frozen_v1/instances.jsonl` and the `task_id` stored on that same line.
Its only valid raw-response filename is:

`responses/{i:03d}_{task_id}.md`

Artifacts with a different prefix, task ID, or suffix are not eligible
for scoring.  Generation schedulers must load one
instance object and derive both the solver prompt and this filename from that
object.  Canonical coverage is computed by exact filename match against the
480 frozen instances; it must not be inferred from raw file count or verifier
row count.
