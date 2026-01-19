# Functional Specification Document (FSD)

## 1. Overview
- ESP32-based weight module for a robotic drink system (e.g., mojito maker).
- Hardware: 1 kg load cell with HX711 amplifier, ultrasonic sensor HC-SR04 for glass presence detection, Ethernet (static IP).
- Provides local HTTP/REST (Mongoose/Wizard) for monitoring/configuration; measured throughput with the test script ~5–10 Hz. Networking currently defaults to DHCP; static IP would need to be set in code.
- A future MQTT-based variant is planned in a separate project (out of scope here).

## 2. Scope
- In scope: sensor reading, calibration, glass detection threshold, tare, web UI/REST API, settings persistence.
- Out of scope: cocktail orchestration logic, payment/auth integration, cloud connectivity. Static-IP handling is not implemented; DHCP is used by default. MQTT migration is ein externes/angegliedertes Projekt, nicht Teil dieses Repos.

## 3. Functional Requirements
### 3.1 Sensor Behavior
- Measure weight from load cell in grams (grams only) with configurable offset and multiplier (calibration factor).
- Detect glass presence via ultrasonic sensor with configurable distance threshold (mm). Glass state is boolean.
- Provide a tare action that zeroes the current weight reading and stores the offset for the current session only (not persisted).

### 3.2 Web Dashboard / REST (local)
- Status view shows live values: weight (g), ultrasonic distance (mm), glass detected (bool), network status.
- Controls:
  - Tare button to zero the scale (REST endpoint `/api/tare`).
  - Refresh/auto-refresh of sensor readings (REST endpoints `/api/weight`, `/api/status`, `/api/glass`).
- Settings:
  - Glass detection threshold distance input (mm).
  - Load cell calibration: offset and multiplier inputs; apply/save.
  - Device identity: device name input.
  - Logging: selectable log level (e.g., ERROR/WARN/INFO/DEBUG).
  - Network: static IP, subnet mask, gateway, DNS; no DHCP option.
- Persist settings in non-volatile storage; values survive reboot and power loss.
- Validation: reject obviously invalid IP/mask/gateway/DNS entries and non-numeric calibration/threshold values.
- Throughput: REST polling mit dem Testskript erreicht ca. 5–10 Hz (bekannte Grenze).

### 3.4 Configuration & Persistence
- Store all settings (glass threshold, calibration offset/multiplier, device name, log level, static IP config, MQTT broker/credentials/topics) in NVS/flash.
- Apply network settings after save; reboot if required.
- On boot, load persisted settings; fall back to safe defaults if missing/corrupt.
- Tare offset applies for the current session only and is not persisted across reboot.

## 4. Non-Functional Requirements
- Reliability: readings update at least 5 Hz intern; REST-Testskript erreicht ca. 5–10 Hz Abfragefrequenz.
- Accuracy: weight resolution ~1 g; glass detection reliable within configured threshold.
- Latency: REST responses < 200 ms auf LAN unter Normalbedingungen (innerhalb der 5–10 Hz Polling-Grenze).
- Availability: device should recover to last good config after power cycle.
- Security: LAN-only; keine Auth, kein Cloud-Egress.
- Logging: include sensor read errors, calibration changes, network changes.

## 5. Error Handling
- If a sensor read fails, return last known good value plus an error flag; surface warning in UI/REST response.
- Validation errors return 400 with message; unknown routes return 404.
- On storage failure, operate with defaults and show warning in UI/status endpoint.

## 6. Assumptions
- Single client at a time is sufficient; simple locking around tare/calibration is enough.
- Static IP only; no DHCP fallback needed.
- Time source: device clock (no NTP assumed); timestamps may be relative if RTC/NTP unavailable.

## 7. Open Questions
- Bedarf für Auth/ACL auf REST-Ebene?
- Soll die spätere MQTT-Variante Topic-/Broker-Config flexibel halten?

## 8. Acceptance Criteria
- Web UI/REST zeigt live weight, distance, glass state; tare funktioniert und aktualisiert die Anzeige.
- Settings (glass threshold, calibration offset/multiplier, device name, log level, static IP/mask/gateway/DNS) können editiert, validiert, gespeichert werden und überstehen einen Reboot.
- REST-Endpoints antworten wie spezifiziert; Polling mit Testskript erreicht ~5–10 Hz.
- Power cycle retains settings; device boots with valid network config and serves UI/API.

## 9. Pinout
- SPI (ETH): GPIO11 MOSI, GPIO12 MISO, GPIO13 SCK, GPIO14 CS, GPIO9 RST, GPIO10 INT
- HX711: GPIO35 DT, GPIO36 SCK
- HC-SR04: GPIO37 TRIG, GPIO38 ECHO
