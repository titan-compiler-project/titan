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
        TitanComms(int pin, SPISettings spi_settings); // pass cs & spi settings?
        enum instruction : byte; // need data type otherwise it complains about forward declaration
        struct int24;
        void begin(); // handles hardware config
        void write(int24 address, long value);
        unsigned long read();
    private:
        int _cs_pin;
        SPISettings _spi_settings;
        byte nop_and_read8();
        int nop_and_read16();
};

#endif