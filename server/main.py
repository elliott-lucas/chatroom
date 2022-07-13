import socket
from server import Server
ip = socket.gethostbyname(socket.gethostname())
port = 25565
name = "Test Server"

Host = Server(ip, port, name)
Host.Start()
        
