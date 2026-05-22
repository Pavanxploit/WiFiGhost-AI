from __future__ import annotations

import json
import math
import shutil
import time
from pathlib import Path
from typing import Any

import joblib
import numpy as np


FEATURE_NAMES = [
    "ap_count",
    "unknown_bssid_count",
    "new_ssid_count",
    "known_ssid_unknown_bssid_count",
    "duplicate_ssid_count",
    "open_network_count",
    "weak_encryption_count",
    "strong_unknown_count",
    "avg_rssi",
    "max_rssi",
    "min_rssi",
    "channel_spread",
]


OPEN_OR_WEAK = {"OPEN", "WEP"}


def clamp(value: float, low: int = 0, high: int = 100) -> int:
    return int(max(low, min(high, round(value))))


def now_ms() -> int:
    return int(time.time() * 1000)


def normalize_bssid(value: Any) -> str:
    return str(value or "").strip().upper()


def normalize_ssid(value: Any) -> str:
    text = str(value or "").strip()
    return text if text else "<hidden>"


def normalize_encryption(value: Any) -> str:
    text = str(value or "UNKNOWN").strip().upper()
    if "OPEN" in text or text == "NONE":
        return "OPEN"
    if "WEP" in text:
        return "WEP"
    if "WPA3" in text:
        return "WPA3"
    if "WPA2" in text:
        return "WPA2"
    if "WPA" in text:
        return "WPA"
    return text or "UNKNOWN"


def normalize_networks(networks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for item in networks:
        bssid = normalize_bssid(item.get("bssid") or item.get("mac"))
        if not bssid:
            continue
        try:
            rssi = int(item.get("rssi", -100))
        except (TypeError, ValueError):
            rssi = -100
        try:
            channel = int(item.get("channel", 0))
        except (TypeError, ValueError):
            channel = 0
        normalized.append(
            {
                "ssid": normalize_ssid(item.get("ssid")),
                "bssid": bssid,
                "rssi": rssi,
                "channel": channel,
                "encryption": normalize_encryption(item.get("encryption") or item.get("auth")),
            }
        )
    return normalized


class WifiGhostDetector:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.data_dir = root / "data"
        self.model_path = root / "models" / "wifighost_model.joblib"
        self.baseline_path = self.data_dir / "baseline.json"
        self.demo_baseline_path = self.data_dir / "demo_baseline.json"
        self.events_path = self.data_dir / "events.jsonl"
        self.latest_path = self.data_dir / "latest_scan.json"
        self.data_dir.mkdir(exist_ok=True)
        self.model = self._load_model()
        self.baseline = self._load_baseline()

    @property
    def model_status(self) -> str:
        return "IsolationForest ready" if self.model is not None else "heuristic fallback"

    def seed_demo_baseline(self) -> dict[str, Any]:
        if self.demo_baseline_path.exists():
            shutil.copyfile(self.demo_baseline_path, self.baseline_path)
        self.baseline = self._load_baseline()
        return self.baseline

    def learn_baseline(self, networks: list[dict[str, Any]]) -> dict[str, Any]:
        normalized = normalize_networks(networks)
        baseline = self._empty_baseline()
        known_bssids: dict[str, dict[str, Any]] = {}
        ssid_to_bssids: dict[str, list[str]] = {}

        for net in normalized:
            bssid = net["bssid"]
            ssid = net["ssid"]
            known_bssids[bssid] = {
                "ssid": ssid,
                "channel": net["channel"],
                "encryption": net["encryption"],
                "last_rssi": net["rssi"],
            }
            ssid_to_bssids.setdefault(ssid, [])
            if bssid not in ssid_to_bssids[ssid]:
                ssid_to_bssids[ssid].append(bssid)

        baseline["known_bssids"] = known_bssids
        baseline["ssid_to_bssids"] = ssid_to_bssids
        baseline["updated_at"] = now_ms()
        self.baseline = baseline
        self._save_json(self.baseline_path, baseline)
        return baseline

    def analyze_payload(self, payload: dict[str, Any], learn: bool = False) -> dict[str, Any]:
        networks = normalize_networks(payload.get("networks", []))
        device_id = str(payload.get("device_id") or "unknown-device")

        if learn:
            self.learn_baseline(networks)

        if not self.baseline["known_bssids"] and networks:
            self.learn_baseline(networks)
            result = self._result(
                device_id=device_id,
                networks=networks,
                risk_score=8,
                status="LEARNING",
                threat="Baseline captured",
                reasons=["First scan saved as the normal Wi-Fi environment."],
                features=self.extract_features(networks),
                ml_score=None,
            )
            self._persist_result(result)
            return result

        features = self.extract_features(networks)
        reasons = self.explain(features, networks)
        heuristic_score = self.heuristic_risk(features)
        ml_score = self.ml_risk(features)

        if ml_score is None:
            risk_score = heuristic_score
        else:
            risk_score = max(heuristic_score, ml_score)

        status, threat = self.classify(risk_score, reasons)
        result = self._result(
            device_id=device_id,
            networks=networks,
            risk_score=risk_score,
            status=status,
            threat=threat,
            reasons=reasons or ["No unusual Wi-Fi behavior found in this scan."],
            features=features,
            ml_score=ml_score,
        )
        self._persist_result(result)
        return result

    def extract_features(self, networks: list[dict[str, Any]]) -> dict[str, float]:
        known_bssids = self.baseline["known_bssids"]
        ssid_to_bssids = self.baseline["ssid_to_bssids"]
        seen_ssids: dict[str, int] = {}

        unknown_bssid_count = 0
        new_ssid_count = 0
        known_ssid_unknown_bssid_count = 0
        open_network_count = 0
        weak_encryption_count = 0
        strong_unknown_count = 0
        channels: list[int] = []
        rssis: list[int] = []

        for net in networks:
            ssid = net["ssid"]
            bssid = net["bssid"]
            encryption = net["encryption"]
            rssi = int(net["rssi"])
            channel = int(net["channel"])
            seen_ssids[ssid] = seen_ssids.get(ssid, 0) + 1
            rssis.append(rssi)
            if channel:
                channels.append(channel)

            is_unknown_bssid = bssid not in known_bssids
            is_known_ssid = ssid in ssid_to_bssids
            if is_unknown_bssid:
                unknown_bssid_count += 1
            if not is_known_ssid:
                new_ssid_count += 1
            if is_unknown_bssid and is_known_ssid:
                known_ssid_unknown_bssid_count += 1
            if encryption == "OPEN":
                open_network_count += 1
            if encryption in OPEN_OR_WEAK:
                weak_encryption_count += 1
            if is_unknown_bssid and rssi >= -48:
                strong_unknown_count += 1

        duplicate_ssid_count = sum(1 for count in seen_ssids.values() if count > 1)
        avg_rssi = float(sum(rssis) / len(rssis)) if rssis else -100.0
        max_rssi = float(max(rssis)) if rssis else -100.0
        min_rssi = float(min(rssis)) if rssis else -100.0
        channel_spread = float(max(channels) - min(channels)) if channels else 0.0

        return {
            "ap_count": float(len(networks)),
            "unknown_bssid_count": float(unknown_bssid_count),
            "new_ssid_count": float(new_ssid_count),
            "known_ssid_unknown_bssid_count": float(known_ssid_unknown_bssid_count),
            "duplicate_ssid_count": float(duplicate_ssid_count),
            "open_network_count": float(open_network_count),
            "weak_encryption_count": float(weak_encryption_count),
            "strong_unknown_count": float(strong_unknown_count),
            "avg_rssi": avg_rssi,
            "max_rssi": max_rssi,
            "min_rssi": min_rssi,
            "channel_spread": channel_spread,
        }

    def explain(self, features: dict[str, float], networks: list[dict[str, Any]]) -> list[str]:
        reasons: list[str] = []
        known_bssids = self.baseline["known_bssids"]
        ssid_to_bssids = self.baseline["ssid_to_bssids"]

        suspicious_twins = sorted(
            {
                net["ssid"]
                for net in networks
                if net["ssid"] in ssid_to_bssids and net["bssid"] not in known_bssids
            }
        )
        if suspicious_twins:
            reasons.append(
                "Known SSID appeared from an unknown BSSID: "
                + ", ".join(suspicious_twins[:3])
            )
        if features["strong_unknown_count"] > 0:
            reasons.append("A new access point has unusually strong signal near the scanner.")
        if features["duplicate_ssid_count"] > 0:
            reasons.append("Duplicate SSID names are visible in the same scan window.")
        if features["open_network_count"] > 0:
            reasons.append("One or more open Wi-Fi networks are present near trusted networks.")
        if features["new_ssid_count"] >= 3:
            reasons.append("Several new SSIDs appeared compared with the saved baseline.")
        if features["unknown_bssid_count"] >= 5:
            reasons.append("Many unknown BSSIDs appeared in one scan.")
        return reasons[:5]

    def heuristic_risk(self, features: dict[str, float]) -> int:
        score = 5
        score += features["known_ssid_unknown_bssid_count"] * 32
        score += features["strong_unknown_count"] * 18
        score += features["duplicate_ssid_count"] * 14
        score += features["open_network_count"] * 8
        score += min(features["new_ssid_count"], 6) * 6
        score += min(features["unknown_bssid_count"], 8) * 4
        return clamp(score)

    def ml_risk(self, features: dict[str, float]) -> int | None:
        if self.model is None:
            return None
        vector = np.array([[features[name] for name in FEATURE_NAMES]], dtype=float)
        prediction = int(self.model.predict(vector)[0])
        score = float(self.model.score_samples(vector)[0])
        # IsolationForest score_samples is higher for normal samples. This mapping is
        # intentionally simple for a predictable classroom demo.
        mapped = 100 - ((score + 0.72) / 0.18 * 100)
        if prediction == -1:
            mapped = max(mapped, 72)
        return clamp(mapped)

    def classify(self, risk_score: int, reasons: list[str]) -> tuple[str, str]:
        joined = " ".join(reasons).lower()
        if risk_score >= 70:
            if "known ssid" in joined or "duplicate ssid" in joined:
                return "ALERT", "Possible evil twin or rogue access point"
            return "ALERT", "Suspicious Wi-Fi environment change"
        if risk_score >= 40:
            return "WATCH", "Environment drift detected"
        return "SAFE", "Normal Wi-Fi environment"

    def latest(self) -> dict[str, Any]:
        if self.latest_path.exists():
            return self._load_json(self.latest_path)
        return {
            "status": "READY",
            "risk_score": 0,
            "threat": "Waiting for ESP32 or demo scan",
            "reasons": ["Start with Seed Demo Baseline, then run a normal or attack demo."],
            "networks": [],
            "features": {},
            "model_status": self.model_status,
            "baseline_count": len(self.baseline["known_bssids"]),
        }

    def demo_scan(self, attack: bool = False) -> dict[str, Any]:
        baseline = [
            {
                "ssid": "Campus-Lab",
                "bssid": "A4:2B:B0:11:22:33",
                "rssi": -48,
                "channel": 6,
                "encryption": "WPA2",
            },
            {
                "ssid": "Library-WiFi",
                "bssid": "B8:27:EB:44:55:66",
                "rssi": -63,
                "channel": 11,
                "encryption": "WPA2",
            },
            {
                "ssid": "Project-Room",
                "bssid": "C0:FF:EE:77:88:99",
                "rssi": -57,
                "channel": 1,
                "encryption": "WPA2",
            },
        ]
        if attack:
            baseline.extend(
                [
                    {
                        "ssid": "Campus-Lab",
                        "bssid": "DE:AD:BE:EF:10:01",
                        "rssi": -31,
                        "channel": 11,
                        "encryption": "OPEN",
                    },
                    {
                        "ssid": "Free-Campus-WiFi",
                        "bssid": "DE:AD:BE:EF:10:02",
                        "rssi": -35,
                        "channel": 11,
                        "encryption": "OPEN",
                    },
                ]
            )
        return {
            "device_id": "demo-scanner",
            "networks": baseline,
            "timestamp_ms": now_ms(),
        }

    def _result(
        self,
        device_id: str,
        networks: list[dict[str, Any]],
        risk_score: int,
        status: str,
        threat: str,
        reasons: list[str],
        features: dict[str, float],
        ml_score: int | None,
    ) -> dict[str, Any]:
        return {
            "device_id": device_id,
            "timestamp_ms": now_ms(),
            "status": status,
            "risk_score": risk_score,
            "threat": threat,
            "top_reason": reasons[0] if reasons else "No unusual behavior found.",
            "reasons": reasons,
            "features": features,
            "networks": networks,
            "ml_score": ml_score,
            "model_status": self.model_status,
            "baseline_count": len(self.baseline["known_bssids"]),
        }

    def _persist_result(self, result: dict[str, Any]) -> None:
        self._save_json(self.latest_path, result)
        with self.events_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(result) + "\n")

    def _load_model(self) -> Any:
        if self.model_path.exists():
            return joblib.load(self.model_path)
        return None

    def _empty_baseline(self) -> dict[str, Any]:
        return {"known_bssids": {}, "ssid_to_bssids": {}, "updated_at": None}

    def _load_baseline(self) -> dict[str, Any]:
        if self.baseline_path.exists():
            return self._load_json(self.baseline_path)
        return self._empty_baseline()

    def _load_json(self, path: Path) -> dict[str, Any]:
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _save_json(self, path: Path, data: dict[str, Any]) -> None:
        with path.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)
