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

### E1a — Native-regime localization (RQ1, RQ2, RQ5)
Two native **conditions**, each scored in **its own metric family** (never merged):
- **Qwen-native-bbox** — Qwen2.5-VL-7B, native `bbox_2d` → **BBox family**
  (Acc@IoU, IoU).
- **Cosmos-native-point** — Cosmos3-Nano-Reasoner, native `point_2d` (0–1000) →
  **Point family** (point-in-GT-box accuracy, normalized point error). **Not IoU;
  not a box.**
- **Regime:** **native** (each condition's documented interface; adapter converts
  to the family canonical schema).
- **Hold constant:** frozen inputs (held-out primary + public), decoding, seed,
  preprocessing.
- **Collect:** per-family accuracy, parse-success, hallucination (negative probes),
  latency, tokens/cost.
- **Analyses:** RQ1 native accuracy **reported per primitive/family, not combined
  into one ranking** (held-out primary; public labeled contamination-suspect);
  feeds RQ2 (native arm) and RQ5 local/API frontier.

### E1b — Prompted-regime bbox localization, all five models (RQ2, RQ4, RQ5)
- **Vary:** model ∈ all five; every condition emits a **prompt-induced bounding
  box** → **BBox family**. Includes **Cosmos-prompted-bbox** (labeled
  prompt-induced; **never** native bbox).
- **Regime:** **prompted** (single shared bbox prompt).
- **Hold constant:** as E1a.
- **Collect:** Acc@IoU, IoU, parse-success (reported separately), hallucination.
  Every box labeled with its condition + prompt-induced flag.
- **Analyses:**
  - **RQ2 (bbox contrast, H2.1):** **Qwen native bbox** (from E1a) **vs**
    prompt-induced boxes in E1b (Cosmos-prompted-bbox, Llama×2, Nemotron) —
    primary metric **Acc@IoU** (not mAP).
  - **RQ2 (within-Cosmos, H2.2):** Cosmos-native-point (E1a, point metric) vs
    Cosmos-prompted-bbox (E1b, bbox metric) — reported as native-vs-prompted
    within one model, **explicitly non-metric-identical**.
  - **RQ4:** E1b restricted to **Llama 11B vs 90B** (only valid scale pair;
    prompt-induced bbox localization).
  - **RQ5:** latency/cost, **frontier-segregated** (local vs NIM-API).

> **No new top-level experiment ID is introduced.** The two Cosmos conditions map
> onto existing experiments: **Cosmos-native-point ⊂ E1a**, **Cosmos-prompted-bbox
> ⊂ E1b**. They are named conditions, tracked via the `condition` config field, so
> the study design is preserved rather than expanded.

### E2 — Prompt-complexity & robustness sweep (RQ3)
- **Vary:** prompt complexity tier L1→L4 + frozen paraphrases (`prompt_protocol.md`),
  per model, all five.
- **Hold constant:** images/targets, model, regime, decoding, seed.
- **Collect:** per-tier IoU/F1; within-model deltas across tiers; paraphrase
  variance.
- **Report:** within-model prompt sensitivity (comparable across all five as a
  *delta*); absolute per-tier level comparable only **within a shared metric
  family** (bbox vs point never merged). Distinct from raw capability (Rule #9).

### E3 — Difficulty stratification (RQ1 depth; held-out only)
- **Vary:** difficulty stratum (object-size bin, occlusion flag, scene clutter —
  labels from `heldout_spec.md`).
- **Conditions:** native conditions for accuracy (Qwen-native-bbox → Acc@IoU per
  stratum; **Cosmos-native-point → point-in-GT-box acc / center-distance per
  stratum**) + all five (behavioral).
- **Collect:** per-family accuracy per stratum; degradation slope. Point
  localization is size-robust where box IoU is not — report both accordingly.

### E4 — Hallucination via negative probes (RQ1/RQ2 secondary; all five)
- **Vary:** referent presence (present vs **absent** negative probe).
- **Collect:** `hall_absent` (box **or** point returned instead of `NOT_PRESENT`),
  `hall_wrongbox` (bbox conditions) / `hall_wrongpoint` (Cosmos-native-point),
  correct-decline rate, parse-success (definitions in `metrics_spec.md`), reported
  per family.
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
  class: A-bbox               # A-bbox | A-point | C
  revision: "<pinned>"        # [⚠ verify]
  access: "<api|local>"       # [⚠ verify]
condition: Qwen-native-bbox   # Qwen-native-bbox | Cosmos-native-point | Cosmos-prompted-bbox | <model>-prompted-bbox
metric_family: bbox           # bbox | point
prompt:
  registry_version: 1.0.0
  regime: native              # native (native conditions) | prompted (all, bbox)
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
- **Power analysis — per metric family, not pooled:** the RQ1/RQ2 accuracy claims
  rest on the **native conditions on the held-out set**, computed **within each
  metric family** — the bbox contrast (Qwen native bbox vs prompt-induced boxes)
  and the point condition (Cosmos-native-point) — never as a single Qwen-vs-Cosmos
  cross-family comparison. Working target N for the held-out set is **TBD from the
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
