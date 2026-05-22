# Demo Plan

## Title

WiFiGhost AI: ML-Based Rogue Access Point Detection Using ESP32 and TFT Display

## Problem

Students and employees often connect to Wi-Fi networks by SSID name. Attackers can create a fake hotspot with the same SSID or a tempting open SSID. This project detects suspicious Wi-Fi environment changes instead of blindly trusting the network name.

## Components

- ESP32 DevKit
- 2.8 inch SPI TFT display
- Laptop running Flask dashboard and ML model
- Phone hotspot for safe rogue AP simulation

## Demo script

1. Open the dashboard at `http://127.0.0.1:5000`.
2. Click `Seed baseline`.
3. Click `Normal scan`.
4. Explain that the system learned known SSIDs and BSSIDs.
5. Click `Rogue AP demo` or turn on a phone hotspot with a similar SSID.
6. Show the dashboard changing to `ALERT`.
7. Show the ESP32 TFT displaying risk score and reason.

## Expected result

Normal scan:

```text
Status: SAFE
Threat: Normal Wi-Fi environment
Risk: low
```

Rogue AP scan:

```text
Status: ALERT
Threat: Possible evil twin or rogue access point
Reason: Known SSID appeared from an unknown BSSID
Risk: high
```

## ML explanation

The model uses Isolation Forest. It learns normal scan features:

- access point count
- unknown BSSID count
- new SSID count
- duplicate SSID count
- open network count
- signal strength range
- channel spread

When the feature vector moves away from normal behavior, the model increases risk.

## Cybersecurity scope

This project does not attack Wi-Fi networks. It detects suspicious wireless access points and helps users avoid rogue AP and evil twin risks.
