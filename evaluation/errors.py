"""Typed errors used across the evaluation core.

These exist so that methodology violations fail LOUDLY instead of silently
producing a wrong number.
"""


class FamilyCoercionError(TypeError):
    """Raised when code tries to mix the two spatial metric families.

    Invariants B & C (docs/metrics_spec.md):
      - scoring a point with IoU, or
      - converting a point into a bbox (or vice-versa).
    """


class TBDBlocker(Exception):
    """Raised when a computation requires a decision that docs/ still marks TBD.

    We NEVER guess a TBD value (e.g. the normalized-point-error scale ``s_i``, or
    the frozen prompted-output numeric convention). Hitting this means: stop and
    ask the human to resolve the TBD in docs/, then retry.
    """
