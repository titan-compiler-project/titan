package TitanComms;

    typedef enum int {
        WRITE = 1, 
        READ = 2, 
        STREAM = 3, 
        BIND_INTERRUPT = 4,
        BIND_READ_ADDRESS = 5,
        BIND_WRITE_ADDRESS = 6,
        TRANSFER = 7, 
        REPEAT = 8
    } instructions;

endpackage