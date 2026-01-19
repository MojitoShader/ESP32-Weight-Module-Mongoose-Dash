// SPDX-FileCopyrightText: 2025
// SPDX-License-Identifier: GPL-2.0-only or commercial
// HX711 Weight Cell Amplifier Driver

#ifndef HX711_H
#define HX711_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdbool.h>

// Initialize HX711 with specified pins
// dout_pin: Data output pin
// sck_pin: Serial clock pin
void hx711_init(uint8_t dout_pin, uint8_t sck_pin);

// Read raw value from HX711
// Returns raw ADC value (24-bit)
int32_t hx711_read_raw(void);

// Read weight in grams with calibration
// Returns weight in grams, with offset and multiplier applied
// offset: calibration offset (typically 0 or tare value)
// multiplier: calibration factor (linear in FSD)
int32_t hx711_read_weight(int32_t offset, int32_t multiplier);

// Set tare (zero offset)
// Stores the current reading as the new offset
void hx711_tare(void);

// Get current tare offset
int32_t hx711_get_tare_offset(void);

// Get raw ADC reading for debugging (non-calibrated)
int32_t hx711_get_raw_debug(void);

// Check if sensor is initialized
bool hx711_is_initialized(void);

#ifdef __cplusplus
}
#endif

#endif  // HX711_H
