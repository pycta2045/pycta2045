# scipi module
This module provides a way to interact with Programmable Instruments. It provides a __simple__ SCPI class that allows the user to send `commands` or `queries` through a network socket. Each invocation to the `send` function must specify the `command` and `command type`. `Command type` (which is either __1__ for `command`, __2__ for `query`, or __3__ for `configure`) is used to determine whether there should be a response or not. 

## Note
This module is far from complete. However, our research has shifted and there isn't an immediate need for the module. Hence, the lack of attention.  

> For more information, be sure to check out the DocStrings in the code and the example programs to learn how to use this module 