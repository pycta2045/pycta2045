# Examples
The objective of these scripts are to provide examples of how to use pycta2045 library. Some use the library to build simple receivers (DER/SGD) while other use it to build simple controllers (DCM/UCM). 

## Notes
Naturally, all the sample scripts import pycta2045. However, for organization purposes, they are kept under `examples/`. This poses an issue with python import system. __All of these examples work around the import system not looking into the parent folder__. There are other ways around this:
1. Use a virtual environment & install pycta2045 using: `pip3 install -e .`
    * This installs pycta2045 lib as an editable package
    * This might not always work as per [PEP 517](https://www.python.org/dev/peps/pep-0517/). 
2. Ensure pycta2045 installed to begin with using `pip3 install pycta2045` (__Recommended__ after the library has been published on PyPi)
3. Add the parent dir to the path (i.e. keep the folllowing line of code) 

## Dependencies
Some of the example scripts use third party libraries (such as [rich](https://github.com/willmcgugan/rich/)) to build frontends (Text UI). The `requirements.txt` included in this folder should simplify the installation of such dependencies. 
## install dependencies:
To install dependencies run: `pip3 install -r requirements.txt`