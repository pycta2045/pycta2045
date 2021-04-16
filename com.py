import serial
import serial.tools.list_ports
port = "/dev/ttyS6"
ports = serial.tools.list_ports.comports()
with serial.Serial(port) as ser:#,num,timeout=0) as ser:
    x = ser.read(10)
    print(f'{x}')
#print(ports)
