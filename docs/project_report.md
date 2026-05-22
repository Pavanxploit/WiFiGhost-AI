# WiFiGhost AI: ML-Based Rogue Access Point Detection Using ESP32 and TFT Display

## Abstract

WiFiGhost AI is an IoT and machine learning based cybersecurity prototype designed to detect suspicious Wi-Fi access points in a local environment. The system uses an ESP32 as a low-cost wireless scanner, a 2.8 inch SPI TFT display as an embedded alert screen, and a Flask-based dashboard for monitoring and analysis. The ESP32 collects SSID, BSSID, RSSI, channel, and encryption details from nearby Wi-Fi networks and sends them to a backend server. The backend extracts features and applies an Isolation Forest model along with cybersecurity rules to detect rogue access points, evil twin SSIDs, suspicious open hotspots, and abnormal Wi-Fi environment changes.

The project demonstrates how IoT devices can be used not only for sensing physical values, but also for cyber-physical security monitoring. The final output is a risk score and status such as SAFE, WATCH, or ALERT, visible on both the dashboard and the TFT display.

## Keywords

IoT, ESP32, machine learning, cybersecurity, rogue access point, evil twin, Wi-Fi scanning, anomaly detection, Flask, Isolation Forest.

## 1. Introduction

Wireless networks are widely used in colleges, laboratories, hostels, offices, and public spaces. Most users identify a Wi-Fi network by its SSID name, but an SSID can easily be copied. A fake hotspot can use the same name as a trusted network and trick users into connecting. This type of attack is commonly known as a rogue access point or evil twin scenario.

WiFiGhost AI is built to monitor this risk. Instead of attacking any network, it passively scans the surrounding Wi-Fi environment and detects whether the visible access points look normal or suspicious. The project combines three domains:

- IoT: ESP32 scans the wireless environment and shows embedded alerts.
- Machine Learning: Isolation Forest identifies abnormal scan behavior.
- Cybersecurity: The system focuses on rogue AP and evil twin detection.

## 2. Problem Statement

Users often trust a Wi-Fi network name without verifying the physical access point behind it. If a fake access point appears with the same SSID as a known network, users may connect to it and expose credentials, browsing activity, or internal traffic. Small campuses and labs usually do not have expensive wireless intrusion detection systems.

The problem is to design a low-cost prototype that can observe nearby Wi-Fi networks, learn a normal baseline, and alert when suspicious access point behavior is detected.

## 3. Objectives

- Build an ESP32-based IoT scanner for nearby Wi-Fi networks.
- Use a TFT display to show live security status and risk score.
- Create a web dashboard for monitoring scan results.
- Train and use an ML model to classify abnormal Wi-Fi environments.
- Detect defensive cybersecurity scenarios such as rogue AP, evil twin SSID, and open hotspot bait.
- Provide a safe classroom demo without performing real Wi-Fi attacks.

## 4. Scope of the Project

This project is a defensive monitoring prototype. It does not crack Wi-Fi passwords, deauthenticate clients, intercept traffic, or perform offensive actions. It only scans public beacon information already broadcast by nearby Wi-Fi access points.

The system is suitable for:

- classroom demonstration
- lab network awareness
- campus security concept prototype
- IoT and ML integration project
- cybersecurity awareness demonstration

## 5. Hardware and Software Requirements

### Hardware

| Component | Purpose |
| --- | --- |
| ESP32 DevKit | Wi-Fi scanning and HTTP communication |
| 2.8 inch SPI TFT Display | Embedded status and risk display |
| Breadboard and jumper wires | Wiring and prototyping |
| Laptop | ML backend and web dashboard |
| Mobile hotspot | Safe rogue AP simulation |

### Software

| Software | Purpose |
| --- | --- |
| Arduino IDE | Upload ESP32 firmware |
| Python | Run backend and ML scripts |
| Flask | Web API and dashboard |
| scikit-learn | Isolation Forest anomaly detection |
| Adafruit GFX and ILI9341 libraries | TFT display control |

## 6. Proposed System

The proposed system has three major layers:

1. Edge IoT Layer: ESP32 scans nearby Wi-Fi access points.
2. ML Detection Layer: Flask backend extracts features and scores risk.
3. Alert Layer: Dashboard and TFT display show status, threat, and reasons.

### System Architecture

```text
Nearby Wi-Fi Access Points
           |
           v
ESP32 Wi-Fi Scanner + TFT Display
           |
           | HTTP JSON scan
           v
Flask API + Isolation Forest Detector
           |
           +--> Web Dashboard
           |
           +--> Risk Response to ESP32 TFT
```

## 7. Working Methodology

The ESP32 performs periodic Wi-Fi scans. For each access point, it records:

- SSID
- BSSID or MAC address
- RSSI signal strength
- Wi-Fi channel
- encryption type

This scan is sent as JSON to the Flask backend. The backend normalizes the values and compares the current scan with a saved baseline. The baseline represents the trusted or normal Wi-Fi environment.

The backend extracts numerical features such as:

- number of visible access points
- unknown BSSID count
- new SSID count
- duplicate SSID count
- open network count
- strong unknown access point count
- average RSSI
- maximum RSSI
- channel spread

These features are passed to an Isolation Forest model. A rule-based cybersecurity score is also calculated for clear attack-like behavior. The final risk score is the stronger signal from both ML and rules.

## 8. Machine Learning Model

The project uses Isolation Forest, an unsupervised anomaly detection algorithm. It is suitable because the system mainly knows what normal Wi-Fi behavior looks like, but it may not have many examples of all possible attacks.

### Why Isolation Forest?

- It works with unlabeled or mostly normal data.
- It is lightweight and fast enough for a project backend.
- It is designed for anomaly detection.
- It gives a practical way to detect unusual Wi-Fi scan patterns.

### Feature Vector

```text
[ap_count,
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
 channel_spread]
```

## 9. Cybersecurity Detection Logic

WiFiGhost AI detects the following suspicious situations:

| Threat | Detection idea |
| --- | --- |
| Evil twin SSID | Known SSID appears from unknown BSSID |
| Rogue AP | New strong access point appears near trusted networks |
| Open hotspot bait | Open network appears with strong signal |
| Environment drift | Many new SSIDs or BSSIDs appear suddenly |
| Duplicate SSID confusion | Same SSID appears multiple times unexpectedly |

The system shows a status:

- SAFE: normal Wi-Fi environment
- WATCH: slight change or drift
- ALERT: high-risk suspicious behavior

## 10. Implementation

### ESP32 Firmware

The firmware uses ESP32 Wi-Fi scanning APIs and sends scan results to the backend using HTTP POST. It also receives a response containing risk score, status, and reason. These values are displayed on the TFT screen.

### Backend

The Flask backend provides:

- `/api/scan` for ESP32 scan uploads
- `/api/status` for dashboard updates
- `/api/demo/normal` for safe normal demo
- `/api/demo/attack` for safe rogue AP simulation
- `/api/demo/seed` to load demo baseline

### Dashboard

The dashboard displays:

- current status
- risk score
- detected threat
- detection reasons
- visible access points
- feature counts

## 11. Hardware Connection

The recommended display is the 2.8 inch SPI TFT module. It is preferred over the Arduino shield display because it exposes standard SPI pins and is easier to connect with ESP32.

| TFT Pin | ESP32 Pin |
| --- | --- |
| VCC | 3V3 |
| GND | GND |
| CS | GPIO5 |
| RESET | GPIO22 |
| D/C | GPIO21 |
| SDI / MOSI | GPIO23 |
| SCK | GPIO18 |
| SDO / MISO | GPIO19 |
| LED | 3V3 |

Touch pins are not required for the current version.

## 12. Demonstration Plan

1. Start the Flask backend and open the dashboard.
2. Click Seed baseline to load the normal Wi-Fi environment.
3. Click Normal scan and show SAFE status.
4. Click Rogue AP demo or turn on a phone hotspot.
5. Show the dashboard changing to ALERT.
6. Explain the detection reason: known SSID with unknown BSSID or strong open hotspot.
7. Show the ESP32 TFT risk output if hardware is connected.

## 13. Results

During testing, the normal demo scan produced SAFE status with a low risk score. The rogue AP demo produced ALERT status with a high risk score. The dashboard clearly displayed the reason: a known SSID appeared from an unknown BSSID.

### Sample Output

```text
Normal scan:
Status: SAFE
Risk score: 5
Threat: Normal Wi-Fi environment

Rogue AP demo:
Status: ALERT
Risk score: 100
Threat: Possible evil twin or rogue access point
Reason: Known SSID appeared from an unknown BSSID
```

## 14. Advantages

- Low-cost hardware implementation.
- Combines IoT, ML, and cybersecurity.
- Does not require extra sensors.
- Uses real wireless environment data.
- Safe for classroom demonstration.
- Dashboard and embedded TFT make the project visually presentable.

## 15. Limitations

- The prototype detects suspicious patterns but does not prove malicious intent.
- Accuracy depends on the baseline quality.
- Crowded Wi-Fi areas may create false positives.
- ESP32 scanning is periodic, not continuous.
- It does not inspect encrypted traffic or connected clients.

## 16. Future Enhancements

- Add SQLite storage for historical event logs.
- Add Telegram or email alerts.
- Add location-based baselines for different rooms.
- Add battery-powered enclosure for portable scanning.
- Add touch controls on the TFT display.
- Improve the model with real campus scan data.
- Add MAC vendor lookup and channel congestion analysis.

## 17. Conclusion

WiFiGhost AI successfully demonstrates a unique IoT, ML, and cybersecurity project using affordable hardware. The ESP32 acts as a wireless environment sensor, the Flask backend performs anomaly detection, and the TFT display provides embedded alerts. The project is practical, safe to demonstrate, and different from common IoT projects such as smart irrigation or basic attendance systems. It shows how machine learning can be used to improve wireless security awareness in campuses, labs, and small organizations.

## References

1. F. T. Liu, K. M. Ting, and Z. H. Zhou, "Isolation Forest," IEEE International Conference on Data Mining, 2008.
2. Espressif Systems, ESP32 Wi-Fi API documentation.
3. scikit-learn documentation, IsolationForest.
4. Flask documentation, web application framework.
5. Adafruit ILI9341 and Adafruit GFX library documentation.
