/*
    TitanComms.h - Library/wrapper intended to help with communicating with
                   Titan-created function blocks via the Titan Compiler (or 
                   any SPI-connected device that implements its protocol).
*/
#ifndef TitanComms_h
#define TitanComms_h

#include "Arduino.h"
#include "SPI.h"

// gotta remember:
// char - 1 byte/8 bits
// int - 2 bytes/16 bits
// long - 4 bytes/32 bits

class TitanComms {
    public:
        TitanComms(int cs_pin, SPISettings spi_settings); // pass cs & spi settings?
        // enum instruction : byte; // need data type otherwise it complains about forward declaration
        
        enum instruction {
            NOP = 0x00,
            WRITE = 0x01,
            READ = 0x02,
            GET_METADATA = 0xFF
        };
        
        struct int24 {
            unsigned long data : 24;
        };
        void begin(); // handles hardware config
        void write(int24 address, long value);
        unsigned long read();
    private:
        int _cs_pin;
        SPISettings _spi_settings;
        byte _nop_and_read8();
        int _nop_and_read16();
        void _extract_byte_from_int(int24 data, int byte_index, byte* storage_byte);
        void _chip_select();
        void _chip_deselect();
};

#endif