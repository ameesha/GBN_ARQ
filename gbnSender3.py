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

window_size = 10
request_num = 01
sequence_num = 0
sequence_base = 0
sequence_max = 9
timeout = -1
payload_max = 500
expected_ack_num = 0
num_packets_sent = 0
num_packets_acked = 0
total_packets = 0
file_contents = []
hostname = ""
portnum = -1

current_milli_time = lambda: int(round(time.time() * 1000))
ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ack_socket.bind(('', 0))
#ack_port = str(ack_socket.getsockname()[1])
#ack_host = socket.gethostbyaddr(socket.gethostname())[0]
# lock = threading.RLock()

def receiveAckThread():
    global expected_ack_num

    while True:
        data = pickle.loads(ack_socket.recv(256))
        if data:
            if data.packetType == PacketType.ACKPacket:
                recv_seq_num = data.sequence_num
                print "PKT RECV ACK " + str(recv_seq_num) + str(data.total_packet_length)
                if recv_seq_num == expected_ack_num:
                    expected_ack_num = expected_ack_num + 1
                    sequence_base = sequence_base + 1
                    sequence_max = sequence_max + 1
                    sendFile(sequence_max, False)
            elif data.packetType == PacketType.EOTPacket:
                recv_seq_num = data.sequence_num
                print "PKT RECV EOT " + str(recv_seq_num) + str(data.total_packet_length)             
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
    print "\n SEQNUM: " + str(seqNum) + " " + str(total_packets) + "\n"
    if seqNum >= total_packets:
        packet = Packet()
        packet.PacketType = PacketType.EOTPacket
        packet.changeSequenceNum(seqNum)
        packet.updateEmptyPacketLength()
        pickledPacket = pickle.dumps(packet)
    else:
       pickledPacket = pickle.dumps(file_contents[seqNum])
    
    s.sendto(pickledPacket, (hostname, portnum))
    if seqNum >= total_packets:
        print "PKT SEND EOT " + str(seqNum) + " 12"
    else:
        print "PKT SEND DATA " + str(seqNum) + " " + str(file_contents[seqNum].total_packet_length)
    threading.Thread(target=waitingForTimeout, args=([seqNum])).start()    

def sendFiles(clientSocket):
    print "SEND FILE CALLED"
    global file_contents
    global window_size
    global sequence_base
    global sequence_max
    global total_packets
    global num_packets_sent
    global timeout
    global hostname
    global portnum

    current_max_window = min(sequence_max, total_packets-1)
    while num_packets_sent <= current_max_window:
        print str(num_packets_sent) + " " + str(current_max_window)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 0))
        sequenceNum = file_contents[num_packets_sent].sequenceNum
        pickledPacket = pickle.dumps(file_contents[num_packets_sent])

        # hostname = socket.gethostbyaddr(socket.gethostname())[0]
        # port_num = s.getsockname()[1]
        
        s.sendto(pickledPacket, (hostname, portnum))
        print "PKT SEND DATA " + str(sequenceNum) + " " + str(file_contents[num_packets_sent].total_packet_length)

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
    
    timeout = tout
    channelInfo = open("channelInfo", 'r')
    deets = channelInfo.read().split(' ')
    hostname = deets[0]
    portnum = int(deets[1])
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print filename
    try:
        with open(filename, 'rb') as f:
            sequenceNum = 0
            while True:
                packet = Packet()
                f.seek(sequenceNum * payload_max)
                packet.changeSequenceNum(sequenceNum)
                chunk = f.read(payload_max)
                if chunk:
                    packet.payload = chunk
                    packet.overridePacketLength(len(chunk))
                    file_contents.append(packet)
                    #print "PKT SEND EOT " + str(sequenceNum) + " " + str(packet.total_packet_length)
                    sequenceNum = sequenceNum + 1
                else:
                    break
    except:
        print "Failed to open file to transmit"
        sys.exit(0)

    total_packets = len(file_contents)
    sendFiles(clientSocket)


if __name__ == "__main__":
   #main(sys.argv[1], sys.argv[2])
    main(100, "helloWorld.py")

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
        
