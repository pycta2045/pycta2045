# CTA2045Device module

### Acronyms
* DER: Distributed Energy Resource
* DCM: Distributed Control Module

This module provides an interface to a CTA2045 device with a level of abstraction. The user doesn't need to know the details about the CTA2045 protocol. Out of the box, it requires only knowing the _serial port_ and mode of operation. The mode of _operation_ can either be a smart device (DER) or a controller (DCM). 
 

## Features
*  __send__: A method that allows the user to send CTA2045 commands through the port. The method uses the `cta2045` module to translate the command before sending it. 
*  __run__: A method to start the CTA2045Device. It ensures the listener is started and running. It takes `block (bool)` as an argument, which affects how the device is run. In the `block` mode, the method blocks execution and becomes verbose. If the `block` argument is false, the is non-blocking (and not verbose). Calling this method results in creating threads. Therefore, make sure there is a matching call to __stop__ when the device is no longer needed. The threads created by this method are all daemons, nevertheless, ensure there is a matching call to __stop__ for safety purposes.
*  __get_log__: A method to get the _complete_ log of CTA2045 captured communication. It could be useful when the device is running in a non-blocking manner.  
*  __stop__: A method to stop all the active threads in the background. It is also invoked upon deletion of the device. 

> For more information, be sure to check out the DocStrings in the code and the example programs to learn how to use this module 