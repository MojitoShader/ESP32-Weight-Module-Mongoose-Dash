// SPDX-FileCopyrightText: 2025
// SPDX-License-Identifier: GPL-2.0-only or commercial
// HC-SR04 Ultrasonic Sensor Driver

#include "hc_sr04.h"
#include <Arduino.h>

static uint8_t s_trig_pin = 0;
static uint8_t s_echo_pin = 0;
static bool s_initialized = false;
static int32_t s_last_distance = 0;

// Initialize HC-SR04 sensor with specified pins
void hc_sr04_init(uint8_t trig_pin, uint8_t echo_pin) {
  s_trig_pin = trig_pin;
  s_echo_pin = echo_pin;
  
  pinMode(s_trig_pin, OUTPUT);
  pinMode(s_echo_pin, INPUT);
  
  // Ensure trigger is low
  digitalWrite(s_trig_pin, LOW);
  delayMicroseconds(2);
  
  s_initialized = true;
}

// Read distance in millimeters
// Returns distance in mm
// Optimized for speed - detects objects up to ~100mm (typical cup detection range)
// If no echo received within timeout, returns the max distance for that timeout
int32_t hc_sr04_read_distance(void) {
  if (!s_initialized) {
    return -1;
  }
  
  // Send 10 microsecond pulse to trigger pin
  digitalWrite(s_trig_pin, HIGH);
  delayMicroseconds(10);
  digitalWrite(s_trig_pin, LOW);
  
  // Wait for echo pulse to go high
  // 10ms timeout = can detect up to ~585mm
  uint32_t timeout = micros() + 10000;  // 10ms timeout in microseconds
  while (digitalRead(s_echo_pin) == LOW && micros() < timeout) {
    // Wait for echo to go high
  }
  
  // If echo never went high, object is too far or no object
  // Return max distance for this timeout: 10000us * 343 / 2000 = 1715mm
  if (micros() >= timeout) {
    int32_t max_distance = (10000 * 343) / 2000;  // ~1715mm for 10ms timeout
    s_last_distance = max_distance;
    return max_distance;  // Return max distance instead of -1
  }
  
  uint32_t echo_start = micros();
  // For cup detection (0-100mm), echo duration is ~0-10ms
  timeout = echo_start + 10000; 

  while (digitalRead(s_echo_pin) == HIGH && micros() < timeout) {
    // Wait for echo to go low
  }
  
  uint32_t echo_end = micros();
  
  // Calculate distance
  // Speed of sound: 343 m/s = 0.343 mm/us
  // Distance = (duration in us * 0.343) / 2
  uint32_t echo_duration = echo_end - echo_start;
  int32_t distance = (echo_duration * 343) / 2000;  // Result in mm
  
  s_last_distance = distance;
  return distance;
  s_last_distance = distance;
  return distance;
}

// Check if sensor is initialized
bool hc_sr04_is_initialized(void) {
  return s_initialized;
}
