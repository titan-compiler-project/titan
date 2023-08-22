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
        #if !defined(ARDUINO_ARCH_RP2040)
            TitanComms(int cs_pin, SPISettings spi_settings); // pass cs & spi settings?
        #elif defined(ARDUINO_ARCH_RP2040)
            TitanComms(int MISO, int MOSI, int CS, int SCLK, SPISettings spi_settings);
        #else
            #error "unsupported target"
        #endif
       
        enum instruction {
            NOP = 0x00,
            WRITE = 0x01,
            READ = 0x02,
            STREAM = 0x03,
            BIND_INTERRUPT = 0x04,
            BIND_ADDRESS = 0x05,
            TRANSFER = 0x06,
            REPEAT = 0x07,
            GET_METADATA = 0xFF
        };
        
        struct u_int24 {
            u_int32_t data : 24;
        };
        void begin(); // handles hardware config
        void write(u_int24 address, u_int32_t value);
        u_int32_t read(u_int24 address);
        void set_core_interrupt(u_int24 address);
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

        // create different class depending on target architecture
        //              v extract from verbose compilation
        // target rpi: ARDUINO_ARCH_RP2040
        // target teensy3.2: ARDUINO_TEENSY32
        #if defined(ARDUINO_TEENSY32)
            SPIClass *_spi;
        #elif defined(ARDUINO_ARCH_RP2040)
            arduino::MbedSPI *_spi;
            int _miso, _mosi, _sclk;
        #else
            #error "unsupported target"
        #endif
};

#endif