#include "Walbi.h"

#define SERIAL_BAUD 115200  // Baudrate to PC
#define DEBUG_BOARD_TX 10  // Arduino soft RX (connects to debug board TX)
#define DEBUG_BOARD_RX 11  // Arduino soft TX (debub board RX)

walbi_ns::Walbi* walbi;

void setup()
{
    walbi = new walbi_ns::Walbi(DEBUG_BOARD_RX, DEBUG_BOARD_TX, SERIAL_BAUD);
}

void loop()
{
    walbi->run();
}
