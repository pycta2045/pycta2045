import serial
import serial.tools.list_ports
port = "/dev/pts/4"
with serial.Serial(port) as ser:#,num,timeout=0) as ser:
    x = ser.readline()
    print(f'{x}')
