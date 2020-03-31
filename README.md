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
pip3 install -e .  # does the same as above
```

The install will take care of the URDF files.

#### Simulation

For simulation, we use `diy-gym` ([github](https://github.com/ascentai/diy-gym)). The repo should already be cloned thanks to the recursive command, otherwise use:

```bash
cd walbi/
git clone https://github.com/ascentai/diy-gym
cp walbi_gym/data/* diy-gym/diy_gym/data
```

Once you have the repository, run :

```bash
cd diy-gym
# pip install -r requirements.txt # already in setup.py from walbi_gym
pip install -e .
```

#### Arduino

To use IRL Walbi you will need to upload a sketch. You will need libraries and a `.ino` sketch.

You will need to copy the folders from [lib](arduino-board/lib) into your local Arduino library folder.

#### Copy libraries with `setup.py`

For your convenience, use the following to copy the Arduino libraries

```bash
python3 setup.py copy_libraries -p $HOME/Arduino/libraries  # you can ommit the option if you have set ARDUINO_LIBRARIES_PATH
```

You may otherwise copy the libraries by hand of course.

### Arduino compilation

To upload Walbi's Arduino code, follow the instructions :

- Install Arduino IDE

- Copy the folders from [lib](arduino-board/lib) into your local Arduino library folder

- From the Arduino IDE, choose from `File > Examples > Walbi`

## Gym environment

The information here will be updated shortly

```
You may create a Walbi Gym environment as usual.

#python3
#import gym
#import walbi_gym  # will register env
#env = gym.make('Walbi-v0')
#

The action space is a Box shaped `(10, 2)`: a target position and a given time span for each of the ten motors.

The observation space is a Box shaped `(10,)` for ten current motor positions.

A timestamp is provided in the info dictionnary.
```

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
1. Version `0.2.0` (beta) with `protocol-v8` is a simplification of the protocol and breaks pervious API

## Acknowledgements

1. Data sending relies on the [serial communication code](https://github.com/araffin/arduino-robust-serial)
by Antonin Raffin, as he wrote the [robust serial library](https://medium.com/@araffin/simple-and-robust-computer-arduino-serial-communication-f91b95596788)
1. The [ServoBus library](https://github.com/slandis/ServoBus) for Arduino interacts with the DebugBoard
1. [Do It Yourself gym](https://github.com/ascentai/diy-gym) is a surprisingly simple framework for fast gym env prototyping
1. The URDF files for the biped come from Einsbon's [Bipedal robot walking simulation](https://github.com/Einsbon/bipedal-robot-walking-simulation)
1. Walbi was originaly [designed](https://create.arduino.cc/projecthub/the-inner-geek/walbi-the-walking-biped-8feacd)
by [Release the Inner Geek](https://releasetheinnergeek.com/)
