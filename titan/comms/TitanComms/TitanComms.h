/*
    TitanComms.h - Library/wrapper intended to help with communicating with
                   Titan-created function blocks via the Titan Compiler (or 
                   any SPI-connected device that implements its protocol).
*/
#ifndef TitanComms_h
#define TitanComms_h

#include "Arduino.h"
#include "SPI.h"

class TitanComms {
    public:
        TitanComms(int cs_pin, SPISettings spi_settings); // pass cs & spi settings?
        // enum instruction : byte; // need data type otherwise it complains about forward declaration
        
        enum instruction {
            NOP = 0x00,
            WRITE = 0x01,
            READ = 0x02,
            STREAM = 0x03,
            TRANSFER = 0x04,
            REPEAT = 0x05,
            GET_METADATA = 0xFF
        };
        
        struct u_int24 {
            u_int32_t data : 24;
        };
        void begin(); // handles hardware config
        void write(u_int24 address, u_int32_t value);
        u_int32_t read(u_int24 address);
    private:
        int _cs_pin;
        SPISettings _spi_settings;
        u_int8_t _nop_and_read8();
        u_int16_t _nop_and_read16();
        void _repeat();
        void _extract_byte_from_int(u_int24 data, int byte_index, u_int8_t* storage_byte);
        void _chip_select();
        void _chip_deselect();
        u_int8_t _xor_checksum(u_int32_t input);
};

#endif