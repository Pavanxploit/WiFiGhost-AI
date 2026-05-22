from __future__ import annotations

from pathlib import Path
import os
from typing import Any

from flask import Flask, jsonify, render_template, request

try:
    from .detector import WifiGhostDetector
except ImportError:
    from detector import WifiGhostDetector


ROOT = Path(__file__).resolve().parents[1]
app = Flask(__name__)
detector = WifiGhostDetector(ROOT)


@app.get("/")
def index() -> str:
    return render_template("index.html")


@app.get("/api/status")
def status() -> Any:
    return jsonify(detector.latest())


@app.post("/api/scan")
def scan() -> Any:
    payload = request.get_json(silent=True) or {}
    result = detector.analyze_payload(payload, learn=request.args.get("learn") == "1")
    return jsonify(result)


@app.post("/api/baseline/learn")
def learn_baseline() -> Any:
    payload = request.get_json(silent=True) or {}
    networks = payload.get("networks")
    if not networks:
        latest = detector.latest()
        networks = latest.get("networks", [])
    baseline = detector.learn_baseline(networks)
    return jsonify(
        {
            "message": "Baseline saved",
            "baseline_count": len(baseline["known_bssids"]),
            "ssid_count": len(baseline["ssid_to_bssids"]),
        }
    )


@app.post("/api/demo/seed")
def demo_seed() -> Any:
    baseline = detector.seed_demo_baseline()
    return jsonify(
        {
            "message": "Demo baseline loaded",
            "baseline_count": len(baseline["known_bssids"]),
        }
    )


@app.post("/api/demo/normal")
def demo_normal() -> Any:
    return jsonify(detector.analyze_payload(detector.demo_scan(attack=False)))


@app.post("/api/demo/attack")
def demo_attack() -> Any:
    return jsonify(detector.analyze_payload(detector.demo_scan(attack=True)))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
