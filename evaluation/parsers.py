"""Per-condition output parsers.

Each parser turns a raw model response into a ParseResult. Parsers do NOT score.

Locked native formats (docs/model_matrix.md):
  - Qwen native  : {"bbox_2d": [x1, y1, x2, y2]} absolute pixels (xyxy).
  - Cosmos native: {"point_2d": [x, y]} normalized 0-1000 (top-left origin).

Prompted-bbox output is parsed ROBUSTLY for parse-success only. The numeric
convention of prompted output (xyxy vs xywh vs normalized) depends on the FROZEN
prompt-registry output_format_spec, which is still TBD — so this parser extracts
the raw numbers + a success flag and does NOT convert to canonical coordinates.

Invariant G: a NOT_PRESENT decline is tracked separately and is NOT a parse
failure.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from .errors import TBDBlocker
from .geometry import BBox, xyxy_to_xywh

# LOCKED prompted-bbox output format (Karar B): JSON {"bbox": [x, y, w, h]},
# absolute pixels, xywh, origin top-left. This IS the canonical schema, so the
# converter is an identity map (no coercion, no xyxy<->xywh ambiguity).
PROMPTED_OUTPUT_FORMAT = "xywh_abs_pixels"
PROMPTED_JSON_KEY = "bbox"

_NUM = re.compile(r"-?\d+(?:\.\d+)?")
_NOT_PRESENT = re.compile(r"\bNOT_PRESENT\b", re.IGNORECASE)


@dataclass
class ParseResult:
    success: bool                     # True iff a valid coordinate object was parsed
    primitive: str | None = None      # "bbox" | "point" | None
    bbox: BBox | None = None          # canonical xywh (native bbox only)
    norm_point: tuple[float, float] | None = None  # Cosmos normalized (0-1000) point
    raw_numbers: list[float] | None = None         # prompted-bbox: extracted numbers
    not_present: bool = False         # model explicitly declined (valid, not a fail)
    note: str = ""
    extra: dict = field(default_factory=dict)


def _as_obj(raw):
    """Accept a dict or a JSON string; return a dict/list or None."""
    if isinstance(raw, (dict, list)):
        return raw
    if isinstance(raw, str):
        try:
            return json.loads(raw)
        except (ValueError, TypeError):
            return None
    return None


def parse_qwen_bbox(raw) -> ParseResult:
    """Qwen native bbox_2d -> canonical xywh (invariant F)."""
    obj = _as_obj(raw)
    coords = None
    if isinstance(obj, dict) and "bbox_2d" in obj:
        coords = obj["bbox_2d"]
    elif isinstance(obj, list) and len(obj) == 4:
        coords = obj
    if not (isinstance(coords, (list, tuple)) and len(coords) == 4):
        return ParseResult(success=False, primitive="bbox", note="no bbox_2d found")
    try:
        x1, y1, x2, y2 = (float(v) for v in coords)
    except (TypeError, ValueError):
        return ParseResult(success=False, primitive="bbox", note="non-numeric bbox_2d")
    return ParseResult(success=True, primitive="bbox", bbox=xyxy_to_xywh(x1, y1, x2, y2))


def parse_cosmos_point(raw) -> ParseResult:
    """Cosmos native point_2d -> normalized (0-1000) point (invariant E).

    Conversion to pixels is done later via geometry.cosmos_norm_point_to_pixel,
    using the sample's image W,H. This parser never emits a BBox (invariant C).
    """
    obj = _as_obj(raw)
    coords = None
    if isinstance(obj, dict) and "point_2d" in obj:
        coords = obj["point_2d"]
    elif isinstance(obj, list) and len(obj) == 2:
        coords = obj
    if not (isinstance(coords, (list, tuple)) and len(coords) == 2):
        return ParseResult(success=False, primitive="point", note="no point_2d found")
    try:
        nx, ny = (float(v) for v in coords)
    except (TypeError, ValueError):
        return ParseResult(success=False, primitive="point", note="non-numeric point_2d")
    return ParseResult(success=True, primitive="point", norm_point=(nx, ny))


def parse_prompted_bbox(raw) -> ParseResult:
    """Robust prompted-bbox parser: parse-success flag only (no canonicalization).

    - Explicit NOT_PRESENT  -> success=False, not_present=True (a valid decline).
    - >= 4 numbers found    -> success=True, raw_numbers=first 4.
    - otherwise             -> success=False (parse failure, invariant G).

    We deliberately do NOT interpret the 4 numbers as xyxy/xywh/normalized here:
    that mapping is set by the frozen prompt output_format_spec (TBD).
    """
    text = raw if isinstance(raw, str) else json.dumps(raw)

    if _NOT_PRESENT.search(text):
        return ParseResult(success=False, primitive="bbox", not_present=True,
                           note="model declined (NOT_PRESENT)")

    obj = _as_obj(raw)
    if isinstance(obj, dict):
        for key in (PROMPTED_JSON_KEY, "bbox_2d"):  # locked key first, legacy second
            val = obj.get(key)
            if isinstance(val, (list, tuple)) and len(val) == 4:
                try:
                    nums = [float(v) for v in val]
                    return ParseResult(success=True, primitive="bbox",
                                       raw_numbers=nums, note=f"json {key}")
                except (TypeError, ValueError):
                    pass

    nums = [float(m.group()) for m in _NUM.finditer(text)]
    if len(nums) >= 4:
        return ParseResult(success=True, primitive="bbox", raw_numbers=nums[:4],
                           note="regex 4-number extraction")
    return ParseResult(success=False, primitive="bbox", note="unparseable to a box")


def convert_prompted_numbers(raw_numbers, output_format_spec: str) -> BBox | None:
    """Convert parsed prompted-bbox numbers to canonical xywh abs-px (Karar B).

    For the LOCKED spec `xywh_abs_pixels`, the numbers ARE [x, y, w, h] in absolute
    pixels — an identity map to canonical BBox. Returns None for an invalid box
    (`w <= 0` or `h <= 0`), which the evaluator records as a PARSE FAILURE (not a
    localization failure). Raises TBDBlocker for any non-locked spec — we never
    guess a numeric convention.
    """
    if output_format_spec != PROMPTED_OUTPUT_FORMAT:
        raise TBDBlocker(
            f"output_format_spec {output_format_spec!r} is not the locked "
            f"{PROMPTED_OUTPUT_FORMAT!r}; no other convention is defined."
        )
    if not raw_numbers or len(raw_numbers) < 4:
        return None
    x, y, w, h = (float(v) for v in raw_numbers[:4])
    if w <= 0 or h <= 0:
        return None
    return BBox(x, y, w, h)
