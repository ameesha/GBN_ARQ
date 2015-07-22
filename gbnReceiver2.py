import os
import socket
import sys
import time
import math
import pickle
import threading
import signal
import inspect
from packet import PacketType, Packet

requested_packet = 0
ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ack_socket.bind(('', 0))

def main(filename):
	global ack_socket

	ack_port = str(ack_socket.getsockname()[1])
	ack_host = socket.gethostbyaddr(socket.gethostname())[0]

	file = open("recvInfo", "w")
    file.write(ack_host + " " + ack_port)
    file.close()

    while True:
    	data = pickle.loads(ack_socket.recv(256))
    	if data:
    		if data.PacketType == PacketType.DataPacket:

    		elif data.PacketType == PacketType.EOTPacket:
    			# confirm you're expecting an eot packet
    			# send own EOT packet then exit


if __name__ == "__main__":
    #main(sys.argv[1])
    main("output.txt")

 # Sender:
# Sb = 0
# Sm = N − 1
# Repeat the following steps forever:
# 1. If you receive a request number where Rn > Sb 
#         Sm = Sm + (Rn − Sb)
#         Sb = Rn
# 2.  If no packet is in transmission, 
#         Transmit a packet where Sb <= Sn <= Sm.  
#         Packets are transmitted in order.

# N  = window size
# Rn = request number
# Sn = sequence number
# Sb = sequence base
# Sm = sequence max

# Receiver:
# Rn = 0
# Do the following forever:
# If the packet received = Rn and the packet is error free
#         Accept the packet and send it to a higher layer
#         Rn = Rn + 1
#         Send a Request for Rn
# Else
#         Refuse packet
#         Send a Request for Rn