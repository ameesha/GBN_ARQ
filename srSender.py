import os
import socket
import sys
import time
import math
import pickle
import threading
import signal
import inspect
import struct
from packet import PacketType, Packet

window_size = 10
request_num = 01
sequence_num = 0
sequence_base = 0
sequence_max = 9
timeout = -1
payload_max = 463
expected_ack_num = 0
num_packets_sent = 0
num_packets_acked = 0
total_packets = 0
file_contents = []
len_of_chunks = []
hostname = ""
portnum = -1

current_milli_time = lambda: int(round(time.time() * 1000))
ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ack_socket.bind(('', 0))

def receiveAckThread():
    global expected_ack_num

    unpack_struct = struct.Struct("L4L4L4s0")

    while True:
        data = ack_socket.recv(1024)
        deets = unpack_struct.unpack(data)
        data_type = deets[0]
        seq_num = deets[1]
        len_of_packet = deets[2]
        if data:
            if data_type == PacketType.ACKPacket:
                recv_seq_num = seq_num
                print "PKT RECV ACK " + str(recv_seq_num) + str(len_of_packet)
            elif data_type == PacketType.EOTPacket:
                recv_seq_num = seq_num
                print "PKT RECV EOT " + str(recv_seq_num) + str(len_of_packet)             
                print "Done receiving acks"
                sys.exit()


def waitingForTimeout(seqNum):
    global current_milli_time
    global timeout
    global expected_ack_num
    global expected_ack_num

    print "WAITING FOR TIMEOUT " + str(seqNum)

    timeout_time = current_milli_time() + timeout
    while current_milli_time() <= timeout_time and expected_ack_num <= seqNum:
        continue
    if expected_ack_num <= seqNum:
        sendFile(seqNum, True)

def sendFile(seqNum, timeout_happened):
    global portnum
    global hostname

    if timeout_happened:
        print "TIMEOUT " + str(seqNum)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', 0))
    
    pickledPacket = None
    packet = None
    if seqNum >= total_packets:
        packet = struct.pack("!L4", PacketType.EOTPacket)
        packet += struct.pack("!L4", sequenceNum)
        packet += struct.pack("!L4", 12)
    else:
       packet = file_contents[seqNum]
    
    s.sendto(packet, (hostname, portnum))
    if seqNum >= total_packets:
        print "PKT SEND EOT " + str(seqNum) + " 12"
    else:
        print "PKT SEND DATA " + str(seqNum) + " " + str(len_of_chunks[seqNum].total_packet_length)
    threading.Thread(target=waitingForTimeout, args=([seqNum])).start()    

def sendFiles(clientSocket):
    global file_contents
    global window_size
    global sequence_base
    global sequence_max
    global total_packets
    global num_packets_sent
    global timeout
    global hostname
    global portnum
    global len_of_chunks

    current_max_window = min(sequence_max, total_packets-1)
    while num_packets_sent <= current_max_window:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 0))
        packet = file_contents[num_packets_sent]
        packet_deets = len_of_chunks[num_packets_sent]
        sequenceNum = packet_deets.sequence_num
        
        s.sendto(packet, (hostname, portnum)) 
        print "PKT SEND DATA " + str(sequenceNum) + " " + str(packet_deets.total_packet_length)

        # timeout thread
        threading.Thread(target=waitingForTimeout, args=([sequenceNum])).start()

        s.close()
        num_packets_sent = num_packets_sent + 1

def main(tout, filename):
    global timeout
    global hostname
    global portnum
    global file_contents
    global total_packets
    global payload_max
    global len_of_chunks
    
    timeout = int(tout)
    channelInfo = open("channelInfo", 'r')
    deets = channelInfo.read().split(' ')
    hostname = deets[0]
    portnum = int(deets[1])
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print payload_max
    print filename
    try:
        with open(filename, 'rb') as f:
            sequenceNum = 0
            while True:
                packet = struct.pack("L4", PacketType.DataPacket)
                packet += struct.pack("L4", sequenceNum)

                f.seek(sequenceNum * payload_max)
                chunk = f.read(payload_max)
                if chunk:
                    length_of_chunk = sys.getsizeof(chunk)
                    packet += struct.pack("L4", length_of_chunk+12)
                    print length_of_chunk
                    packet += struct.pack("s"+str(length_of_chunk), chunk)
                    file_contents.append(packet)
                    chunk_packet = Packet()
                    chunk_packet.changeSequenceNum(sequenceNum)
                    chunk_packet.overridePacketLength(length_of_chunk)
                    len_of_chunks.append(chunk_packet)
                    sequenceNum = sequenceNum + 1
                else:
                    break
    except:
        print "Failed to open file to transmit"
        sys.exit(0)

    total_packets = len(file_contents)
    sendFiles(clientSocket)


if __name__ == "__main__":
   main(sys.argv[1], sys.argv[2])
    # main(99999, "helloWorld.py")        
