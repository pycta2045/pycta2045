import socket

ip = "192.168.0.153"
port = 5025

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.settimeout(1)

print(f"connecting to {ip}:{port} ...")
s.connect((ip,port))

s.send(b"SYST:RWL\n")
print(s.recv(1024))



s.send(b"*IDN?\n")

print(s.recv(1024))

s.send(b"SYST:LOC\n")
print(s.recv(1024))


s.close()
