// SPDX-FileCopyrightText: 2025
// SPDX-License-Identifier: GPL-2.0-only or commercial
// HC-SR04 Ultrasonic Sensor Driver

#ifndef HC_SR04_H
#define HC_SR04_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stdint.h>
#include <stdbool.h>

// Initialize HC-SR04 sensor with specified pins
void hc_sr04_init(uint8_t trig_pin, uint8_t echo_pin);

// Read distance in millimeters
// Returns distance in mm, or -1 on error
int32_t hc_sr04_read_distance(void);

// Check if sensor is initialized
bool hc_sr04_is_initialized(void);

#ifdef __cplusplus
}
#endif

#endif  // HC_SR04_H
