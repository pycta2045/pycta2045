# Communication module

## Checksum and message validity

The COM module (contained in `com.py`) is tasked with sending and receiving serial communication with other devices. For a COM object to perform its tasks, it needs to determine when a message ends and the next starts. Thus, it needs to be guided by callable objects (passed during instantiation) to determine how to separate the bytes of different messages. For example, the `CTA-2045` standard uses _Fletcher_ checksum appended to each message. Therefore, the following is a common way of instantiating `COM` objects throughout this project:

```python
cta_obj = CTA2045()
COM(...,is_valid=cta_obj.is_valid,...)
```
The `is_valid` message in the example above uses _Fletcher_ checksum to determine whether the message is valid.

## Features
* __start__: 
    * The COM module, when `start()` is invoked, starts a daemon in the background to listen for incoming messages via the given port during instantiation. It stores the received message in a thread-safe FIFO queue along with a reception timestamp in a tuple format `(message, timestamp)`.  
* __get_next_msg__: 
    * The module allows retrieving the received messages in a non-blocking manner. This method returns the next message stored in the queue. If called when the queue is empty, it raises a `TimeoutException` since the user expects a message but no message was received.
* __get_log__: 
    * COM module allows for the retrieval of all logged messages (passed messages + messages waiting in the queue to be popped).


> For more information, be sure to check out the DocStrings in the code and the example programs to learn how to use this module 