"""Prediction selection and duplicate handling for the BBox family.

Rules (docs/metrics_spec.md):
  - Single-target headline prediction = the model's FIRST box.
  - Duplicate predictions with pairwise IoU >= 0.95 are removed before matching.
  - The bbox matcher must REJECT a Point (invariant C: no point->bbox coercion).

Multi-target Hungarian matching is defined in docs but is NOT exercised in
Phase A; it is intentionally left unimplemented rather than approximated.
"""
from __future__ import annotations

from .errors import FamilyCoercionError, TBDBlocker
from .geometry import BBox, Point, iou

DUP_IOU_THRESHOLD = 0.95  # locked in docs/metrics_spec.md


def _reject_point(obj) -> None:
    if isinstance(obj, Point):
        raise FamilyCoercionError(
            "A Point was passed to the BBox matcher; points are never coerced "
            "into boxes (invariant C)."
        )


def dedup_bboxes(preds, thr: float = DUP_IOU_THRESHOLD):
    """Remove near-identical boxes (IoU >= thr), keeping first-seen order.

    Deterministic: input order is preserved; earlier boxes win.
    """
    kept: list[BBox] = []
    for p in preds:
        _reject_point(p)
        if not isinstance(p, BBox):
            raise FamilyCoercionError("dedup_bboxes() expects BBox instances.")
        if any(iou(p, k) >= thr for k in kept):
            continue
        kept.append(p)
    return kept


def select_first_box(preds):
    """Headline single-target prediction = first box (no oracle peeking)."""
    if not preds:
        return None
    _reject_point(preds[0])
    if not isinstance(preds[0], BBox):
        raise FamilyCoercionError("select_first_box() expects BBox instances.")
    return preds[0]


def hungarian_match(*_args, **_kwargs):
    """Multi-target one-to-one matching — NOT implemented in Phase A.

    docs/metrics_spec.md specifies Hungarian matching for multi-target detection,
    but Phase A only exercises single-target localization. Implementing it now
    without the multi-target held-out data would be premature.
    """
    raise TBDBlocker(
        "Multi-target Hungarian matching is out of Phase A scope (needs the "
        "multi-target held-out set). Do not approximate it here."
    )
