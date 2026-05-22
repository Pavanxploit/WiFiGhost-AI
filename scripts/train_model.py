from __future__ import annotations

import random
import sys
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.detector import FEATURE_NAMES


def normal_feature_row() -> list[float]:
    ap_count = random.randint(3, 7)
    unknown_bssid_count = random.choice([0, 0, 0, 1])
    new_ssid_count = random.choice([0, 0, 1])
    known_ssid_unknown_bssid_count = 0
    duplicate_ssid_count = random.choice([0, 0, 0, 1])
    open_network_count = random.choice([0, 0, 1])
    weak_encryption_count = open_network_count
    strong_unknown_count = 0
    avg_rssi = random.uniform(-70, -48)
    max_rssi = random.uniform(-54, -38)
    min_rssi = random.uniform(-88, -62)
    channel_spread = random.choice([5, 6, 10, 11])
    return [
        ap_count,
        unknown_bssid_count,
        new_ssid_count,
        known_ssid_unknown_bssid_count,
        duplicate_ssid_count,
        open_network_count,
        weak_encryption_count,
        strong_unknown_count,
        avg_rssi,
        max_rssi,
        min_rssi,
        channel_spread,
    ]


def main() -> None:
    random.seed(7)
    rows = [normal_feature_row() for _ in range(350)]
    model = IsolationForest(
        n_estimators=150,
        contamination=0.08,
        random_state=7,
    )
    model.fit(np.array(rows, dtype=float))

    out = ROOT / "models" / "wifighost_model.joblib"
    out.parent.mkdir(exist_ok=True)
    joblib.dump(model, out)
    print(f"Saved {out}")
    print("Features:", ", ".join(FEATURE_NAMES))


if __name__ == "__main__":
    main()
