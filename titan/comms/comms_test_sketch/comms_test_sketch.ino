// example sketch for how to interface a teensy with titan cores using the TitanComms library
#define DEBUG

#include "TitanComms.h"
#include "TitanCommsDebug.h"
#include "SPI.h"


// pins - teensy - first spi bus
// const int CS_PIN = 15; // dedicated CS pin 10 does not work, causes weird glitches on MISO
// const int DOUT = 11;
// const int DIN = 12;
// const int SCLK_PIN = 13;

// pins - teensy - alternative SPI pins
// https://www.pjrc.com/teensy/card7a_rev3_web.pdf
const int CS_PIN = 21;
const int DOUT = 7;
const int DIN = 8;
const int SCLK_PIN = 14;

// pins - mega
// const int CS_PIN = 53;
// const int DOUT = 51;
// const int DIN = 50;
// const int SCLK_PIN = 52;

const int SCLK = 8000000;

TitanComms comms(CS_PIN, SPISettings(SCLK, MSBFIRST, SPI_MODE0));

unsigned int wrong_counter = 0;
unsigned int total_requests = 0;

SPISettings spis(SCLK, MSBFIRST, SPI_MODE0);

void setup()
{
    Serial.begin(115200);
    
    // library handles setting up CS pin as output
    // and initialising the SPI library
    comms.begin();

    // setting alternative SPI pins
    SPI.setSCK(SCLK_PIN);
    SPI.setMISO(DIN);
    SPI.setMOSI(DOUT);
}

bool stop = false;

TitanComms::u_int24 address_a = {0};
TitanComms::u_int24 address_b = {1};
TitanComms::u_int24 address_c = {2};
u_int32_t rx = 0;

void loop()
{
    if (!stop){

        for (u_int32_t i = 0; i < 0xFFF; i++){
            comms.write(address_a, i);

            for (u_int32_t j = 0; j < 0xFFF; j++){
                comms.write(address_b, j);

                // no need to delay since the core is a simple adder, and should
                // already be done with the calculation
                rx = comms.read(address_c);

                total_requests++;

                if ((rx != i + j) ^ (total_requests % 1000 == 0)) {
                    
                    if (rx != i + j) 
                        wrong_counter++;

                    DEBUG_PRINTLN(); DEBUG_PRINT_HEX(i); DEBUG_PRINT_STR(" + "); DEBUG_PRINT_HEX(j);
                        DEBUG_PRINT_STR(" = "); DEBUG_PRINT_HEX(rx);
                        DEBUG_PRINT_STR(" (missed ");  DEBUG_PRINT_INT(wrong_counter);
                        DEBUG_PRINT_STR(" out of ");  DEBUG_PRINT_INT(total_requests); DEBUG_PRINT_STR(")");
                }
                delay(1);
            }
        }

        stop = true;

        DEBUG_PRINTLN(); DEBUG_PRINT_STR("[stop] missed ");  DEBUG_PRINT_INT(wrong_counter);
                    DEBUG_PRINT_STR(" out of ");  DEBUG_PRINT_INT(total_requests); DEBUG_PRINTLN();

    } else if (stop) {
        DEBUG_PRINT_STR("-");
        delay(1000);
    }
}