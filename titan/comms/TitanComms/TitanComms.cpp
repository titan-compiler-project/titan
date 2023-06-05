/*
    TitanComms.cpp - Library/wrapper intended to help with communicating with
                     Titan-created function blocks via the Titan Compiler (or 
                     any SPI-connected device that implements its protocol).
*/
#include "Arduino.h"
#include "TitanComms.h"
#include "SPI.h"

enum TitanComms::instruction {
    NOP = 0x0,
    WRITE = 0x1,
    READ  = 0x2,
    GET_METADATA = 0xFF
};

struct TitanComms::int24 {
    unsigned int data : 24;
};

TitanComms::TitanComms(int pin, SPISettings spi_settings){
    _cs_pin = pin;
    _spi_settings = spi_settings;
}

void TitanComms::begin(){
    pinMode(_cs_pin, OUTPUT);
    digitalWrite(_cs_pin, HIGH); // cs is active low, so setting to high means its disabled
    SPI.begin();
}

void TitanComms::write(int24 address, long value){

    // have 8b instruction + 24bit address + 32bit value
    // how to split into nice 8 or 16 bit calls?

    

}