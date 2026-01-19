// SPDX-FileCopyrightText: 2025
// SPDX-License-Identifier: GPL-2.0-only or commercial
// HX711 Weight Cell Amplifier Driver

#include "hx711.h"
#include <Arduino.h>

static uint8_t s_dout_pin = 0;
static uint8_t s_sck_pin = 0;
static bool s_initialized = false;
static int32_t s_tare_offset = 0;  // Current session tare offset (not persisted)

// Initialize HX711 with specified pins
void hx711_init(uint8_t dout_pin, uint8_t sck_pin) {
  s_dout_pin = dout_pin;
  s_sck_pin = sck_pin;
  
  pinMode(s_dout_pin, INPUT);
  pinMode(s_sck_pin, OUTPUT);
  
  // Ensure clock is low
  digitalWrite(s_sck_pin, LOW);
  delayMicroseconds(1);
  
  // Initial read to stabilize
  hx711_read_raw();
  delay(10);
  
  s_tare_offset = 0;
  s_initialized = true;
}

// Read raw value from HX711 (24-bit ADC)
// Protocol: Read 24 bits of data + 1 pulse for channel/gain selection (25 total pulses)
// Channel A, Gain 128 (default, most common)
int32_t hx711_read_raw(void) {
  if (!s_initialized) {
    return 0;
  }
  
  // Wait for data ready (DOUT low) with timeout
  uint32_t timeout = millis() + 100;  // 100ms timeout
  while (digitalRead(s_dout_pin) == HIGH && millis() < timeout) {
    delayMicroseconds(1);
  }
  
  if (millis() >= timeout) {
    return 0;  // Timeout - no data ready
  }
  
  int32_t data = 0;
  
  // Read 24 bits (MSB first)
  // Each bit is clocked by toggling SCK (LOW->HIGH->LOW)
  for (int i = 23; i >= 0; i--) {
    // Clock pulse: rise
    digitalWrite(s_sck_pin, HIGH);
    delayMicroseconds(1);  // Wait for data to stabilize
    
    // Read bit (DOUT is stable on HIGH clock)
    int bit = digitalRead(s_dout_pin);
    data |= ((int32_t) bit) << i;
    
    // Clock pulse: fall
    digitalWrite(s_sck_pin, LOW);
    delayMicroseconds(1);
  }
  
  // 25th clock pulse: selects Channel A with Gain 128 for next read
  // (This is the default, must occur or data will be corrupted on next read)
  digitalWrite(s_sck_pin, HIGH);
  delayMicroseconds(1);
  digitalWrite(s_sck_pin, LOW);
  delayMicroseconds(1);
  
  // Convert 24-bit two's complement to 32-bit signed integer
  // If MSB (bit 23) is 1, the number is negative
  // We need to sign-extend from 24 bits to 32 bits
  if (data & 0x800000) {
    // MSB is 1, this is a negative number
    // Sign-extend by setting all upper bits to 1
    data |= 0xFF000000;
  }
  
  return data;
}

// Read weight in grams with calibration
int32_t hx711_read_weight(int32_t offset, int32_t multiplier) {
  if (!s_initialized) {
    return 0;
  }
  
  if (multiplier == 0) {
    return 0;  // Prevent division by zero
  }
  
  // Read raw ADC value
  int32_t raw = hx711_read_raw();
  
  // Apply session tare and permanent offset
  // Formula: weight = (raw - tare_offset - offset) * multiplier / 1000
  int32_t calibrated = raw - s_tare_offset - offset;
  
  // Apply multiplier (calibration factor)
  // Multiplier is typically determined during calibration
  // We scale by 1000 to allow fractional multipliers
  int32_t weight = (calibrated * multiplier) / 1000;
  
  // Clamp to reasonable range (0-1000g for 1kg load cell)
  if (weight < 0) weight = 0;
  if (weight > 1000) weight = 1000;
  
  return weight;
}

// Set tare (zero offset) for current session
void hx711_tare(void) {
  if (s_initialized) {
    // Average multiple readings for more stable tare
    int32_t sum = 0;
    const int samples = 5;
    
    for (int i = 0; i < samples; i++) {
      sum += hx711_read_raw();
      delay(10);
    }
    
    s_tare_offset = sum / samples;
  }
}

// Get current tare offset (session-only)
int32_t hx711_get_tare_offset(void) {
  return s_tare_offset;
}

// Get raw ADC reading for debugging
int32_t hx711_get_raw_debug(void) {
  if (s_initialized) {
    return hx711_read_raw();
  }
  return 0;
}

// Check if sensor is initialized
bool hx711_is_initialized(void) {
  return s_initialized;
}
