

# Class TitanComms



[**ClassList**](annotated.md) **>** [**TitanComms**](classTitanComms.md)




















## Classes

| Type | Name |
| ---: | :--- |
| struct | [**u\_int24**](structTitanComms_1_1u__int24.md) <br> |


## Public Types

| Type | Name |
| ---: | :--- |
| enum  | [**instruction**](#enum-instruction)  <br> |




















## Public Functions

| Type | Name |
| ---: | :--- |
|   | [**TitanComms**](#function-titancomms) (int cs\_pin, SPISettings spi\_settings) <br> |
|  void | [**begin**](#function-begin) () <br> |
|  void | [**bind\_address**](#function-bind_address) ([**u\_int24**](structTitanComms_1_1u__int24.md) address) <br> |
|  u\_int32\_t | [**read**](#function-read) ([**u\_int24**](structTitanComms_1_1u__int24.md) address) <br> |
|  void | [**set\_core\_interrupt**](#function-set_core_interrupt) ([**u\_int24**](structTitanComms_1_1u__int24.md) address) <br> |
|  void | [**set\_stream\_read\_address**](#function-set_stream_read_address) (u\_int32\_t address) <br> |
|  void | [**set\_stream\_write\_address**](#function-set_stream_write_address) (u\_int32\_t address) <br> |
|  u\_int32\_t | [**stream**](#function-stream) (u\_int32\_t value) <br> |
|  void | [**write**](#function-write) ([**u\_int24**](structTitanComms_1_1u__int24.md) address, u\_int32\_t value) <br> |




























## Public Types Documentation




### enum instruction 

```C++
enum TitanComms::instruction {
    NOP = 0x00,
    WRITE = 0x01,
    READ = 0x02,
    STREAM = 0x03,
    BIND_INTERRUPT = 0x04,
    BIND_READ_ADDRESS = 0x05,
    BIND_WRITE_ADDRESS = 0x06,
    TRANSFER = 0x07,
    REPEAT = 0x08,
    GET_METADATA = 0xFF
};
```



## Public Functions Documentation




### function TitanComms 

```C++
TitanComms::TitanComms (
    int cs_pin,
    SPISettings spi_settings
) 
```






### function begin 

```C++
void TitanComms::begin () 
```






### function bind\_address 

```C++
void TitanComms::bind_address (
    u_int24 address
) 
```






### function read 

```C++
u_int32_t TitanComms::read (
    u_int24 address
) 
```






### function set\_core\_interrupt 

```C++
void TitanComms::set_core_interrupt (
    u_int24 address
) 
```






### function set\_stream\_read\_address 

```C++
void TitanComms::set_stream_read_address (
    u_int32_t address
) 
```






### function set\_stream\_write\_address 

```C++
void TitanComms::set_stream_write_address (
    u_int32_t address
) 
```






### function stream 

```C++
u_int32_t TitanComms::stream (
    u_int32_t value
) 
```






### function write 

```C++
void TitanComms::write (
    u_int24 address,
    u_int32_t value
) 
```




------------------------------
The documentation for this class was generated from the following file `titan/comms/TitanComms/TitanComms.h`

