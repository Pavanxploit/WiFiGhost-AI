#include <Adafruit_GFX.h>
#include <Adafruit_ILI9341.h>
#include <HTTPClient.h>
#include <SPI.h>
#include <WiFi.h>

#include "secrets.h"

#define TFT_CS 5
#define TFT_DC 21
#define TFT_RST 22

#define TFT_MOSI 23
#define TFT_MISO 19
#define TFT_SCLK 18

const unsigned long SCAN_INTERVAL_MS = 7000;

Adafruit_ILI9341 tft(TFT_CS, TFT_DC, TFT_RST);

String jsonEscape(const String& value) {
  String escaped = "";
  for (size_t i = 0; i < value.length(); i++) {
    char c = value.charAt(i);
    if (c == '"' || c == '\\') {
      escaped += '\\';
    }
    if (c >= 32) {
      escaped += c;
    }
  }
  return escaped;
}

String authModeName(wifi_auth_mode_t auth) {
  switch (auth) {
    case WIFI_AUTH_OPEN:
      return "OPEN";
    case WIFI_AUTH_WEP:
      return "WEP";
    case WIFI_AUTH_WPA_PSK:
      return "WPA";
    case WIFI_AUTH_WPA2_PSK:
      return "WPA2";
    case WIFI_AUTH_WPA_WPA2_PSK:
      return "WPA/WPA2";
    case WIFI_AUTH_WPA2_ENTERPRISE:
      return "WPA2-ENT";
#ifdef WIFI_AUTH_WPA3_PSK
    case WIFI_AUTH_WPA3_PSK:
      return "WPA3";
#endif
#ifdef WIFI_AUTH_WPA2_WPA3_PSK
    case WIFI_AUTH_WPA2_WPA3_PSK:
      return "WPA2/WPA3";
#endif
    default:
      return "UNKNOWN";
  }
}

int extractJsonInt(const String& json, const String& key, int fallback) {
  String searchKey = String("\"") + key + "\"";
  int keyIndex = json.indexOf(searchKey);
  if (keyIndex < 0) return fallback;
  int colonIndex = json.indexOf(':', keyIndex);
  if (colonIndex < 0) return fallback;

  int start = colonIndex + 1;
  while (start < json.length() && json.charAt(start) == ' ') start++;

  String number = "";
  while (start < json.length()) {
    char c = json.charAt(start);
    if (!isDigit(c) && c != '-') break;
    number += c;
    start++;
  }

  return number.length() ? number.toInt() : fallback;
}

String extractJsonString(const String& json, const String& key, const String& fallback) {
  String searchKey = String("\"") + key + "\"";
  int keyIndex = json.indexOf(searchKey);
  if (keyIndex < 0) return fallback;
  int colonIndex = json.indexOf(':', keyIndex);
  if (colonIndex < 0) return fallback;
  int quoteStart = json.indexOf('"', colonIndex + 1);
  if (quoteStart < 0) return fallback;
  int quoteEnd = json.indexOf('"', quoteStart + 1);
  if (quoteEnd < 0) return fallback;
  return json.substring(quoteStart + 1, quoteEnd);
}

void drawHeader(const String& subtitle) {
  tft.fillScreen(ILI9341_BLACK);
  tft.setTextColor(ILI9341_CYAN);
  tft.setTextSize(2);
  tft.setCursor(12, 12);
  tft.print("WiFiGhost AI");
  tft.setTextColor(ILI9341_LIGHTGREY);
  tft.setTextSize(1);
  tft.setCursor(12, 38);
  tft.print(subtitle);
}

void drawCenteredStatus(const String& status, int color, int risk, const String& reason) {
  drawHeader("ESP32 rogue AP monitor");
  tft.fillRoundRect(18, 62, 284, 96, 8, color);
  tft.setTextColor(ILI9341_BLACK);
  tft.setTextSize(3);
  tft.setCursor(34, 82);
  tft.print(status);
  tft.setTextSize(2);
  tft.setCursor(34, 120);
  tft.print("Risk: ");
  tft.print(risk);
  tft.print("%");

  tft.setTextColor(ILI9341_WHITE);
  tft.setTextSize(1);
  tft.setCursor(12, 178);
  tft.print(reason.substring(0, 45));
  if (reason.length() > 45) {
    tft.setCursor(12, 194);
    tft.print(reason.substring(45, 90));
  }
}

void drawNetworkCount(int count) {
  tft.fillRect(0, 218, 320, 22, ILI9341_DARKGREY);
  tft.setCursor(12, 225);
  tft.setTextColor(ILI9341_WHITE);
  tft.setTextSize(1);
  tft.print("Networks scanned: ");
  tft.print(count);
}

void connectWiFi() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  drawHeader("Connecting to Wi-Fi...");

  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    tft.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    drawHeader("Connected");
    tft.setCursor(12, 64);
    tft.setTextColor(ILI9341_WHITE);
    tft.setTextSize(1);
    tft.print(WiFi.localIP());
    delay(1200);
  } else {
    drawCenteredStatus("NO WIFI", ILI9341_ORANGE, 0, "Check SSID/password in secrets.h");
    delay(2500);
  }
}

String buildScanPayload(int networkCount) {
  String payload = "{\"device_id\":\"esp32-devkit-v1\",\"networks\":[";

  for (int i = 0; i < networkCount; i++) {
    if (i > 0) payload += ",";
    payload += "{";
    payload += "\"ssid\":\"";
    payload += jsonEscape(WiFi.SSID(i));
    payload += "\",";
    payload += "\"bssid\":\"";
    payload += WiFi.BSSIDstr(i);
    payload += "\",";
    payload += "\"rssi\":";
    payload += String(WiFi.RSSI(i));
    payload += ",";
    payload += "\"channel\":";
    payload += String(WiFi.channel(i));
    payload += ",";
    payload += "\"encryption\":\"";
    payload += authModeName(WiFi.encryptionType(i));
    payload += "\"";
    payload += "}";
  }

  payload += "]}";
  return payload;
}

void postScan(const String& payload, int networkCount) {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
  }

  HTTPClient http;
  http.begin(API_URL);
  http.addHeader("Content-Type", "application/json");
  int code = http.POST(payload);
  String response = http.getString();
  http.end();

  if (code <= 0) {
    drawCenteredStatus("API ERR", ILI9341_ORANGE, 0, "Backend not reachable. Check laptop IP and Flask server.");
    drawNetworkCount(networkCount);
    Serial.println(payload);
    return;
  }

  int risk = extractJsonInt(response, "risk_score", 0);
  String status = extractJsonString(response, "status", "READY");
  String reason = extractJsonString(response, "top_reason", "Scan sent to backend.");

  int color = ILI9341_GREEN;
  if (status == "ALERT") color = ILI9341_RED;
  else if (status == "WATCH") color = ILI9341_ORANGE;
  else if (status == "LEARNING") color = ILI9341_CYAN;

  drawCenteredStatus(status, color, risk, reason);
  drawNetworkCount(networkCount);

  Serial.println(response);
}

void setup() {
  Serial.begin(115200);
  SPI.begin(TFT_SCLK, TFT_MISO, TFT_MOSI, TFT_CS);
  tft.begin();
  tft.setRotation(1);
  connectWiFi();
}

void loop() {
  drawHeader("Scanning nearby Wi-Fi...");
  int networkCount = WiFi.scanNetworks(false, true);

  if (networkCount < 0) {
    drawCenteredStatus("SCAN ERR", ILI9341_ORANGE, 0, "ESP32 Wi-Fi scan failed. Retrying.");
  } else {
    String payload = buildScanPayload(networkCount);
    postScan(payload, networkCount);
  }

  WiFi.scanDelete();
  delay(SCAN_INTERVAL_MS);
}
