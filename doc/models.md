# model module
This module contains an abstract base class (`CTA2045Model`) for DERs (i.e. smart devices). It specifies the required methods by [__CTA2045Device__](device.md) module for the DER mode of operation. These methods along with the methods provided by the __CTA2045Device__ module allow the device to meet CTA2045 level 1 requirements (_software_ requirements only).

## Example
The ev_model in `examples/` shows an example of usage. The example _attempts_ to implement a simple Electric Vehicle model. The thing to note is that it inherits from the `CTA2045Model` and implements all the required methods. 

> For more information, be sure to check out the DocStrings in the code and the example programs to learn how to use this module 