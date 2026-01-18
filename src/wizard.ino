#include <SPI.h>
#include "src/mongoose_glue.h"
#include <Arduino.h>

#define SS_PIN 14            // Slave select pin
#define RST_PIN 9            // Reset pin for W5500
#define LED_PIN LED_BUILTIN  // LED pin

void spi_begin(void *spi) {
  digitalWrite(SS_PIN, LOW);
  SPI.beginTransaction(SPISettings());
  (void) spi;
}
void spi_end(void *spi) {
  digitalWrite(SS_PIN, HIGH);
  SPI.endTransaction();
  (void) spi;
}
uint8_t spi_txn(void *spi, uint8_t byte) {
  return SPI.transfer(byte);
  (void) spi;
}

void setup() {
  Serial.begin(115200);
  while (!Serial) delay(50);

  pinMode(SS_PIN, OUTPUT);
  pinMode(RST_PIN, OUTPUT);
  pinMode(LED_PIN, OUTPUT);

  // Reset W5500
  digitalWrite(RST_PIN, LOW);
  delay(50);
  digitalWrite(RST_PIN, HIGH);
  delay(150);

  SPI.begin(13, 12, 11, 14);

  // Set logging function to serial print
  mg_log_set_fn([](char ch, void *) { Serial.print(ch); }, NULL);
  mg_log_set(MG_LL_DEBUG);

  mongoose_init();
}

void loop() {
  mongoose_poll();
}
