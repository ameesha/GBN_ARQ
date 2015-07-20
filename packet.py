class PacketType:
    DataPacket = 0
    ACKPacket = 1
    EOTPacket = 2

class Packet:
    def __init__(self):
        self.packetType = 0
        self.sequenceNum = 0
        self.packetLength = 0
        self.payload = None

    def changePacketType(self, typeNum):
        self.packetType = typeNum

    def changeSequenceNum(self, seqNum):
        self.sequenceNum = seqNum

    def updateEmptyPacketLength(self):
        self.packetLength = 12

    def overridePacketLength(self, lenOfPayload):
        self.packetLength = 12 + lenOfPayload

    @property
    def total_packet_length(self):
        return self.packetLength

    @property
    def packet_length(self):
        return self.packetLength - 12

    @property
    def packet_type(self):
        return self.packetType

    @property
    def sequence_num(self):
        return self.sequenceNum

    @property
    def payload(self):
        return self.payload
