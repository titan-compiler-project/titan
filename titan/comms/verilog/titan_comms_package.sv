package TitanComms;

    // typedef enum bit [7:0] { 
    //     NOP = 0,
    //     WRITE = 1,
    //     READ = 2
    //  } instructions;

    typedef enum int {
        WRITE = 1, 
        READ = 2, 
        STREAM = 3, 
        BIND_INTERRUPT = 4,
        BIND_ADDRESS = 5,
        TRANSFER = 6, 
        REPEAT = 7
    } instructions;

endpackage