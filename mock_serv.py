import socket
timeout = 1 # timeout len used in connection
port = 5025 # port used for connection
buf_sz = 1024 # size of buffer used in recv
addr = "127.0.0.1" # using local mock

ss = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # server socket
# ss.settimeout(timeout) # time out in secs
ss.bind((addr,port)) # bind instead of connect
ss.listen(5)

cmd = ''
res = '200'
try:
    while True:
        (cs,add) = ss.accept()
        data = ''
        try:
            while data != 'QUIT':
                data = cs.recv(buf_sz)
                cs.send(res.encode())
                data = data.decode()
                print(data)
        except Exception as e:
            cs.close()
    ss.close()
except Exception as e:
    ss.close()
    print(e)