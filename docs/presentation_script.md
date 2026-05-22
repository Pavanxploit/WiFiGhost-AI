# WiFiGhost AI Presentation Script

## Slide 1: Title

Good morning. My project is WiFiGhost AI, an ML-based rogue access point detection system using ESP32 and a TFT display. It combines IoT, machine learning, and cybersecurity.

## Slide 2: Problem

Most users trust Wi-Fi by looking only at the network name. But a fake hotspot can copy the same SSID as a real network. This can lead to evil twin or rogue access point attacks. My project tries to detect this suspicious Wi-Fi environment.

## Slide 3: Proposed Solution

The ESP32 scans nearby Wi-Fi networks. It sends SSID, BSSID, signal strength, channel, and encryption details to a Flask backend. The backend uses ML and security rules to calculate a risk score. The result is shown on a web dashboard and the TFT display.

## Slide 4: Architecture

The architecture has three layers: ESP32 scanner layer, ML detection backend, and alert display layer. The ESP32 is the IoT device, Flask is the server, and Isolation Forest is used for anomaly detection.

## Slide 5: Hardware

The hardware used is ESP32 DevKit, 2.8 inch SPI TFT display, jumper wires, breadboard, and laptop. I selected the SPI TFT because it is easier to connect with ESP32 than the Arduino shield display.

## Slide 6: ML Features

The ML model uses features such as access point count, unknown BSSID count, duplicate SSID count, open network count, signal strength, and channel spread. These values represent the behavior of the Wi-Fi environment.

## Slide 7: Cybersecurity Detection

The system detects situations like evil twin SSID, rogue access point, strong unknown hotspot, open network bait, and sudden environment drift. If a known SSID appears with a new BSSID, the system marks it as suspicious.

## Slide 8: Demo

First I load the baseline. Then I show a normal scan, which gives SAFE status. After that I run the rogue AP demo or turn on a phone hotspot. The system changes to ALERT and displays the reason and risk score.

## Slide 9: Results

In testing, normal scan gave SAFE status with low risk. Rogue AP demo gave ALERT status with high risk. The dashboard showed the reason as known SSID appeared from unknown BSSID.

## Slide 10: Conclusion

WiFiGhost AI is a low-cost defensive security prototype. It does not attack Wi-Fi networks. It only monitors the environment and detects suspicious access points. This makes it useful for cybersecurity awareness in colleges and labs.

## Short Viva Answers

**Why did you use ESP32?**  
ESP32 has built-in Wi-Fi, so it can scan nearby networks without an extra Wi-Fi module.

**Why Isolation Forest?**  
It is suitable for anomaly detection when mostly normal data is available.

**Is this a hacking tool?**  
No. It is a defensive monitoring tool. It only reads public Wi-Fi beacon information.

**What is an evil twin?**  
An evil twin is a fake access point that copies the name of a trusted Wi-Fi network.

**What is BSSID?**  
BSSID is the MAC address of the access point. Even if two networks have the same SSID, their BSSID can be different.

**What is the future scope?**  
Historical logs, alerts, location-based baselines, better ML training data, and portable enclosure.
