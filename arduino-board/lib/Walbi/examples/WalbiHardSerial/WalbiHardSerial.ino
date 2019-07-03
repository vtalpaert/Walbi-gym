#include "Walbi.h"

#define SERIAL_BAUD 115200  // Baudrate to PC
#define DEBUG_BOARD_TX 10  // Arduino soft RX (connects to debug board TX)
#define DEBUG_BOARD_RX 11  // Arduino soft TX (debub board RX)

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
