#include "Walbi.h"

#define SERIAL_BAUD 115200  // Baudrate to PC

walbi_ns::Walbi walbi(&Serial1);

void setup()
{
    Serial1.begin(walbi_ns::DEBUG_BOARD_BAUD);
    walbi.begin(SERIAL_BAUD, 34, 36, 35, 37);
}

void loop()
{
    walbi.run();
}
