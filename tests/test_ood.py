from __future__ import annotations

import numpy as np
import pandas as pd

from failsafemlx.reliability.ood import MahalanobisOODDetector


def test_mahalanobis_ood_detector_reports_warning_on_shift():
    rng = np.random.default_rng(23)
    ref = pd.DataFrame(rng.normal(0, 1, size=(500, 4)), columns=list("abcd"))
    cur = pd.DataFrame(rng.normal(3, 1, size=(100, 4)), columns=list("abcd"))
    detector = MahalanobisOODDetector(threshold_quantile=0.95).fit(ref)
    report = detector.report(cur, ood_rate_warning_threshold=0.15)
    assert report["ood_warning"] is True
    assert report["ood_rate"] > 0.15
