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

------------------- 


### virtual ports:
1. use `socat -d pty,link=/dev/ttyS99,raw,echo=0 pty,link=/dev/ttyS100,raw,echo=0` to create two virtual ports
2. use one of the virtual ports as the DCMs end & other as the agent's end
3. start DCM/mock on one while the agent on the other via `python3 com.py /dev/#given_by_socat`


## tests:
run all tests with `python -m unittest tests/all.py`

run a specific test for a _module_ with `python -m unittest tests/module/test_module.py`