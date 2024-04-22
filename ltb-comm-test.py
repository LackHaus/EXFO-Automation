import socket 
ltb = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ltb.connect(('169.254.244.64', 5025))

ltb.sendall("LINS10:SNUM?".encode())
print(ltb.recv(4096))