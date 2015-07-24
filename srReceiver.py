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

    recv_file = open("recvInfo", "w")
    recv_file.write(ack_host + " " + ack_port)
    recv_file.close()

    output_file = open(filename, "w")

    while True:
        data = ack_socket.recv(1024)
        unpack_struct = struct.Struct("L4L4L4s500")
            
        if data:
            deets = unpack_struct.unpack(data)
            data_type = deets[0]
            seq_num = deets[1]
            len_of_packet = deets[2]
            chunk = deets[3]
            if data_type == PacketType.DataPacket:
                seqNum = seq_num
                print "PKT RECV DATA " + str(seqNum) + " " + str(len_of_packet)
                payload = chunk
                if len(payload) != len_of_packet-12:
                    continue
                output_file.seek(seq_num*500)
                output_file.write(payload)

            elif data_type == PacketType.EOTPacket:
                seqNum = seq_num
                print "PKT RECV EOT " + str(seqNum) + " 12"
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.bind(('', 0))

                new_packet = struct.pack("L4L4L4s500", PacketType.EOTPacket, seqNum, 12, None)
                hostname = socket.gethostbyaddr(socket.gethostname())[0]
                port_num = s.getsockname()[1]
                s.sendto(new_packet, (hostname, port_num))
                s.close()
                break
    output_file.close()
    sys.exit();

if __name__ == "__main__":
    main(sys.argv[1])
