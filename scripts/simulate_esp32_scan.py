from __future__ import annotations

import argparse
import json
from urllib.request import Request, urlopen


NORMAL_SCAN = {
    "device_id": "simulated-esp32",
    "networks": [
        {
            "ssid": "Campus-Lab",
            "bssid": "A4:2B:B0:11:22:33",
            "rssi": -49,
            "channel": 6,
            "encryption": "WPA2",
        },
        {
            "ssid": "Library-WiFi",
            "bssid": "B8:27:EB:44:55:66",
            "rssi": -62,
            "channel": 11,
            "encryption": "WPA2",
        },
        {
            "ssid": "Project-Room",
            "bssid": "C0:FF:EE:77:88:99",
            "rssi": -56,
            "channel": 1,
            "encryption": "WPA2",
        },
    ],
}

ATTACK_SCAN = {
    "device_id": "simulated-esp32",
    "networks": NORMAL_SCAN["networks"]
    + [
        {
            "ssid": "Campus-Lab",
            "bssid": "DE:AD:BE:EF:10:01",
            "rssi": -30,
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
    ],
}


def post_json(url: str, payload: dict) -> dict:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Send a fake ESP32 scan to WiFiGhost AI.")
    parser.add_argument("--attack", action="store_true", help="Send a rogue AP / evil twin scan.")
    parser.add_argument("--learn", action="store_true", help="Save this scan as baseline first.")
    parser.add_argument("--url", default="http://127.0.0.1:5000/api/scan")
    args = parser.parse_args()

    payload = ATTACK_SCAN if args.attack else NORMAL_SCAN
    url = args.url + ("?learn=1" if args.learn else "")
    result = post_json(url, payload)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
