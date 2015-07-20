import os
import socket
import sys
import time
from packet import PacketType, Packet

def main(filename):
    sequenceNum = 1
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSocket.bind(('', 0))
    portNum = str(serverSocket.getsockname()[1])
    hostName = socket.gethostbyaddr(socket.gethostname())[0]
    file = open("recvInfo", "w")
    file.write(hostName + " " + portNum)
    file.close()

    serverSocket.listen(1)
    with serverSocket.accept()[0] as c:
        chunks = []
        while True:
            chunk = c.recv(2048)
            if chunk:
                print len(chunk)
            if not chunk:
                break
##            chunks.append(chunk)
##    with open(filename, 'wb') as f:
##        f.write(b''.join(chunks))
