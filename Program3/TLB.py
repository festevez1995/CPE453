import sys

class TLB:
    def __init__(self):
        self.tlb = {}
        self.tlbSize = 16

    def addToTLB(self, pageNum, frame):
        self.tlb[pageNum] = frame

    def getFromTLB(self, pageNum):
        return self.tlb[pageNum]

    def deleteFrameFromTLB(self, frame):
        for key in self.tlb.keys():
            if self.tlb[key] == frame:
                # print("Deleting page Number: %d" % key)
                self.tlb.pop(key)
                break

    def isTLBFull(self):
        if len(self.tlb) > self.tlbSize - 1:
            return True
        return False

    def pageNumInTLB(self, pageNum):
        if pageNum in self.tlb:
            return True
        return False

    def freeTLBFrame(self):
        # Remove element in the tlb table
        self.tlb.pop(next(iter(self.tlb)))
