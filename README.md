# Neon Installer

Neon is a software collection and configuration that allows you to use something
like a Raspberry Pi to act as an AirPlay target.

## How to use

0. Spray a [fedora arm minimal](https://www.raspberrypi.org/forums/viewtopic.php?f=51&t=101027&sid=978beab1105eb6fd5318755628bdf402) image on sd card, and put that in your raspberry pi.
0. [Download this repo.](https://github.com/jetpks/neon/archive/v0.1.tar.gz)
0. `./stage_one` # will reboot box
0. `./stage_two` 




## Dirty Note

This installer project values dependency minimization over clean code. As a
result, there will be a lot of shelling out bash to accomplish things rather
than using the appropriate module from PyPi. Sorry, not sorry.
