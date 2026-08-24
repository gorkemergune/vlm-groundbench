"""T-09 — hallucination / negative probes.

Guards: a returned box/point on an absent referent is a hallucination; a correct
NOT_PRESENT decline is neither a hallucination nor a miss (docs/metrics_spec.md).
"""
from evaluation.geometry import BBox
from evaluation.families import MetricFamily
from evaluation.metrics import hallucination
from evaluation.types import SampleResult


def test_t09_negative_probe_and_decline():
    # Negative probe, model returned a box anyway -> hallucination.
    neg_hit = SampleResult("neg1", MetricFamily.BBOX, referent_present=False,
                           gt_boxes=[], pred_bbox=BBox(0, 0, 5, 5),
                           parse_success=True, not_present=False)
    # Negative probe, model correctly declined -> NOT a hallucination, NOT a miss.
    neg_decline = SampleResult("neg2", MetricFamily.BBOX, referent_present=False,
                               gt_boxes=[], pred_bbox=None,
                               parse_success=False, not_present=True)
    # Present referent, asserted box with IoU=0 vs GT -> gross-wrong-box.
    wrong = SampleResult("p1", MetricFamily.BBOX, referent_present=True,
                         gt_boxes=[BBox(100, 100, 10, 10)],
                         pred_bbox=BBox(0, 0, 10, 10), parse_success=True)

    h = hallucination([neg_hit, neg_decline, wrong])
    assert h["hall_absent_n"] == 2          # two negative probes
    assert h["hall_absent"] == 0.5          # only neg1 hallucinated
    assert h["hall_wrongbox_n"] == 1
    assert h["hall_wrongbox"] == 1.0


def test_t09_decline_not_counted_as_absent_hallucination():
    only_decline = SampleResult("neg", MetricFamily.BBOX, referent_present=False,
                                gt_boxes=[], pred_bbox=None,
                                parse_success=False, not_present=True)
    h = hallucination([only_decline])
    assert h["hall_absent"] == 0.0          # correct decline is not a hallucination
