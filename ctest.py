import socket
s=socket.socket()
## getting the hostname by socket.gethostname() method
hostname = socket.gethostname()
## getting the IP address using socket.gethostbyname() method
host = socket.gethostbyname(hostname)     #This is your Server IP!
port=2345
s.connect((host,port))
s.send(b"hello")
rece=s.recv(1024)
print("Received",rece)
s.close()