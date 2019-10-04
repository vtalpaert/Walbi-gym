#include "Walbi.h"

#define SERIAL_BAUD 115200  // Baudrate to PC

walbi_ns::Walbi walbi(&Serial1, SERIAL_BAUD);

void setup()
{
    Serial1.begin(walbi_ns::DEBUG_BOARD_BAUD);
}

void loop()
{
    walbi.run();
}
