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
request_num = -1
sequence_num = 0
sequence_base = 0
sequence_max = 9
payload_max = 500
timeout = -1
ACK = 0
portnum = 0
hostname = ""
num_packets_sent = 0
num_packets_acked = 0
total_packets = 0
file_contents = []
round_trip_time = 0.1


current_milli_time = lambda: int(round(time.time() * 1000))
ack_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ack_socket.bind(('', 0))
ack_port = str(ack_socket.getsockname()[1])
ack_host = socket.gethostbyaddr(socket.gethostname())[0]
lock = threading.RLock()

def main(tout, filename):
    global timeout
    global portnum
    global hostname
    global total_packets
    global payload_max
    
    timeout = tout
    channelInfo = open("channelInfo", 'r')
    deets = channelInfo.read().split(' ')
    hostname = deets[0]
    portnum = int(deets[1])
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    signal.signal(signal.SIGALRM, timer)
    
    file_contents = []
    print filename
    try:
        with open(filename, 'rb') as f:
	    sequenceNum = 0
            while True:
		print "WHILE START"
                packet = Packet()
                f.seek(sequenceNum * payload_max)
                packet.changeSequenceNum(sequenceNum)
		print "before chunk made"
                chunk = f.read(payload_max)
		print str(len(chunk))
                if chunk:
                    packet.payload = chunk
                    packet.overridePacketLength(len(chunk))
                    file_contents.append(packet)
                    print "PKT SEND EOT " + str(sequenceNum) + " " + str(packet.total_packet_length)
                    #clientSocket.sendto(pickledPacket, (hostname, portnum))
                    sequenceNum = sequenceNum + 1
                else:
                    break
    except:
        print "Failed to open file to transmit"
        sys.exit(0)

    total_packets = len(file_contents)
    sendFile(clientSocket, file_contents)
    threading.Thread(target=receiveAckThread, args=(clientSocket)).start()
    clientSocket.close()

def timer():
    global ACK
    global round_trip_time
    global sequence_base
    global sequence_max
    global total_packets

    resent_index = sequence_base
    if ACK == sequence_base:
        print "Timeout sequence number = " + str(ACK)
        lock.acquire()
        while resent_index <= sequence_max and resent_index < total_packets:
            signal.alarm(timeout)
            signal.setitimer(signal.ITEMER_REAL, round_trip_time)
            socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            port_num = str(socket.getsockname()[1])
            hostname = socket.gethostbyaddr(socket.gethostname())[0]
            pickledPacket = pickle.dumps(file_contents[resent_index])
            socket.sendto(pickledPacket)
            socket.close()
        lock.release()

def sendFile(clientSocket, file_contents):
    global sequence_num
    global sequence_base
    global sequence_max
    global ACK
    global num_packets_sent

    packets_to_send = []
    current_max_window = min(window_size, total_packets)
    while num_packets_sent < current_max_window:
        if ACK == 0:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            port_num = str(s.getsockname()[1])
            hostname = socket.gethostbyaddr(socket.gethostname())[0]
            pickledPacket = pickle.dumps(file_contents[num_packets_sent])
            s.sendto(pickledPacket, (hostname, port_num))
            print "PKT SEND EOT " + str(file_contents[num_packets_sent].sequenceNum) + " " + str(file_contents[num_packets_sent].total_packet_length)
            s.close()
            num_packets_sent = num_packets_sent + 1
        else:
            break

def receiveAckThread(clientSocket):
    global sequence_max
    global sequence_base
    global num_packets_sent
    global num_packets_acked
    global total_packets
    global ACK
    global done_transmitting

    done_transmitting = 0
    while True:
        data = pickle.loads(ack_socket.recv(256))
        if data.packetType == PacketType.ACKPacket:
            ACK = data.sequenceNum
            if ACK:
                lock.acquire()
                if ACK >= sequence_base and ACK < total_packets:
                    signal.alarm(timeout)
                    signal.setitimer(signal.ITIMER_REAL, round_trip_time)
                    temp_packets_acked = ACK - sequence_base
                    old_sequence_max = sequence_max
                    sequence_max = min(sequence_max + ACK - sequence_base, total_packets -1)
                    sequence_base = ACK
                    num_packets_acked = num_packets_acked + temp_packets_acked
                    for i in range(sequence_max-old_sequence_max):
                        socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        port_num = str(socket.getsockname()[1])
                        hostname = socket.gethostbyaddr(socket.gethostname())[0]
                        pickledPacket = pickle.dumps(file_contents[num_packets_send])
                        socket.sendto(pickledPacket)
                        print "PKT SEND EOT " + str(file_contents[num_packets_sent].sequenceNum) + " " + str(file_contents[num_packets_sent].total_packet_length)
                        socket.close()
                        if num_packets_sent < total_packets-1:
                            num_packets_sent = num_packets_sent + 1
                elif ACK == total_packets:
                    print "DONE"
                    done_transmitting = 1
                    exit()

if __name__ == "__main__":
   #main(sys.argv[1], sys.argv[2])
    main(9999999999999, "helloWorld.py")
