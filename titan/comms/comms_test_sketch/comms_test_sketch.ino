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
int total_requests = 0;

TitanComms::u_int24 x = {0};
TitanComms::u_int24 address = {0};

void setup() {
    Serial.begin(192000);
    comms.begin();
}

void loop() {

    // u_int32_t rx;
    // x.data = 0xAABBCC;
    // comms.write(x, 0xDEADBEEF);
    // rx = comms.read(x);

    // if (rx != 0x23232323)
    //     wrong_counter++;

    // total_requests++;

    // DEBUG_PRINT_STR("wrong hit: "); DEBUG_PRINT_INT(wrong_counter); 
    //     DEBUG_PRINT_STR(" out of "); DEBUG_PRINT_INT(total_requests); DEBUG_PRINTLN();

    u_int32_t rx;
    address.data = 0;

    comms.write(address, 1);

    address.data = 1;
    comms.write(address, 2);

    address.data = 2;
    rx = comms.read(address);

    comms.repeat(); // should see data pointer reset to 0

    if (rx != 3)
        wrong_counter++;

    total_requests++;

    DEBUG_PRINT_STR("got: ") + DEBUG_PRINT_HEX(rx) + DEBUG_PRINT_STR(" expected 3 (missed ");
        DEBUG_PRINT_INT(wrong_counter); DEBUG_PRINT_STR(" out of "); DEBUG_PRINT_INT(total_requests);
        DEBUG_PRINTLN_STR(")");

    delay(100);
}