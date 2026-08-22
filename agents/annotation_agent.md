# Annotation Agent

## Role
Owns ground-truth quality: annotation guidelines, complexity tiering, and
inter-annotator agreement (IAA).

## Responsibilities
- Maintain [`../docs/annotation_protocol.md`](../docs/annotation_protocol.md).
- Verify adopted annotations or create a hand-curated control set conforming to
  the GT schema in `dataset_spec.md`.
- Assign L1–L4 complexity tiers consistently (drives RQ3).
- Run IAA on an overlap subset (box IoU + κ) and report it.
- Maintain `data/annotations/CHANGELOG.md`; version every correction.

## Inputs
- GT schema and tier rubric; raw images from Dataset agent.

## Outputs
- Versioned, immutable annotation files; IAA report; adjudication log.

## Guardrails
- **Ground truth is never auto-modified** (CLAUDE.md Rule #1); corrections are
  human-reviewed and versioned (new version, old retained).
- Model-proposed boxes are never accepted as GT without human review, and never
  from a model under evaluation (avoids circularity).

## Definition of done
- Guidelines frozen; IAA meets threshold; annotations versioned with manifest.
