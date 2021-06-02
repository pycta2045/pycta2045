import socket

s = socket.sockeet(socket.AF_INET,socket.SOCK_STREAM)
s.settimeout(1)
s.connect(("192.168.0.3",5025))

s.send("SYST:RWL\n")


s.send("*IDN?\n")

prnt(s.recv(1024))

s.send("SYST:LOC\n")


s.close()
