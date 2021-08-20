# DER agent simulator for CTA 2045
## what I need to do:
* add the following vars to the class:
* * intial battery SOC
* * ramp rate
* * constant current (linear)
* * constant voltage periods (linear)
* * time delay

phases:
1. pre-charge: current is kept low
2. starts when the EV has < 10% of SOC of (10%)




### virtual ports:
1. use `socat -d -d pty,raw,echo=0 pty,raw,echo=0` to create two virtual ports
2. use one of the virtual ports as the DCMs end & other as the agent's end
3. start DCM/mock on one while the agent on the other via `python3 com.py /dev/pts/#given_by_socat`


## tests:
>__NOTE__: Com unittests rely on the creation of a virtual serial port. To do so, it creates two virtual comports using socat (```ttyUSB99 and ttyUSB100```). The numbers were chosen (ignorantly) based on the idea that they should far away from any actual existing comports. Thus avoiding collisions with actual comports.

run all tests with `python -m unittest tests/all.py`

run a specific test with `python -m unittest tests/test.py`