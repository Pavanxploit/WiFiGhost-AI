# ESP32 and TFT Wiring Guide

## Display choice

Pick the **2.8 inch TFT SPI 240x320 V1.2** display from your photo.

Why:

- It has SPI pins, so it matches ESP32 well.
- It needs fewer wires than the Arduino shield display.
- It works with common Arduino libraries like `Adafruit_ILI9341`.

Avoid the Arduino-style shield for this one-day build because it is made for Uno pin layout and usually consumes many GPIO pins.

## Pin table

| TFT label | Meaning | ESP32 connection |
| --- | --- | --- |
| VCC | Power | 3V3 |
| GND | Ground | GND |
| CS | Chip select | GPIO5 / D5 |
| RESET | Reset | GPIO22 / D22 |
| D/C | Data/command | GPIO21 / D21 |
| SDI | MOSI data input | GPIO23 / D23 |
| SCK | SPI clock | GPIO18 / D18 |
| SDO | MISO data output | GPIO19 / D19 |
| LED | Backlight | 3V3 |

The touch pins `T_IRQ`, `T_DO`, `T_DIN`, `T_CS`, and `T_CLK` are not used in the current firmware.

## Power notes

- Use `3V3` for TFT `VCC` first. It is safest for ESP32 logic.
- Connect all grounds together.
- If the display backlight stays off, check the `LED` pin. It usually needs `3V3`.
- Do not connect ESP32 GPIO pins to 5V logic.

## Arduino IDE settings

- Board: ESP32 Dev Module
- Upload speed: 115200 or 921600
- Partition scheme: Default
- Required libraries:
  - Adafruit GFX Library
  - Adafruit ILI9341

## Laptop IP address

Find your laptop IP:

```powershell
ipconfig
```

Look for the IPv4 address under your Wi-Fi adapter. Use it in `secrets.h`:

```cpp
const char* API_URL = "http://192.168.x.x:5000/api/scan";
```
