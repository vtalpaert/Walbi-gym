#include "Walbi.h"

#define SERIAL_BAUD 115200  // Baudrate to PC

walbi_ns::Walbi* walbi;

void setup()
{
    Serial1.begin(walbi_ns::DEBUG_BOARD_BAUD);
    walbi = new walbi_ns::Walbi(&Serial1, SERIAL_BAUD);
}

void loop()
{
    walbi->run();
}
