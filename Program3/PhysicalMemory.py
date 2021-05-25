import sys
from collections import OrderedDict

class PhysicalMemory:

    def __init__(self, frames):
        # Create a memory table
        self.memory = []
        self.cache = OrderedDict()
        # Physical memory of size in bytes
        self.memorySize = frames
        # save frames
        self.frames = frames
        # boolean to inidcate when memory is full
        self.isFull = False
        self.removeIdx = 0
        # Initialize memory
        self.initMemory()

    # Initializes memory to all 0's
    def initMemory(self):
        # iterate through the entire table
        for i in range(self.memorySize):
            # insert at each idx a 0
            self.memory.insert(i, 0)
            self.cache[i] = 0

    # finds the next available frame in memory
    def findFreeFrame(self):
        freeFrameIdx = 0
        # Holds the idx of the next available frame
        freeFrameIdx = -1
        if self.isMemFull():
            return freeFrameIdx
        # iterate through memory and find frame
        for frame in self.memory:
            freeFrameIdx += 1
            if frame == 0:
                return freeFrameIdx
        return freeFrameIdx

    # Check to see if memory is full
    def isMemFull(self):
        for x in range(self.memorySize):
            if self.memory[x] == 0:
                self.isFull = False
                return False
        return True

    # Adds frame to memory
    def addFrame(self, idx, frame):
        self.memory[idx] = frame
        self.cache[idx] = frame
        self.cache.move_to_end(idx)

    # Get frame from memory
    def getFrame(self, idx):
        self.cache.move_to_end(idx)
        return self.memory[idx]

    def deleteFrame(self, idx):
        self.memory[idx] = 0

    def getIdx(self, frame):
        idx = -1
        for targetFrame in self.memory:
            idx += 1
            if targetFrame is frame:
                return idx
        return idx

    def printMemory(self):
        idx = 0
        for frame in self.memory:
            print("%d Memory: %x\n"%(idx, 1))
            idx += 1

    def shiftMemory(self):
        # Removes the memrory at idx 0
        # self.memory.pop(self.removeIdx)
        if self.removeIdx > self.frames - 1:
            self.removeIdx = 0

        frame = self.memory[self.removeIdx]
        self.memory.pop(self.removeIdx)
        # adds an empty frame at the end of the memory
        self.memory.insert(self.removeIdx, 0)
        self.removeIdx += 1
        return frame

    def frameInMemory(self, frame):
        for targetFrame in self.memory:
            if targetFrame == frame:
                return True
        return False

    def pageNumInMemory(self, pageNum):
        if pageNum > self.memorySize:
            return False
            
        if self.memory[pageNum] == 0:
            return False
        return True

    def deleteFrameFromMemory(self, frame):
        idx = 0
        for targetFrame in self.memory:
            if targetFrame == frame:
                self.memory[idx] = 0
            idx += 1

    def leastRecentlyUsed(self):
        val = self.cache.popitem(last=False)
        # self.cache[val[0]] = 0
        self.deleteFrameFromMemory(val[1])
        return val

    def printCache(self):
        for key in self.cache.keys():
            if self.cache[key] == 0:
                print("Key: {}, Val: {}".format(key, 0))
            else:
                print("Key: {}, Val: {}".format(key, 1))
