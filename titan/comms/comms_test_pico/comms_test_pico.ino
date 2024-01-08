#define DEBUG

#include "Arduino.h"
#include "SPI.h"
#include "TitanComms.h"
#include "TitanCommsDebug.h"
#include "Serial.h"

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

#define LED 25

SPISettings spi_settings_0(6'900'000, MSBFIRST, SPI_MODE0);

TitanComms comms_0(SPI0_MISO_RX, SPI0_MOSI_TX, SPI0_CS, SPI0_SCLK, spi_settings_0);
TitanComms comms_1(SPI1_MISO_RX, SPI1_MOSI_TX, SPI0_CS, SPI1_SCLK, spi_settings_0);

arduino::MbedSPI SPI0(SPI0_MISO_RX, SPI0_MOSI_TX, SPI0_SCLK);

TitanComms::u_int24 address_a = {0};
TitanComms::u_int24 address_b = {1};
TitanComms::u_int24 address_c = {2};
bool stop = false;
u_int32_t total_requests = 0;
u_int32_t wrong_counter = 0;
u_int32_t rx = 0;

void setup(){
    pinMode(SPI0_CS, OUTPUT);
    digitalWrite(SPI0_CS, HIGH);

    pinMode(LED, OUTPUT);
    digitalWrite(LED, LOW);
    SPI0.begin();
    comms_0.begin();
    // comms_1.begin();
    Serial.begin(115200);
}

u_int32_t temp;
// bool stop = false;

void loop() {

    digitalWrite(LED, LOW);

 /*   // reset?
    // comms_0.write(address_a, 0);
    // comms_0.write(address_b, 0);


    // if (!stop){
    //     for (u_int32_t i = 0; i < 0xFFF; i++){
    //         comms_0.write(address_a, i);

    //         for (u_int32_t j = 0; j < 0xFFF; j++){
    //             comms_0.write(address_b, j);
    //             rx = comms_0.read(address_c);

    //             total_requests++;

    //             if ((rx != i + j) ^ (total_requests % 1000 == 0)) {
                        
    //                     if (rx != i + j) 
    //                         wrong_counter++;

    //                     DEBUG_PRINTLN(); DEBUG_PRINT_HEX(i); DEBUG_PRINT_STR(" + "); DEBUG_PRINT_HEX(j);
    //                         DEBUG_PRINT_STR(" = "); DEBUG_PRINT_HEX(rx);
    //                         DEBUG_PRINT_STR(" (missed ");  DEBUG_PRINT_INT(wrong_counter);
    //                         DEBUG_PRINT_STR(" out of ");  DEBUG_PRINT_INT(total_requests); DEBUG_PRINT_STR(")");

    //                     if (rx != i + j){
    //                         delay(1000);
    //                     } else {
    //                         delay(1);
    //                     }
    //                 }
    //         }
    //     }

    //     stop = true;
    //     DEBUG_PRINT_STR("[stop] missed ");  DEBUG_PRINT_INT(wrong_counter);
    //     DEBUG_PRINT_STR(" out of ");  DEBUG_PRINT_INT(total_requests); DEBUG_PRINTLN();

    // } else {
    //     DEBUG_PRINT_STR(".");
    //     delay(1000);
    // }*/

    // input 0 + input 1 = output 0
    // 0x0 - input 0
    // 0x1 - input 1
    // 0x2 - output 0
    comms_0.write(address_a, 0xBEEF0000);
    comms_0.set_stream_write_address(0x1);

    for (int i = 0; i < 10; i++){
        temp = comms_0.stream(i);
        DEBUG_PRINT_STR("returned: ");
        DEBUG_PRINT_HEX(temp);
        DEBUG_PRINTLN();

        // -1 because we're always getting the last answer
        u_int32_t ans = (0xBEEF0000 + i)-1;
        if (temp != ans){
            DEBUG_PRINTLN_STR("...failed!");
            DEBUG_PRINT_STR("  temp:");
            DEBUG_PRINT_HEX(temp); DEBUG_PRINT_STR(" .. answer: ");
            DEBUG_PRINT_HEX(ans); DEBUG_PRINTLN();
        }

        delay(500);
    }

    digitalWrite(LED, HIGH);
    delay(500);
}