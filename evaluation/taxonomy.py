"""Error taxonomy codes (docs/error_analysis.md).

Two SEPARATE families of codes. They are never pooled and there is no
cross-family code (invariant J).
"""
from __future__ import annotations

# --- BBox family (Qwen native bbox; all prompt-induced boxes) ---
E_LOC = "E-LOC"      # correct object, box too loose/tight/shifted (0 < IoU < tau)
E_WRONG = "E-WRONG"  # confident box on the wrong referent (IoU ~ 0)
E_HALL = "E-HALL"    # box for an absent referent
E_MISS = "E-MISS"    # no box / NOT_PRESENT for a present referent
E_MULTI = "E-MULTI"  # wrong number of targets
E_FMT = "E-FMT"      # output not parseable to a box
E_AMB = "E-AMB"      # genuinely ambiguous GT (not a model fault)

BBOX_CODES = frozenset({E_LOC, E_WRONG, E_HALL, E_MISS, E_MULTI, E_FMT, E_AMB})

# --- Point family (Cosmos-native-point only; scored against GT bbox, never IoU) ---
P_IN = "P-IN"        # point_correct / point_inside: point inside correct GT box
P_OUT = "P-OUT"      # point_outside: correct referent, point outside its GT box
P_WRONG = "P-WRONG"  # point_wrong_target: point inside a different object's region
P_HALL = "P-HALL"    # point_hallucination: point for an absent referent
P_MISS = "P-MISS"    # point_missed: no point / NOT_PRESENT for a present referent
P_DUP = "P-DUP"      # point_duplicate: redundant points for a single-target referent
P_FMT = "P-FMT"      # point_parse_failure: output not parseable to an (x,y) point

POINT_CODES = frozenset({P_IN, P_OUT, P_WRONG, P_HALL, P_MISS, P_DUP, P_FMT})

# Invariant check available to callers/tests: the two code sets must stay disjoint.
assert BBOX_CODES.isdisjoint(POINT_CODES), "BBox and Point error codes must be disjoint"
