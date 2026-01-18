# Functional Specification Document (FSD)

## 1. Overview
- ESP32-based weight module for a robotic drink system (e.g., mojito maker).
- Hardware: 1 kg load cell with HX711 amplifier, ultrasonic sensor HC-SR04 for glass presence detection, Ethernet (Static IP) with Mongoose Dash UI.
- Provides local web dashboard (Mongoose Wizard standard) for monitoring/configuration and REST API for control.
- Consumers: other modules (e.g., ICE module) read weight and glass state and trigger tare.

## 2. Scope
- In scope: sensor reading, calibration, glass detection threshold, tare, web UI, REST API, settings persistence.
- Out of scope: cocktail orchestration logic, payment/auth integration, cloud connectivity, DHCP.

## 3. Functional Requirements
### 3.1 Sensor Behavior
- Measure weight from load cell in grams (grams only) with configurable offset and multiplier (calibration factor).
- Detect glass presence via ultrasonic sensor with configurable distance threshold (mm). Glass state is boolean.
- Provide a tare action that zeroes the current weight reading and stores the offset for the current session only (not persisted).

### 3.2 Web Dashboard (local)
- Status view shows live values: weight (g), ultrasonic distance (mm), glass detected (bool), network status.
- Controls:
  - Tare button to zero the scale.
  - Refresh/auto-refresh of sensor readings.
- Settings page:
  - Glass detection threshold distance input (mm).
  - Load cell calibration: offset and multiplier inputs; apply/save button.
  - Device identity: device name input.
  - Logging: selectable log level (e.g., ERROR/WARN/INFO/DEBUG).
  - Network: static IP, subnet mask, gateway, DNS; no DHCP option.
- Persist settings in non-volatile storage; values survive reboot and power loss.
- Validation: reject obviously invalid IP/mask/gateway/DNS entries and non-numeric calibration/threshold values; show inline error.
- UI follows Mongoose Wizard standard components/layout conventions.

### 3.4 Configuration & Persistence
- Store all settings (glass threshold, calibration offset, calibration multiplier, device name, log level, static IP config) in NVS/flash.
- Apply network settings after save with clear user feedback if a reboot is required.
- On boot, load persisted settings; fall back to safe defaults if missing/corrupt.
- Tare offset applies for the current session only and is not persisted across reboot.

## 4. Non-Functional Requirements
- Reliability: readings update at least 5 Hz internally; UI poll/WS update at 1-2 Hz acceptable.
- Accuracy: weight resolution ~1 g; glass detection reliable within configured threshold.
- Latency: REST responses < 200 ms on LAN under nominal load.
- Availability: device should recover to last good config after power cycle.
- Security: LAN-only; no internet egress; no authentication required.
- Logging: include sensor read errors, calibration changes, network changes.

## 5. Error Handling
- If a sensor read fails, return last known good value plus an error flag; surface warning in UI.
- Validation errors return 400 with message; unknown routes return 404.
- On storage failure, operate with defaults and show warning in UI/status endpoint.

## 6. Assumptions
- Single client at a time is sufficient; no concurrency constraints beyond simple locking around tare/calibration.
- Static IP only as per requirement; no DHCP fallback needed.
- Time source: device clock (no NTP assumed); timestamps may be relative if RTC/NTP unavailable.

## 7. Open Questions
- Should UI use WebSockets for live updates or periodic polling? (default to Mongoose Wizard standard if available)

## 8. Acceptance Criteria
- Web UI shows live weight, distance, and glass state; tare works and updates reading.
- Settings (glass threshold, calibration offset/multiplier, device name, log level, static IP/mask/gateway/DNS) can be edited, validated, saved, and persist across reboot.
- REST endpoints respond as specified with correct values and error codes.
- Power cycle retains settings; device boots with valid network config and serves UI/API.

## 9. Pinout
- SPI (ETH): GPIO11 MOSI, GPIO12 MISO, GPIO13 SCK, GPIO14 CS, GPIO9 RST, GPIO10 INT
- HX711: GPIO35 DT, GPIO36 SCK
- HC-SR04: GPIO37 TRIG, GPIO38 ECHO