# Walbi Gym

**Walbi Gym** is a project to interact with [Walbi](https://releasetheinnergeek.com/) as an [OpenAI gym](https://gym.openai.com/) environment.

## Installation

### Installing with Arduino libraries

Installing the package will automatically put the Arduino libraries in the folder specifed by your environment variable `ARDUINO_LIBRARIES_PATH`.

To set an environment variable, use:

- In Linux : `export ARDUINO_LIBRARIES_PATH=$HOME/Arduino/libraries`
- In Windows, follow [this guide](https://www.computerhope.com/issues/ch000549.htm)

Note that to installing files outside the package folder [is not permited by wheels](https://github.com/pypa/wheel/issues/92).

The following command allow for libraries copy

```bash
pip3 install --no-binary walbi-gym .  # avoids building a wheel
```

### Developpers

Clone repository with:

```bash
git clone --recursive https://github.com/vtalpaert/Walbi-gym
```

For developpers, install in editable mode with:

```bash
pip3 install -r requirements.txt
pip3 install -e .[all]  # does the same as above
```

You will need to copy the folders from [lib](arduino-board/lib) into your local Arduino library folder.

#### Copy libraries with `setup.py`

For your convenience, use the following to copy the Arduino libraries

```bash
python3 setup.py copy_libraries -p $HOME/Arduino/libraries  # you can ommit the option if you have set ARDUINO_LIBRARIES_PATH
```

You may always copy libraries by hand of course.

### Arduino compilation

You must upload Walbi's Arduino code. To do so:

- Install Arduino IDE

- (Optional) Copy the folders from [lib](arduino-board/lib) into your local Arduino library folder

- From the Arduino IDE, choose from `File > Examples > Walbi`

## Gym environment

You may create a Walbi Gym environment as usual.

```python3
import gym
import walbi_gym  # will register env
env = gym.make('Walbi-v0')
```

The action space is a Box shaped `(10, 2)`: a target position and a given time span for each of the ten motors.

The observation space is a Box shaped `(10,)` for ten current motor positions.

A timestamp is provided in the info dictionnary.

## Hardware

### Performances

Timing measurements :

- looping on STEP (computer side) ~ 150 ms
- looping on Walbi->get_state() (Arduino only) ~ 120 ms
- test with Arduino Mega (Hardware Serial Port) ~ 215ms (get state only), 225 (step)

### Buiding Walbi

Build Walbi according to [original instructions](https://create.arduino.cc/projecthub/the-inner-geek/walbi-the-walking-biped-8feacd).

### Wiring

1. Serial
    1. Connect your Arduino Serial to your computer
    1. Connect Arduino to the Debug Board
        1. Use two `DEBUG_BOARD_RX`, `DEBUG_BOARD_TX` pins for SoftwareSerial
        1. Connect to the DebugBoard to Serial1 for HardwareSerial
1. Bluetooth (TODO)
1. Wifi (TODO)

## Versions

1. Version `0.1.0` with `protocol-v0` is simple motor observation and action
1. Version `0.1.1` with `protocol-v1` adds time interval
1. Version `0.1.2` with `protocol-v2` removes the time interval, it is now directly the timestamp in the info dictionnary
1. Version `0.1.3` with `protocol-v3` is more straightforward with less OK messages (e.g. STEP does not send ACTION anymore). Also the responsability for a reward and termination is left to the `Env`
1. Version `0.1.4` with `protocol-v4` adds correct_motor_reading to State (debug)
1. Version `0.1.5` with `protocol-v5` adds weight data to State
1. Version `0.1.6` with `protocol-v6` adds activate to Action
1. Version `0.1.7` with `protocol-v7` adds IMU data to State

## Acknowledgements

1. Data sending relies on the [serial communication code](https://github.com/araffin/arduino-robust-serial)
by Antonin Raffin, as he wrote the [robust serial library](https://medium.com/@araffin/simple-and-robust-computer-arduino-serial-communication-f91b95596788)
1. The [ServoBus library](https://github.com/slandis/ServoBus) for Arduino interacts with the DebugBoard
1. Walbi was [designed](https://create.arduino.cc/projecthub/the-inner-geek/walbi-the-walking-biped-8feacd)
by [Release the Inner Geek](https://releasetheinnergeek.com/)
