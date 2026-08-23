# Model Matrix

> **Status:** Capabilities **verified** against primary sources (Aug 2026). This
> replaces the earlier all-`[⚠ verify]` draft. Every capability below carries an
> evidence tag; values still unknown are marked **TBD**. Per CLAUDE.md we do
> **not** invent capabilities, sizes, or licenses.

## Capability tiers (the organizing distinction for the whole benchmark)

The benchmark is a **native-vs-prompted grounding study**. Models are classified
by *how* they produce coordinates, not merely by *whether* they can:

- **Tier A — native/documented grounding.** The vendor documents a bounding-box
  (or point) output format. Coordinates are a first-class model capability.
- **Tier B — visual localization/reasoning without a documented bbox output.**
  The model can reason about *where* things are, but the vendor documents no box
  format.
- **Tier C — prompt-induced coordinates.** Any box the model emits exists only
  because the prompt asked for one; it is not a documented capability.

> **Rule (integrity):** A Tier-C coordinate is **never** described as "native
> grounding" anywhere in this benchmark. B/C-tier boxes are always labeled
> *prompt-induced*. See CLAUDE.md Rule #9 (capability vs prompt engineering).

## Verified model table

| Model | Params (verified) | Access | Native bbox output? | Coordinate format | Structured JSON | **Grounding tier** | License |
|-------|-------------------|--------|---------------------|-------------------|-----------------|--------------------|---------|
| **Qwen2.5-VL-7B-Instruct** | ~7B dense **[Verified]** | Local **[Verified, Apache-2.0]** + hosted API (Alibaba DashScope) **[Verified]** | **Yes** — `bbox_2d` **[Verified]** | **Absolute pixels, `xyxy`**, origin top-left **[Verified]** | **Yes** — documented stable JSON coords **[Verified]** | **A (native)** | Apache-2.0 **[Verified]** |
| **Cosmos3-Nano-Reasoner** | 16B total; **8B dense backbone** (Mixture-of-Transformers, adapts Qwen3-VL 8B arch) **[Verified]** | NVIDIA NIM API **[Verified]** + local weights (`nvidia/Cosmos3-Nano`) **[Verified]** | **Yes** — box + `point_2d` **[Verified]**; exact **bbox JSON key = TBD** (only `point_2d` confirmed verbatim) | **Normalized 0–1000 per axis**, origin top-left, unified JSON **[Verified]** | **Yes** **[Verified]** | **A (native)** | OpenMDW-1.1 (HF card) **[Verified]**; NIM-endpoint terms **TBD** |
| **Llama 3.2 11B Vision** | **10.6B** dense **[Verified]** | Local (gated HF weights) **[Verified]** + hosted API coverage **[⚠ verify]** | **No documented bbox format** **[Verified]**; grounding named only as a *use case*; **text-out only** | none documented → any box is **prompt-induced** | Not documented **[Verified]** | **B** (localization ability); **bbox = C** | Llama 3.2 Community License **[Verified]** |
| **Llama 3.2 90B Vision** | **88.8B** dense **[Verified]** | Local (multi-GPU) **[Verified]** + hosted API coverage **[⚠ verify]** | Same as 11B **[Verified]** | none documented → **prompt-induced** | Not documented **[Verified]** | **B** (localization ability); **bbox = C** | Llama 3.2 Community License **[Verified]** |
| **Nemotron 3 Nano Omni** | **30B-A3B MoE (~3B active/token)** **[Verified]** | NVIDIA NIM API **[Verified]** + local (HF weights) + AWS SageMaker JumpStart **[Verified]** | **No documented grounding/bbox** **[Verified]**; OCR/GUI focus | none documented → **prompt-induced**. JSON output *is* supported, but **not documented for coordinates** | JSON yes; **coords: not documented** **[Verified]** | **B→C** | NVIDIA Open Model Agreement **[Verified]** |

**Tier assignment for the study:** **Tier A = {Qwen2.5-VL-7B, Cosmos3-Nano-Reasoner}.**
**Tier C (prompt-induced bbox) = {Llama 3.2 11B, Llama 3.2 90B, Nemotron 3 Nano Omni}.**
(The three C models retain Tier-B *localization ability*; only their *bounding-box
output* is Tier C.)

## Per-model coordinate handling (drives the evaluation adapter)

The evaluation layer converts every model's raw output to the canonical internal
schema (`xywh`, absolute pixels, origin top-left — see
[`dataset_spec.md`](dataset_spec.md) and [`metrics_spec.md`](metrics_spec.md)).
Conversion is per-model and **must be unit-tested against known boxes** before any
reported run (a top source of silent IoU bugs).

| Model | Raw form | Conversion to canonical `xywh` abs-px |
|-------|----------|----------------------------------------|
| Qwen2.5-VL-7B | `bbox_2d = [x1,y1,x2,y2]` abs px | `w=x2−x1, h=y2−y1` (already absolute) |
| Cosmos3-Nano-Reasoner | box/point normalized 0–1000 | multiply by `(W/1000, H/1000)` using the **post-preprocessing** image W,H; then `xyxy→xywh` |
| Llama 11B / 90B | free-text (prompt-induced) | robust parse → whatever numeric convention the model emitted; **flag parse failures**; label prompt-induced |
| Nemotron 3 Nano Omni | JSON/free-text (prompt-induced) | robust parse; **flag parse failures**; label prompt-induced |

> The **prompt regime** differs by tier (native elicitation for A, shared prompted
> regime for all) — see [`prompt_protocol.md`](prompt_protocol.md). A-tier models
> emit their **native** format and the adapter converts; they are never instructed
> to emit a foreign format (doing so would collapse Tier A into Tier C).

## RQ dependencies on this table

- **RQ1 (Tier-A native accuracy):** headline accuracy claims restricted to
  Tier A. C-tier numbers are reported, but labeled *prompt-induced*.
- **RQ2 (native vs prompt-induced):** A-vs-C contrast. Primary metric is
  **Acc@IoU**, **not** mAP (see [`metrics_spec.md`](metrics_spec.md)).
- **RQ3 (prompt complexity):** within-model across all five; comparable in
  *direction* across tiers, in *level* only within Tier A.
- **RQ4 (scale):** the **only** valid controlled pair is **Llama 3.2 11B vs 90B**
  (verified same architecture: Llama-3.1 backbone + vision adapter, two sizes).
  This measures *prompt-induced localization* scale, not native grounding. All
  other size differences (7B dense vs 16B MoT vs 30B-A3B MoE) are **not
  commensurable** and are reported descriptively only.
- **RQ5 (cost/latency):** access path drives frontier assignment — **local**
  {Qwen, Llama 11B, Llama 90B} vs **NIM-API** {Cosmos, Nemotron}. Never one
  frontier (see [`experiment_plan.md`](experiment_plan.md)).

## Verification checklist (status)

- [x] Official model card / paper per model (URLs in the verification log).
- [x] Native bbox output + coordinate format per model → adapter mapping above.
- [x] Tier classification (A/B/C) with evidence.
- [x] Parameter counts (for RQ4); same-family scale pair identified (Llama).
- [x] Access path (API vs local) per model.
- [ ] **Deterministic decoding at T=0 per model — [⚠ verify], esp. NIM APIs.**
- [ ] **Token accounting / pricing per provider (RQ5) — [⚠ verify], may be TBD.**
- [ ] **Cosmos exact bbox JSON key — TBD (only `point_2d` confirmed verbatim).**
- [ ] **Hosted-API coverage for Llama 3.2 Vision — [⚠ verify].**
- [x] License per model (NIM-endpoint terms for Cosmos still **TBD**).

## Adapter contract (design only — not implemented yet)

Each model gets a thin adapter under [`../models/`](../models):

```
predict(image, prompt) -> raw_response   # verbatim, saved to results/raw_outputs
```

Adapters do **not** score, edit GT, or alter prompts. Box parsing and the
per-model conversions above live in the **evaluation layer**, documented here and
frozen with the protocol.

> No adapters are implemented until the remaining `[⚠ verify]`/TBD items close.
