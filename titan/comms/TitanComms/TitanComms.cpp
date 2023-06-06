/*
    TitanComms.cpp - Library/wrapper intended to help with communicating with
                     Titan-created function blocks via the Titan Compiler (or 
                     any SPI-connected device that implements its protocol).
*/
#define DEBUG

#include "Arduino.h"
#include "TitanComms.h"
#include "TitanCommsDebug.h"
#include "SPI.h"

// constructor
TitanComms::TitanComms(int cs_pin, SPISettings spi_settings){
    _cs_pin = cs_pin;
    _spi_settings = spi_settings;
}

void TitanComms::begin(){
    pinMode(_cs_pin, OUTPUT);
    digitalWrite(_cs_pin, HIGH); // cs is active low, so setting to high means its disabled
    SPI.begin();
}

void TitanComms::_extract_byte_from_int(int24 data, int byte_index, byte* storage_byte){
    // byte_index should be either 0, 1 or 2
    // byte_index:     2           1           0
    // 24b number: xxxx xxxx | xxxx xxxx | xxxx xxxx
    // byte mask:  1000 0000   0000 0000   0000 0000 -- 0x800000
    //             0000 0000   1000 0000   0000 0000 -- 0x008000
    //             0000 0000   0000 0000   1000 0000 -- 0x000080
    
    long byte_mask = 0x800000 >> (8 * byte_index);
    byte new_byte;

    DEBUG_PRINT_STR("address/value: "); DEBUG_PRINT_INT(data.data); DEBUG_PRINT_STR(" "); DEBUG_PRINT_BIN(data.data); DEBUG_PRINTLN();
    DEBUG_PRINT_STR("byte shift: "); DEBUG_PRINT_INT(byte_index); DEBUG_PRINT_STR(" "); DEBUG_PRINT_BIN(byte_index); DEBUG_PRINTLN();
    DEBUG_PRINT_STR("byte mask hex: "); DEBUG_PRINT_HEX(byte_mask); DEBUG_PRINT_STR(" "); DEBUG_PRINT_BIN(byte_mask); DEBUG_PRINTLN();

    // for each pos (23-16, 15-8, 7-0):
    //    if data & bytemask
    //      bitset(pos, newbyte)

    int upper_limit = 7 + (8 * byte_index);
    int lower_limit = 0 + (8 * byte_index);


    int normal_pos = 0; // i is relative to the incoming value, it needs to be translated to the new byte
    for (int i = lower_limit; i < upper_limit + 1; i++){
        if (bitRead(data.data, i)) {
            bitSet(new_byte, normal_pos);
            DEBUG_PRINT_STR("pos: "); DEBUG_PRINT_INT(i); DEBUG_PRINTLN_STR(" set");
        } else {
            bitClear(new_byte, normal_pos);
            DEBUG_PRINT_STR("pos: "); DEBUG_PRINT_INT(i); DEBUG_PRINTLN_STR(" not set");
        }
        normal_pos++;
    }

    *storage_byte = new_byte;

    DEBUG_PRINT_STR("returning: "); DEBUG_PRINT_BIN(new_byte); DEBUG_PRINTLN();
    DEBUG_PRINTLN_STR("-------");
}

void TitanComms::write(int24 address, long value){

    // have 8b instruction + 24bit address + 32bit value
    // how to split into nice 8 or 16 bit calls?

    // 8 8 16 16 16

    byte addr_high, addr_mid, addr_low = 0;

    // DEBUG_PRINT_VALUE(address.data);

    // for (int i = 0; i < 3; i++){
    //     _extract_byte_from_int(address, i, &addr_high);
    // }

    _extract_byte_from_int(address, 0, &addr_low);
    _extract_byte_from_int(address, 1, &addr_mid);
    _extract_byte_from_int(address, 2, &addr_high);
    DEBUG_PRINT_STR("---L "); DEBUG_PRINT_BIN(addr_low); DEBUG_PRINTLN();
    DEBUG_PRINT_STR("---M "); DEBUG_PRINT_BIN(addr_mid); DEBUG_PRINTLN();
    DEBUG_PRINT_STR("---H "); DEBUG_PRINT_BIN(addr_high); DEBUG_PRINTLN();
}