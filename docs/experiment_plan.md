# Experiment Plan

> Defines the concrete experiments that answer the RQs, each config-driven and
> reproducible (CLAUDE.md Rule #3). Frozen at benchmark freeze.

## Datasets used (see `dataset_spec.md`)

- **Held-out custom set (PRIMARY evidence, contamination-free)** — the basis for
  the main RQ1/RQ2 claims and the only source of hallucination negative probes
  and difficulty labels (`heldout_spec.md`).
- **Public benchmarks (SECONDARY, labeled contamination-suspect):** RefCOCO
  (basic), RefCOCO+ (attribute), RefCOCOg (relational/complex), Visual Genome
  (relations/attributes, detection subset), Flickr30k Entities (multi-object,
  reference-only license).

## Experiment catalog

### E1a — Tier-A native-regime grounding (RQ1, RQ2, RQ5)
- **Vary:** model ∈ **Tier A** {Qwen2.5-VL-7B, Cosmos3-Nano-Reasoner}.
- **Regime:** **native** (each model's documented grounding interface; adapter
  converts native coords → canonical `xywh` abs-px).
- **Hold constant:** frozen inputs (held-out primary + public), decoding, seed,
  preprocessing.
- **Collect:** raw outputs → **Acc@0.5/0.75**, IoU dist., P/R/F1, parse-success,
  hallucination (on negative probes), latency, tokens/cost.
- **Analyses:** RQ1 Tier-A native accuracy (held-out primary; public labeled
  contamination-suspect); feeds RQ2 (the "native" arm) and RQ5 local/API frontier.

### E1b — Prompted-regime grounding, all five models (RQ2, RQ4, RQ5)
- **Vary:** model ∈ all five.
- **Regime:** **prompted** (single shared prompt; Tier-C boxes labeled
  prompt-induced).
- **Hold constant:** as E1a.
- **Collect:** same metric set, every box tier-labeled; parse-success reported
  separately from Acc@IoU.
- **Analyses:**
  - **RQ2:** E1a (native, Tier A) **vs** E1b (prompted) — native-vs-prompted
    contrast; primary metric **Acc@IoU** (not mAP).
  - **RQ4:** E1b restricted to **Llama 11B vs 90B** (the only valid scale pair;
    Tier-C, prompt-induced localization).
  - **RQ5:** latency/cost, **frontier-segregated** (local vs NIM-API).

### E2 — Prompt-complexity & robustness sweep (RQ3)
- **Vary:** prompt complexity tier L1→L4 + frozen paraphrases (`prompt_protocol.md`),
  per model, all five.
- **Hold constant:** images/targets, model, regime, decoding, seed.
- **Collect:** per-tier IoU/F1; within-model deltas across tiers; paraphrase
  variance.
- **Report:** within-model prompt sensitivity (comparable across all five as a
  *delta*); absolute per-tier level comparable only within Tier A. Distinct from
  raw capability (Rule #9).

### E3 — Difficulty stratification (RQ1 depth; held-out only)
- **Vary:** difficulty stratum (object-size bin, occlusion flag, scene clutter —
  labels from `heldout_spec.md`).
- **Models:** Tier A (accuracy) + all five (behavioral).
- **Collect:** Acc@IoU per stratum; degradation slope; small-box center-distance
  (since IoU is unstable for small boxes).

### E4 — Hallucination via negative probes (RQ1/RQ2 secondary; all five)
- **Vary:** referent presence (present vs **absent** negative probe).
- **Collect:** `hall_absent`, `hall_wrongbox`, correct-decline rate, parse-success
  (definitions in `metrics_spec.md`).
- **Note:** requires the held-out negative probes; not computable on public REC
  data (no absent-referent cases).

> All experiments share the same frozen inputs and the single deterministic
> evaluator; only the declared variable (and, for E1a/E1b, the **regime**) changes.

## Configuration-driven runs

Every run is defined by a committed config (Rule #3). Proposed schema:

```yaml
run_id: E1a_qwen25vl7b_native_2026-08-22
experiment_id: E1a
protocol_version: 1.0.0
model:
  id: qwen2.5-vl-7b
  tier: A                     # A (native) | C (prompt-induced)
  revision: "<pinned>"        # [⚠ verify]
  access: "<api|local>"       # [⚠ verify]
prompt:
  registry_version: 1.0.0
  regime: native              # native (Tier-A) | prompted (all)
  prompt_id: grounding.native.qwen.v1
data:
  split_manifest: data/splits/test_v1.json
  split_hash: "sha256:..."
decoding:
  temperature: 0
  seed: 0
output:
  raw_dir: results/raw_outputs/${run_id}
  metrics_dir: results/metrics/${run_id}
```

- Config + run manifest (see `benchmark_protocol.md`) together fully determine a run.
- Raw outputs and derived metrics are written to separate trees (Rules #4, #5).

## Statistical analysis plan

- **Uncertainty:** 95% bootstrap CIs on all headline metrics.
- **Model comparisons (RQ1/RQ2/RQ4):** paired bootstrap / permutation test over
  shared samples; correct for multiple comparisons (e.g., Holm–Bonferroni).
- **Prompt effect (RQ3):** within-model repeated-measures analysis across tiers.
- **Effect sizes** reported alongside p-values (not p-values alone).
- **Power analysis — per tier, not pooled:** the RQ1/RQ2 accuracy claim rests on
  the **two Tier-A models on the held-out set**, so power is computed for that
  comparison specifically. Working target N for the held-out set is **TBD from the
  power analysis** (order-of-magnitude planning figure ~200–500 images, pending
  that analysis — not a fixed decision). If power is insufficient, claims are
  scoped down honestly rather than overstated.
- **Contamination reporting:** every public-benchmark result is presented next to
  its held-out counterpart; the gap is reported, not hidden.

## Execution order

1. Freeze all protocols (see `benchmark_protocol.md` checklist).
2. Close remaining `[⚠ verify]`/TBD items in `model_matrix.md` (API determinism,
   pricing, Cosmos bbox key, Llama API coverage).
3. Build + IAA-verify the held-out set (`heldout_spec.md`); run power analysis.
4. Dry-run on small dev subset (parsing/format + coordinate-conversion sanity —
   not reported).
5. Run E1a, E1b, E2, E3, E4. Archive raw outputs immediately.
6. Compute metrics deterministically from raw. Generate figures (two RQ5 Pareto
   frontiers; held-out vs public panels).
7. Reviewer agent integrity pass (`../agents/reviewer_agent.md`).

## Reproducibility deliverables

- [ ] Committed run configs for every reported run.
- [ ] Pinned environment (lockfile) + `env_hash` in each manifest.
- [ ] Archived raw outputs with checksums.
- [ ] One-command re-computation of all metrics from raw outputs.
