# Project Report

## Abstract

WiFiGhost AI is an IoT and machine learning based wireless security prototype. An ESP32 scans nearby Wi-Fi access points and sends SSID, BSSID, RSSI, channel, and encryption information to a Flask backend. The backend extracts behavior features and uses an Isolation Forest model with rule-based cybersecurity checks to detect rogue access points, evil twin SSIDs, and abnormal changes in the local Wi-Fi environment. Results are displayed on a web dashboard and returned to the ESP32 TFT display as a risk score.

## Objective

To design a low-cost IoT security monitor that can detect suspicious Wi-Fi access point behavior using ML and display alerts on both a dashboard and an embedded TFT screen.

## Existing problem

Normal users often identify Wi-Fi networks by SSID only. SSID names can be copied easily. A fake access point with a trusted-looking name may trick users into connecting. Traditional attendance, door lock, and IoT projects usually focus on access control, but this project focuses on wireless environment trust.

## Proposed system

The proposed system has three layers:

1. ESP32 scanner layer: collects nearby Wi-Fi access point information.
2. ML detection layer: extracts features and calculates anomaly risk.
3. Alert layer: shows status on a web dashboard and TFT display.

## Methodology

The system stores a baseline of known Wi-Fi access points. During each scan it compares the current environment with the baseline and calculates features such as unknown BSSID count, duplicate SSID count, open network count, strong unknown AP count, and signal strength spread. An Isolation Forest model is trained on normal feature patterns. The final risk score combines ML anomaly scoring with cybersecurity rules.

## Result

The prototype can classify a normal scan as safe and a simulated rogue AP or evil twin scan as alert. A phone hotspot or dashboard demo button can be used to simulate a suspicious access point safely.

## Future enhancement

- Add GPS or room labels for location-aware baselines.
- Store long-term events in SQLite.
- Add email or Telegram alerting.
- Add battery-powered enclosure for portable scanning.
- Add touch controls on the TFT display.
