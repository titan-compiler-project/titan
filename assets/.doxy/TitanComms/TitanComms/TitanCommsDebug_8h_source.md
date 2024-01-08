

# File TitanCommsDebug.h

[**File List**](files.md) **>** [**comms**](dir_15e9a61cbc095141a3f886f43eb6818f.md) **>** [**TitanComms**](dir_5bea15bd51704c26ebfcf0ce33d5c553.md) **>** [**TitanCommsDebug.h**](TitanCommsDebug_8h.md)

[Go to the documentation of this file](TitanCommsDebug_8h.md)

```C++

#ifdef DEBUG
    #define DEBUG_PRINT_VALUE(x) \
        Serial.print(x); \
        Serial.print(" as hex: "); \
        Serial.print(x, HEX); \
        Serial.print(" , as bin: "); \
        Serial.print(x, BIN); \
        Serial.println();
    
    #define DEBUG_PRINT_STR(x) Serial.print(x);
    #define DEBUG_PRINTLN() Serial.println();
    #define DEBUG_PRINTLN_STR(x) Serial.println(x);
    #define DEBUG_PRINT_HEX(x) Serial.print(x, HEX);
    #define DEBUG_PRINT_INT(x) Serial.print(x);
    #define DEBUG_PRINT_BIN(x) Serial.print(x, BIN);
    #define DEBUG_PRINT_SIZEOF(x) Serial.print(sizeof(x));

#else
    #define DEBUG_PRINT(x)
    #define DEBUG_PRINT_STR(x)
    #define DEBUG_PRINTLN()
    #define DEBUG_PRINTLN_STR(x)
    #define DEBUG_PRINT_HEX(x)
    #define DEBUG_PRINT_INT(x)
    #define DEBUG_PRINT_BIN(x)
    #define DEBUG_PRINT_SIZEOF(x)
#endif

```

