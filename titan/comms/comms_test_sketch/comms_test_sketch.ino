#include "TitanComms.h"
#include "SPI.h"

const int CS_PIN = 8;

TitanComms comms(CS_PIN, SPISettings(8000000, LSBFIRST, SPI_MODE3));

void setup() {
    Serial.begin(9600);
    comms.begin();
}

void loop() {
    TitanComms::int24 x = {0};

    // for (int i = 0; i < 5; i++) {
    //     comms.write(x, 3);
    //     x.data += 1;
    //     delay(750);
    // }

    x.data = 24;
    comms.write(x, 77);
    delay(1000);

}