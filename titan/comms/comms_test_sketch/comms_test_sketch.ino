#define DEBUG

#include "TitanComms.h"
#include "TitanCommsDebug.h"
#include "SPI.h"

// mega
// const int CS_PIN = 48;

// teensy
const int CS_PIN = 0;
// const int CLOCK = 72000000;
// 562600
const int SCLK = 4000000;

TitanComms comms(CS_PIN, SPISettings(SCLK, MSBFIRST, SPI_MODE3));
int wrong_counter = 0;

void setup() {
    Serial.begin(192000);
    comms.begin();
}

void loop() {
    TitanComms::u_int24 x = {0};

    // for (int i = 0; i < 5; i++) {
    //     comms.write(x, 3);
    //     x.data += 1;
    //     delay(750);
    // }

    unsigned int rx;
    x.data = 0xAABBCC;
    comms.write(x, 0xDEADBEEF);
    // delayMicroseconds(10);
    rx = comms.read(x);

    DEBUG_PRINT_STR("got: "); DEBUG_PRINT_HEX(rx); DEBUG_PRINTLN();

    if (rx != 0x23232323)
        wrong_counter++;

    DEBUG_PRINT_STR("wrong hit: "); DEBUG_PRINT_INT(wrong_counter); DEBUG_PRINTLN();

    delay(1500);

}