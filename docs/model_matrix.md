# Model Matrix

> **Status:** Capabilities **verified** against primary sources (Aug 2026). This
> replaces the earlier all-`[⚠ verify]` draft. Every capability below carries an
> evidence tag; values still unknown are marked **TBD**. Per CLAUDE.md we do
> **not** invent capabilities, sizes, or licenses.

## Capability classes (the organizing distinction for the whole benchmark)

The benchmark is a **native-vs-prompted localization study**. Models are classified
by *how* they produce coordinates **and by which spatial primitive is natively
documented** — because a native **bounding box** and a native **point** are not the
same capability and are not scored with the same metric.

- **Tier A — native/documented localization.** The vendor documents a coordinate
  output format. Tier A subdivides by primitive:
  - **A-bbox — native bounding box.** Documented bbox output. → **Qwen2.5-VL-7B**.
  - **A-point — native point.** Documented point output; **no** documented native
    bbox schema. → **Cosmos3-Nano-Reasoner**.
- **Tier B — visual localization/reasoning without a documented coordinate
  output.** The model can reason about *where* things are, but the vendor
  documents no bbox/point format.
- **Tier C — prompt-induced coordinates.** Any coordinate the model emits exists
  only because the prompt asked for one; it is not a documented capability.

> **Rule (integrity):** A Tier-C coordinate is **never** described as "native
> grounding/localization." **Cosmos is never described as native bbox** — its
> documented native primitive is the **point** (`point_2d`); any Cosmos *box* is
> **prompt-induced**. See CLAUDE.md Rule #9 (capability vs prompt engineering).

## Verified model table

| Model | Params (verified) | Access | Native primitive (documented) | Documented coordinate format | Structured JSON | **Class** | License |
|-------|-------------------|--------|-------------------------------|------------------------------|-----------------|-----------|---------|
| **Qwen2.5-VL-7B-Instruct** | ~7B dense **[Verified]** | Local **[Verified, Apache-2.0]** + hosted API (Alibaba DashScope) **[Verified]** | **Native bounding box** — `bbox_2d` **[Verified]** | **Absolute pixels, `xyxy`**, origin top-left **[Verified]** | **Yes** — documented stable JSON coords **[Verified]** | **A-bbox** | Apache-2.0 **[Verified]** |
| **Cosmos3-Nano-Reasoner** | 16B total; **8B dense backbone** (Mixture-of-Transformers, adapts Qwen3-VL 8B arch) **[Verified]** | NVIDIA NIM API **[Verified]** + local weights (`nvidia/Cosmos3-Nano`) **[Verified]** | **Native point** — `point_2d [x,y]` **[Verified]**. **NOT confirmed native bbox** — no documented bbox JSON schema (model card mentions boxes only "in general terms") **[Verified: not documented]** | **Point: normalized 0–1000 per axis**, origin top-left, JSON **[Verified]**. Native bbox format: **none documented** | **Yes** (points) **[Verified]** | **A-point** | OpenMDW-1.1 (HF card) **[Verified]**; NIM-endpoint terms **TBD** |
| **Llama 3.2 11B Vision** | **10.6B** dense **[Verified]** | Local (gated HF weights) **[Verified]** + third-party hosted (no first-party Meta API found) **[Verified]** | **None** — no documented bbox/point schema; grounding named only as a *use case*; **text-out only** | none documented → any coordinate is **prompt-induced** | Not documented **[Verified]** | **C** (prompt-induced; retains Tier-B localization ability) | Llama 3.2 Community License **[Verified]** |
| **Llama 3.2 90B Vision** | **88.8B** dense **[Verified]** | Local (multi-GPU) **[Verified]** + third-party hosted (no first-party Meta API found) **[Verified]** | Same as 11B **[Verified]** | none documented → **prompt-induced** | Not documented **[Verified]** | **C** (prompt-induced; retains Tier-B localization ability) | Llama 3.2 Community License **[Verified]** |
| **Nemotron 3 Nano Omni** | **30B-A3B MoE (~3B active/token)** **[Verified]** | NVIDIA NIM API **[Verified]** + local (HF weights) + AWS SageMaker JumpStart **[Verified]** | **None** — no documented grounding/bbox/point schema; OCR/GUI focus | none documented → **prompt-induced**; JSON output supported, but **not for coordinates** | JSON yes; **coords: not documented** **[Verified]** | **C** (prompt-induced; retains Tier-B localization ability) | NVIDIA Open Model Agreement **[Verified]** |

**Class assignment for the study:**
- **A-bbox (native bounding box):** {Qwen2.5-VL-7B} → **bbox metric family**.
- **A-point (native point):** {Cosmos3-Nano-Reasoner} → **point metric family**.
- **C (prompt-induced coordinates):** {Llama 3.2 11B, Llama 3.2 90B, Nemotron 3
  Nano Omni} → coordinates only via prompting; retain Tier-B localization ability.

> **A-bbox and A-point are not directly comparable** (different spatial primitive,
> different metric family — see [`metrics_spec.md`](metrics_spec.md)). Cosmos is
> **never** called native bbox.

## Per-model / per-condition coordinate handling (drives the evaluation adapter)

There are **two canonical internal schemas**, one per metric family (see
[`metrics_spec.md`](metrics_spec.md)):
- **BBox family** → canonical `xywh`, absolute pixels, origin top-left.
- **Point family** → canonical `(x, y)`, absolute pixels, origin top-left.

Conversions are per-condition and **must be unit-tested against known
boxes/points** before any reported run (a top source of silent IoU/point-error
bugs). **A point is never converted into a box and never scored with IoU.**

| Condition | Native? | Raw form | Metric family | Conversion |
|-----------|---------|----------|---------------|------------|
| **Qwen native bbox** | native | `bbox_2d [x1,y1,x2,y2]` abs px | BBox | `w=x2−x1, h=y2−y1` |
| **Cosmos-native-point** | native | `point_2d [x,y]` normalized 0–1000 | **Point** | multiply by `(W/1000, H/1000)` using **post-preprocessing** image W,H → `(x,y)` abs-px |
| **Cosmos-prompted-bbox** | **prompt-induced** | box elicited by prompt (no documented native bbox schema) | BBox | robust parse; **label prompt-induced**; flag parse failures |
| **Qwen prompted bbox** (E1b) | prompt-induced | box from shared prompt | BBox | robust parse; label prompt-induced |
| **Llama 11B / 90B** | prompt-induced | free-text box | BBox | robust parse; flag parse failures; label prompt-induced |
| **Nemotron 3 Nano Omni** | prompt-induced | JSON/free-text box | BBox | robust parse; flag parse failures; label prompt-induced |

> The **prompt regime** differs by condition (native elicitation for Qwen bbox and
> Cosmos point; shared prompted regime for all) — see
> [`prompt_protocol.md`](prompt_protocol.md). Native conditions emit their **native**
> format and the adapter converts; they are never instructed to emit a foreign
> format. **Cosmos-prompted-bbox is a prompt-induced condition, never native bbox.**

## RQ dependencies on this table

- **RQ1 (native localization accuracy):** reported **per native primitive on its
  own metric family** — Qwen native **bbox** (bbox metrics) and Cosmos-native-point
  (point metrics). These two are **not combined into one ranking** (different
  primitive/metric). C-model numbers are reported labeled *prompt-induced*.
- **RQ2 (native vs prompt-induced):** two contrasts, kept separate: (i) **bbox
  metric family** — Qwen native bbox vs prompt-induced bbox (Cosmos-prompted-bbox,
  Llama×2, Nemotron); (ii) **within-Cosmos** — native-point vs prompted-bbox
  (does the documented native primitive beat prompting Cosmos for a box?). Primary
  metric is **Acc@IoU** for bbox and **point-in-GT-box accuracy** for point, **not**
  mAP (see [`metrics_spec.md`](metrics_spec.md)).
- **RQ3 (prompt complexity):** within-model across all five (unchanged). Comparable
  in *direction* across models; in *level* only within a shared metric family.
- **RQ4 (scale):** the **only** valid controlled pair is **Llama 3.2 11B vs 90B**
  (verified same architecture: Llama-3.1 backbone + vision adapter, two sizes).
  This measures *prompt-induced bbox localization* scale. All other size
  differences (7B dense vs 16B MoT vs 30B-A3B MoE) are **not commensurable** and
  reported descriptively only. (Unchanged by this revision.)
- **RQ5 (cost/latency):** access path drives frontier assignment — **local**
  {Qwen, Llama 11B, Llama 90B} vs **NIM-API** {Cosmos, Nemotron}. Never one
  frontier (see [`experiment_plan.md`](experiment_plan.md)). (Unchanged.)

## Verification checklist (status)

- [x] Official model card / paper per model (URLs in the verification log).
- [x] Native primitive + coordinate format per model → adapter mapping above.
- [x] Class assignment (A-bbox / A-point / C) with evidence.
- [x] Parameter counts (for RQ4); same-family scale pair identified (Llama).
- [x] Access path (API vs local) per model.
- [x] **Cosmos bbox JSON key — resolved: NOT DOCUMENTED in primary sources.**
      Cosmos native primitive = `point_2d` (0–1000); any Cosmos box is
      prompt-induced. (Do not invent a bbox schema.)
- [x] **Hosted-API coverage for Llama 3.2 Vision — resolved: no first-party Meta
      API found; third-party hosted exists (NVIDIA NIM/Together/Oracle[dep]/
      DeepInfra). Design unaffected (Llama is local).**
- [ ] **Deterministic decoding at T=0 per model — [⚠ verify] NOT DOCUMENTED for
      NIM APIs; keep flag + capture returned model version.**
- [ ] **Token accounting / pricing per provider (RQ5) — no official per-model NIM
      pricing found → cost reported N/A / TBD.**
- [x] License per model verified (NIM hosted API = trial/research-eval only, not
      production; NIM-endpoint commercial terms **TBD** if productionized).

## Adapter contract (design only — not implemented yet)

Each model gets a thin adapter under [`../models/`](../models):

```
predict(image, prompt) -> raw_response   # verbatim, saved to results/raw_outputs
```

Adapters do **not** score, edit GT, or alter prompts. Box parsing and the
per-model conversions above live in the **evaluation layer**, documented here and
frozen with the protocol.

> No adapters are implemented until the remaining `[⚠ verify]`/TBD items close.
