# Benchmark Protocol

> **This is the freeze document.** Per CLAUDE.md "Research Integrity", the
> protocol must be frozen before final evaluation. After freeze, changes require
> a version bump and re-run — not silent edits.

## Protocol version

`protocol_version: 0.1.0-draft` → bump to `1.0.0` at freeze.

## Pipeline (model-agnostic)

```
frozen inputs                 per-model adapter            deterministic eval
┌────────────────┐   image    ┌──────────────────┐  raw   ┌──────────────────┐
│ image + prompt │──+prompt──▶│ VLM inference    │──────▶│ parse → boxes    │
│ (frozen)       │            │ (via adapter)    │ output │ compute metrics  │
└────────────────┘            └──────────────────┘        └──────────────────┘
        │                             │                            │
   data/splits              results/raw_outputs           results/metrics
```

- **Inputs are frozen:** the (image, prompt, GT) triples come from a committed,
  hashed split manifest. Same inputs for every model (fairness).
- **Adapters are thin:** an adapter only (a) sends the frozen prompt+image to a
  model and (b) returns the raw response verbatim. It performs **no scoring**.
- **Raw ≠ derived:** raw model outputs are saved untouched (Rule #4) and stored
  separately from metrics (Rule #5). Metrics are recomputable from raw (Rule #7).

## What is held constant

| Factor | Setting | Rationale |
|--------|---------|-----------|
| Image set | frozen split | fair comparison |
| Prompt template | frozen per tier (`prompt_protocol.md`) | Rule #2, RQ3 control |
| Coordinate convention | `xywh` abs px (`dataset_spec.md`) | avoid IoU bugs |
| Decoding params | fixed per run, logged | reproducibility |
| Image preprocessing | fixed, scripted | reproducibility |
| Random seeds | fixed + recorded | reproducibility |

Only the **model** (E1) or the **prompt tier** (E2) varies; everything else is
held constant within an experiment.

## Output parsing & fairness

- Each model emits boxes in its own format; the adapter maps to the canonical
  schema. **Parsing rules are documented per model** in [`model_matrix.md`](model_matrix.md)
  and are part of the frozen protocol.
- **Parsing fairness:** a lenient/robust parser (tolerant of formatting quirks)
  is used uniformly so a model is not penalized for cosmetic output differences.
  Parse failures are recorded as such (not silently scored 0 without a flag).
- **Non-answers / refusals / "not present"** are recorded explicitly and feed the
  hallucination-rate and recall accounting (see [`metrics_spec.md`](metrics_spec.md)).

## Run manifest (captured for every run)

Every run writes a manifest under `results/raw_outputs/<run_id>/manifest.json`:

```json
{
  "run_id": "E1_qwen25vl7b_2026-08-22T...Z",
  "protocol_version": "1.0.0",
  "experiment_id": "E1",
  "model_id": "...",
  "model_version_or_revision": "...",         // [⚠ verify per provider]
  "prompt_registry_version": "...",
  "split_manifest_hash": "sha256:...",
  "decoding_params": {"temperature": 0, "...": "..."},
  "seed": 0,
  "env_hash": "sha256 of pinned env",
  "timestamp_utc": "...",
  "code_git_commit": "..."
}
```

## Determinism & reproducibility rules

1. Fixed seeds; greedy/temperature-0 decoding where the model supports it
   (**[⚠ verify per model]** — not all APIs are deterministic even at T=0).
2. Pinned environment (see [`../models/`](../models) and repo env files).
3. All headline metrics recomputable by re-running the eval on saved raw outputs.
4. No manual edits to raw outputs or metrics (Rules #4, #6).

## Freeze checklist (must all be ✅ before final eval)

- [ ] RQs/hypotheses frozen (`research_questions.md`)
- [ ] Dataset + license + splits frozen (`dataset_spec.md`)
- [ ] Annotations verified + IAA reported (`annotation_protocol.md`)
- [ ] Prompt registry frozen + versioned (`prompt_protocol.md`)
- [ ] Metric definitions frozen (`metrics_spec.md`)
- [ ] Model matrix capabilities **verified** (`model_matrix.md`)
- [ ] Environment pinned; run manifest schema implemented
- [ ] Power analysis done; target N met

Bump `protocol_version` to `1.0.0` and tag the git commit at freeze.
