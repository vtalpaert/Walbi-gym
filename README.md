# Walbi Gym

**Walbi Gym** is a project to interact with [Walbi](https://releasetheinnergeek.com/) as an [OpenAI gym](https://gym.openai.com/) environment.

## How to use

### Install the Python3 module

```bash
python3 setup.py
```

### Gym environment

You may create a Walbi Gym environment as usual.

```python
import gym
import walbi_gym  # will register env
env = gym.make('Walbi-v0')
```

The action space is a Box shaped `(10, 2)`: a target position and a given time span for each of the ten motors.

The observation space is a Box shaped `(11,)` for one time interval between the two last observation (`-1` if invalid) and ten current motor positions.

### Arduino compilation

1. With Makefile (Linux/Mac OS systems)

    ***This method is currently not working. For an unknown reason, the ServoBus library does not seem to read the motor positions even after successful compilation.***

    Install [Arduino Makefile](https://github.com/sudar/Arduino-Makefile):

    ```bash
    sudo apt-get install arduino-mk
    ```

    Compile and upload the code to the Arduino (please check the board name in the Makefile):

    ```bash
    cd arduino-board/
    make  # compile
    make upload  # compile and upload
    ```

1. With the Arduino IDE (all platforms)

    Copy the folders from [lib](arduino-board/lib) into your local Arduino library folder.

    Change the includes from:

    ```c
    #include "../ServoBus/ServoBus.h"
    ```

    to:

    ```c
    #include "ServoBus.h"
    ```

    Open the file [slave.ino](arduino-board/slave/slave.ino) and hit verify/upload.

## Hardware

### Buiding Walbi

Build Walbi according to [original instructions](https://create.arduino.cc/projecthub/the-inner-geek/walbi-the-walking-biped-8feacd).

### Wiring

1. Serial
    1. Connect your Arduino Serial to your computer
    1. Connect Arduino to the Debug Board by the two `DEBUG_BOARD_RX`, `DEBUG_BOARD_TX` pins
1. Bluetooth (TODO)
1. Wifi (TODO)

## Versions

1. Version 0 is simple motor observation and action
1. Version 1 adds time interval

## Acknowledgements

This project relies on the [serial communication code](https://github.com/araffin/arduino-robust-serial)
by Antonin Raffin, as he wrote the [robust serial library](https://medium.com/@araffin/simple-and-robust-computer-arduino-serial-communication-f91b95596788).

Walbi was [designed](https://create.arduino.cc/projecthub/the-inner-geek/walbi-the-walking-biped-8feacd)
by [Release the Inner Geek](https://releasetheinnergeek.com/).
