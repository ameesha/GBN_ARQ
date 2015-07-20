import os
import socket
import sys
import time
import math
import pickle
from packet import PacketType, Packet

current_milli_time = lambda: int(round(time.time() * 1000))

def main(tout, filename):
    timeout = current_milli_time() + tout
    sequenceNum = 0
    payload_max = 500
    
    channelInfo = open("channelInfo", 'r')
    deets = channelInfo.read().split(' ')
    hostname = deets[0]
    portnum = int(deets[1])
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    bytes_to_send = int(os.stat(filename).st_size)
    print str(bytes_to_send)
    numPacketsMin = math.ceil(bytes_to_send / payload_max)

    previous_ack_num = -1
    

    with open(filename, 'rb') as f:
        while True and current_milli_time() < timeout:

            
            
            packet = Packet()
            f.seek(sequenceNum * payload_max)
            packet.changeSequenceNum(sequenceNum)
            chunk = f.read(payload_max)
            if chunk:
                packet.payload = chunk
                packet.overridePacketLength(len(chunk))
                pickledPacket = pickle.dumps(packet)
                print "PKT SEND DAT " + str(sequenceNum) + " " + str(packet.total_packet_length)
                clientSocket.sendto(pickledPacket, (hostname, portnum))
                sequenceNum = sequenceNum + 1

                #if sequenceNum % 10 == 1:
                    # clientSocket.listen(1)
                    #with clientSocket.accept()[0] as c:
                     #   while True and current_milli_time < timeout:
                      #      chunk = c.recv(2048)
                       #     if chunk:
                        #        print len(chunk)
                         #       if chunk.PacketType is PacketType.ACKPacket:
                          #          if chunk.sequence_num == previous_ack_num:
                           #             seqenceNum = chunk.sequence_num
                            #        else:
                             #           previous_ack_num = chunk.sequence_num                        
            else:
                # call list
                while previous_ack_num != numPacketsMin:
                    with clientSocket.accept()[0] as c:
                        while True and current_milli_time < timeout:
                            chunk = c.recv(2048)
                            if chunk:
                                print len(chunk)
                                if chunk.PacketType is PacketType.ACKPacket:
                                    if chunk.sequence_num == previous_ack_num:
                                        seqenceNum = chunk.sequence_num
                                    else:
                                        previous_ack_num = chunk.sequence_num 
                    
                packet.changePacketType = PacketType.EOTPacket
                packet.updateEmptyPacketLength()
                pickledPacket = pickle.dumps(packet)
                print "PKT SEND EOT " + str(sequenceNum) + " " + str(packet.total_packet_length)
                clientSocket.sendto(pickledPacket, (hostname, portnum))
                break

    if current_milli_time() >= timeout:
        print "TIMEOUT"
        packet = Packet()
        packet.changeSequenceNum(sequenceNum)
        packet.changePacketType = PacketType.EOTPacket
        packet.updateEmptyPacketLength()
        pickledPacket = pickle.dumps(packet)
        print "PKT SEND EOT " + str(sequenceNum) + " " + str(packet.total_packet_length)
        clientSocket.sendto(pickledPacket, (hostname, portnum))
        
if __name__ == "__main__":
   #main(sys.argv[1], sys.argv[2])
    main(9999999999999, "helloworld.py")
