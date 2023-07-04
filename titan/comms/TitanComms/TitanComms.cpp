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

void TitanComms::_chip_select(){
    digitalWrite(_cs_pin, LOW);
}

void TitanComms::_chip_deselect(){
    digitalWrite(_cs_pin, HIGH);
}

void TitanComms::begin(){
    pinMode(_cs_pin, OUTPUT);
    digitalWrite(_cs_pin, HIGH); // cs is active low, so setting to high means its disabled
    SPI.begin();
}

void TitanComms::_extract_byte_from_int(u_int24 data, int byte_index, u_int8_t* storage_byte){
    // byte_index should be either 0, 1 or 2
    // byte_index:     2           1           0
    // 24b number: xxxx xxxx | xxxx xxxx | xxxx xxxx
    // byte mask:  1000 0000   0000 0000   0000 0000 -- 0x800000
    //             0000 0000   1000 0000   0000 0000 -- 0x008000
    //             0000 0000   0000 0000   1000 0000 -- 0x000080
    
    u_int32_t byte_mask = 0x800000 >> (8 * byte_index);
    u_int8_t new_byte;

    int upper_limit = 7 + (8 * byte_index);
    int lower_limit = 0 + (8 * byte_index);

    int normal_pos = 0; // i is relative to the incoming value, it needs to be translated to the new byte
    for (int i = lower_limit; i < upper_limit + 1; i++){
        if (bitRead(data.data, i)) {
            bitSet(new_byte, normal_pos);
        } else {
            bitClear(new_byte, normal_pos);
        }

        normal_pos++;
    }

    *storage_byte = new_byte;
}

void TitanComms::write(u_int24 address, u_int32_t value){
    byte addr_high, addr_mid, addr_low = 0;

    _extract_byte_from_int(address, 0, &addr_low);
    _extract_byte_from_int(address, 1, &addr_mid);
    _extract_byte_from_int(address, 2, &addr_high);

    u_int16_t merged_instr_addr_high = (WRITE << 8) + addr_high; // instruction + address high byte (16b)
    u_int16_t addr_mid_and_low = (addr_mid << 8) + addr_low; // address mid byte + address low byte (16b)
    u_int16_t upper_data = (value >> 16);
    u_int16_t lower_data = value; // auto truncated?


    SPI.beginTransaction(_spi_settings);
    _chip_select();
    SPI.transfer16(merged_instr_addr_high);
    SPI.transfer16(addr_mid_and_low);
    SPI.transfer16(upper_data);
    SPI.transfer16(lower_data);
    _chip_deselect();
    SPI.endTransaction();

    // DEBUG_PRINT_STR("---L "); DEBUG_PRINT_HEX(addr_low); DEBUG_PRINTLN();
    // DEBUG_PRINT_STR("---M "); DEBUG_PRINT_HEX(addr_mid); DEBUG_PRINTLN();
    // DEBUG_PRINT_STR("---H "); DEBUG_PRINT_HEX(addr_high);  DEBUG_PRINTLN();
}

byte TitanComms::_nop_and_read8(){
    byte temp = SPI.transfer(TRANSFER);
    return temp;
}

u_int16_t TitanComms::_nop_and_read16(){
    // TODO: how to format 0x0404 as TRANSFER, TRANSFER instead of using magic value
    u_int16_t temp = SPI.transfer16(0x0404);
    return temp;
}

void TitanComms::_repeat() {
    SPI.beginTransaction(_spi_settings);
    _chip_select();
    SPI.transfer(REPEAT);
    _chip_deselect();
    SPI.endTransaction();
}


u_int32_t TitanComms::read(u_int24 address){
    // send: instruction + address --> 8 bits + 24 bits
    // recieve: value + checksum --> 32 bits + 8 bits

    u_int8_t addr_high;
    _extract_byte_from_int(address, 2, &addr_high); // should get the highest byte from address

    u_int16_t merged_instr_addr_high = (READ << 8) + addr_high;
    u_int16_t addr_mid_and_low = address.data;

    u_int16_t value_high, value_low;
    u_int8_t recieved_checksum, calculated_checksum;

    
    SPI.beginTransaction(_spi_settings);
    
    _chip_select();
    SPI.transfer16(merged_instr_addr_high);
    SPI.transfer16(addr_mid_and_low);
    
    value_high = _nop_and_read16();
    value_low = _nop_and_read16();

    // TODO: checksum, and repeating if necessary
    // recieved_checksum = _nop_and_read8();
    
    _chip_deselect();
    SPI.endTransaction();

    u_int32_t final_val = (value_high << 16) + value_low;

    return final_val;
}