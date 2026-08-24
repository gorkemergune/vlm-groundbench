"""Geometric primitives and coordinate conversions.

Two canonical internal schemas (docs/metrics_spec.md, docs/benchmark_protocol.md):
  - BBox family  -> xywh, absolute pixels, origin top-left.
  - Point family -> (x, y), absolute pixels, origin top-left.

A BBox and a Point are DISTINCT types. IoU only accepts BBox; passing a Point
raises FamilyCoercionError (invariant B). There is no point->bbox conversion here
(invariant C).
"""
from __future__ import annotations

from dataclasses import dataclass

from .errors import FamilyCoercionError


@dataclass(frozen=True)
class BBox:
    """Canonical bounding box: xywh, absolute pixels, origin top-left."""

    x: float
    y: float
    w: float
    h: float

    def to_xyxy(self) -> tuple[float, float, float, float]:
        return (self.x, self.y, self.x + self.w, self.y + self.h)

    def area(self) -> float:
        return max(0.0, self.w) * max(0.0, self.h)


@dataclass(frozen=True)
class Point:
    """Canonical point: (x, y), absolute pixels, origin top-left."""

    x: float
    y: float


def xyxy_to_xywh(x1: float, y1: float, x2: float, y2: float) -> BBox:
    """Qwen native bbox_2d is [x1,y1,x2,y2] absolute px -> canonical xywh."""
    return BBox(x=float(x1), y=float(y1), w=float(x2) - float(x1), h=float(y2) - float(y1))


def cosmos_norm_point_to_pixel(nx: float, ny: float, image_w: int, image_h: int) -> Point:
    """Cosmos native point_2d is normalized to 0-1000 per axis (top-left origin).

    Convert to absolute pixels using the POST-preprocessing image size:
        px = nx * W / 1000 ,  py = ny * H / 1000
    (docs/model_matrix.md conversion table). This is invariant E; note we produce
    a Point, never a BBox (invariant C).
    """
    return Point(x=float(nx) * float(image_w) / 1000.0,
                 y=float(ny) * float(image_h) / 1000.0)


def iou(a: BBox, b: BBox) -> float:
    """Intersection-over-Union for two bounding boxes (invariant B guard).

    Raises FamilyCoercionError if either argument is not a BBox — a point must
    never be scored with IoU.
    """
    if not isinstance(a, BBox) or not isinstance(b, BBox):
        raise FamilyCoercionError(
            "iou() requires two BBox instances; a Point is never scored with IoU "
            "(metric-family invariant B)."
        )
    ax1, ay1, ax2, ay2 = a.to_xyxy()
    bx1, by1, bx2, by2 = b.to_xyxy()
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0.0, ix2 - ix1), max(0.0, iy2 - iy1)
    inter = iw * ih
    union = a.area() + b.area() - inter
    if union <= 0.0:
        return 0.0
    return inter / union


def point_in_box(p: Point, gt: BBox) -> bool:
    """Point-in-GT-box test (invariant B: the point-family primary primitive).

    Boundary is INCLUSIVE ("inside (or on)") per docs/metrics_spec.md.
    Raises FamilyCoercionError if a BBox is passed where a Point is expected.
    """
    if not isinstance(p, Point) or not isinstance(gt, BBox):
        raise FamilyCoercionError(
            "point_in_box() requires (Point, BBox); no point<->bbox coercion "
            "(invariants A & C)."
        )
    x1, y1, x2, y2 = gt.to_xyxy()
    return (x1 <= p.x <= x2) and (y1 <= p.y <= y2)


def center_distance_px(p: Point, gt: BBox) -> float:
    """Raw pixel distance from a point to a GT box center.

    Unnormalized (pixels) — this involves NO methodology decision. The NORMALIZED
    point error requires the scale s_i (image-diagonal vs sqrt(area)), which is
    TBD in docs/ and therefore lives in metrics.normalized_point_error (raises).
    """
    if not isinstance(p, Point) or not isinstance(gt, BBox):
        raise FamilyCoercionError("center_distance_px() requires (Point, BBox).")
    cx = gt.x + gt.w / 2.0
    cy = gt.y + gt.h / 2.0
    return ((p.x - cx) ** 2 + (p.y - cy) ** 2) ** 0.5
