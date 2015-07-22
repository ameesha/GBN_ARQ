﻿import os
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

    recv_file = open("recvInfo", "w")
    recv_file.write(ack_host + " " + ack_port)
    recv_file.close()

    output_file = open(filename, "w")

    while True:
        data = pickle.loads(ack_socket.recv(256))
        if data:
            if data.PacketType == PacketType.DataPacket:
                seqNum = data.sequence_num
                total_length = data.total_packet_length
                print "PKT RECV DATA " + str(seqNum) + " " + str(data.total_packet_length)
                if seqNum == requested_packet:
                    payload = data.payload
                    if len(payload) != total_length-12:
                        continue
                    output_file.write(payload)
                    requested_packet = requested_packet + 1
                else:
                    continue

            elif data.PacketType == PacketType.EOTPacket:
                seqNum = data.sequence_num
                print "PKT RECV EOT " + str(seqNum) + " 12"
                if seqNum == requested_packet:
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.bind(('', 0))
                    packet = Packet()
                    packet.PacketType = PacketType.EOTPacket
                    packet.changeSequenceNum(seqNum)
                    packet.updateEmptyPacketLength()
                    pickledPacket = pickle.dumps(packet)
                    hostname = socket.gethostbyaddr(socket.gethostname())[0]
                    port_num = s.getsockname()[1]
                    s.sendto(pickledPacket, (hostname, port_num))
                    s.close()
                    break
    output_file.close()
    sys.exit();

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
