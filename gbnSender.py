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

current_milli_time = lambda: int(round(time.time() * 1000))

def ack_listen():
    clientSocket.listen(1)
    with clientSocket.accept()[0] as c:
       while True:
          chunk = c.recv(2048)
          if chunk:
              print len(chunk)
              if chunk.PacketType is PacketType.ACKPacket:
                  if chunk.sequence_num == previous_ack_num:
                      seqenceNum = chunk.sequence_num
                  else:
                      previous_ack_num = chunk.sequence_num                            

def sendFile(chunk):
    packet.payload = chunk
    packet.overridePacketLength(len(chunk))
    pickledPacket = pickle.dumps(packet)
    print "PKT SEND DAT " + str(sequenceNum) + " " + str(packet.total_packet_length)
    clientSocket.sendto(pickledPacket, (hostname, portnum))
    sequenceNum = sequenceNum + 1

def timeout_handler(timeout):
    while True:
        if current_milli_time > timeout:
            print "PKT TIMEOUT, exiting program...."
            sys.exit(0)

def main(tout, filename):
    # start timeout timer
    timeout = current_milli_time() + tout
    thread = threading.Thread(target=timeout_handler, args=(timeout))
    thread.daemon = True
    thread.start

    global sequenceNum
    global payloadMax
    global bytes_to_send
    global numPacketsMin
    global previousAckNum
    global clientPortNum
    global clientHostName

    # fill out global variables
    sequenceNum = 0
    payloadMax = 500
    previousAckNum = None
    channelInfo = open("channelInfo", 'r')
    deets = channelInfo.read().split(' ')
    hostname = deets[0]
    portnum = int(deets[1])
    clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    clientSocket.bind(('', 0))
    clientPortNum = str(clientSocket.getsockname()[1])
    clientHostName = socket.gethostbyaddr(socket.gethostname())[0]
    bytes_to_send = int(os.stat(filename).st_size)
    numPacketsMin = math.ceil(bytes_to_send / payloadMax)    

    try:
        with open(filename, 'rb') as f:
            while True:
                if sequenceNum % 10 == 1 and sequenceNum != 0:
                    ack_listen()

                packet = Packet()
                f.seek(sequenceNum * payload_max)
                packet.changeSequenceNum(sequenceNum)
                chunk = f.read(payload_max)
                if chunk:
                    sendFile()
                    
                        
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
#                    while previous_ack_num != numPacketsMin:
 #                       with clientSocket.accept()[0] as c:
  #                          while True and current_milli_time < timeout:
   #                             chunk = c.recv(2048)
    #                            if chunk:
     #                               print len(chunk)
      #                              if chunk.PacketType is PacketType.ACKPacket:
       #                                 if chunk.sequence_num == previous_ack_num:
        #                                    seqenceNum = chunk.sequence_num
         #                               else:
          #                                  previous_ack_num = chunk.sequence_num 
                        
                    packet.changePacketType = PacketType.EOTPacket
                    packet.updateEmptyPacketLength()
                    pickledPacket = pickle.dumps(packet)
                    print "PKT SEND EOT " + str(sequenceNum) + " " + str(packet.total_packet_length)
                    clientSocket.sendto(pickledPacket, (hostname, portnum))
                    break

    except:
        print "PKT Failed to open file"
        sys.exit(0)

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
