<h1 align='center'>Welcome to PyCTA2045 :vulcan_salute:</h1>
<p>
    <a href="LICENSE">
        <img alt="License: MIT", src="https://img.shields.io/badge/License-MIT-yellow.svg">
    </a>
</p>

PyCTA2045 is a library that provides software adoption of the CTA2045 standard (version B). It offers features such as translating CTA2045 bytes. The hope is to aid in integrating the standard with other goals. Currently, it only provides support for level 1 CTA2045 (software) requirements. 

## Installation
### Install the dependencies
```
sudo apt-get install libatlas-base-dev libopenjp2-7 libtiff5 socat -y 
```
### Install dependencies using the requirements file
```
pip3 install -r requirements.txt
```
### __OR__ Install the library directly
```
pip3 install pycta2045
```
## Usage

Check [examples/](examples/) and documentation for more information [here](doc/)

## Virtual ports
1. use `nohup socat -d pty,link=/dev/ttyS99,raw,echo=0 pty,link=/dev/ttyS100,raw,echo=0` to create two virtual ports
    * This should run in the background and outputs the `process ID` to stdout
    * Keep the `process ID` handy
2. use one of the virtual ports as the controller end & other as the smart device's end
3. start DCM/mock on one while the smart device on the other via `python3 com.py /dev/#port_given_by_socat`
4. when done with virtual ports, use the `process ID` to kill socat's process
    * kill `process ID`

## Tests
run all tests with `python -m unittest tests/all.py`

run a specific test for a _module_ with `python -m unittest tests/module/test_module.py`

## Author

👤 **Mohammed Alsaid (mohamm-alsaid)**

* Github: [@mohamm-alsaid](https://github.com/mohamm-alsaid)
* LinkedIn: [@mohammed-alsaid](https://linkedin.com/in/mohammed-alsaid)

## Show your support

Give a ⭐️ if this project helped you!


***
_This README was generated with ❤️ by [readme-md-generator](https://github.com/kefranabg/readme-md-generator)_