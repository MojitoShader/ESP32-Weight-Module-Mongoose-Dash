# ESP32 Weight Module (ESP32-S3, HX711, W5500, HTTP/REST)

ESP32-S3 basierte Gewichtseinheit mit HX711-Load-Cell, HC-SR04-Glaserkennung und W5500-Ethernet. Das UI/REST-Backend wurde mit dem Mongoose Wizard (https://mongoose.ws/wizard/) generiert; ergänzt wurden nur die Sensoranbindung und wenige Bindings. Eine MQTT-Variante wird in einem anderen Projekt umgesetzt. Mit der REST-API und dem Testskript wurden ca. 5–10 Hz erreicht – für strengere Echtzeit-Anforderungen sollte auf MQTT gewechselt werden (nicht Teil dieses Repos).

## Features
- Gewichtserfassung (g) mit konfigurierbarem Offset/Scale (Kalibrierung).
- Glaserkennung per Ultraschall mit einstellbarer Schwelle (mm).
- Tare per REST-Aufruf.
- REST-/Wizard-API über Mongoose; gemessene Rate mit Testskript ca. 5–10 Hz.

## Hardware
- Board: ESP32-S3
- Ethernet: W5500 SPI (SCK 13, MISO 12, MOSI 11, CS 14, RST 9, INT 10).
- Load cell: HX711 (DT 35, SCK 36).
- HC-SR04: TRIG 37, ECHO 38.

## Build & Flash (PlatformIO)
```
pio run
pio run -t upload
pio run -t monitor
```
- Port in `platformio.ini` anpassen (`upload_port = COM...`).
- Log-Level kann zur Laufzeit per Setting geändert werden (siehe MQTT).

## Netzwerk
- Aktueller Code nutzt DHCP (MG_TCPIP_IP = 0). Eine feste IP ist noch nicht verdrahtet – muss bei Bedarf im Code hinterlegt werden (z.B. MG_TCPIP_IP/MASK/GW setzen oder g_net_ip vor `mg_mgr_init()` füllen).

## REST Endpunkte (Custom)
- `GET /api/weight` → `{"weight_g":<float>,"timestamp":"<sec.msec>"}`
- `GET /api/glass` → `{"glass_present":true|false,"distance_mm":<float>,"timestamp":"..."}`  
- `POST /api/tare` → `{"status":"ok","offset_g":<float>}`
- `GET /api/status` → `{"weight_g":...,"glass_present":...,"distance_mm":...,"device_name":"...","ip":"..."}`  
Hinweis: Weitere generierte Wizard-APIs (state/settings/network_settings usw.) sind ebenfalls verfügbar.

## Performance-Hinweis
- Mit dem mitgelieferten REST-Testskript wurden ca. 5–10 Hz erreicht.

## Status & Roadmap
- Aktueller Stand: HTTP/REST über Mongoose
- MQTT-Variante wird in einem anderen Projekt entwickelt (nicht Teil dieses Repos).

## Tests
- Sensor/GPIO-Tests unter `test/` (HX711/HC-SR04 GUI-Skripte).
