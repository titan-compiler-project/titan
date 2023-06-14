package TitanComms;

    // typedef enum bit [7:0] { 
    //     NOP = 0,
    //     WRITE = 1,
    //     READ = 2
    //  } instructions;

    typedef enum int {
        WRITE = 1, READ = 2, STREAM = 3, TRANSFER = 4, REPEAT = 5
    } instructions;

endpackage