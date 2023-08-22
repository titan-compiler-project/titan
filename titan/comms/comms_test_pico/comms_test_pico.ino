#define DEBUG

#include "Arduino.h"
#include "SPI.h"
#include "TitanComms.h"
// #include "TitanCommsDebug.h"

// https://www.raspberrypi-spy.co.uk/wp-content/uploads/2021/01/raspberry_pi_pico_pinout.png
// PICO SPI0 pins
#define SPI0_MISO_RX 4
#define SPI0_MOSI_TX 3
#define SPI0_SCLK 2
#define SPI0_CS 5

#define SPI1_MISO_RX 12
#define SPI1_MOSI_TX 11
#define SPI1_SCLK 10
#define SPI1_CS 13

SPISettings spi_settings_0(1'000'000, MSBFIRST, SPI_MODE0);

TitanComms comms_0(SPI0_MISO_RX, SPI0_MOSI_TX, SPI0_CS, SPI0_SCLK, spi_settings_0);
TitanComms comms_1(SPI1_MISO_RX, SPI1_MOSI_TX, SPI0_CS, SPI1_SCLK, spi_settings_0);

TitanComms::u_int24 addr_a = {2};
TitanComms::u_int24 addr_b = {1024};


void setup(){
    pinMode(25, OUTPUT);
    digitalWrite(25, HIGH);
    comms_0.begin();
    comms_1.begin();
}


void loop() {

    digitalWrite(25, HIGH);
    for (int i = 0; i < 1024; i++){
        comms_0.write(addr_a, i);
        delayMicroseconds(10);
    }

    delay(200);

    for (int i = 0; i < 1024; i++){
        comms_1.write(addr_b, i);
        delayMicroseconds(10);
    }

    digitalWrite(25, LOW);
    delay(10);
}