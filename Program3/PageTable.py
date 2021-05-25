import sys

class PageTable:

    def __init__(self, frames, pra):
        self.pageTable = []
        self.pageSize = 256
        self.frames = 256
        self.alg = pra
        self.initPageTable()

    # Initializes the page table to A tuple of 0's.
    def initPageTable(self):
        # iterate through page size
        for x in range(self.pageSize):
            self.pageTable.insert(x, 0)

    # Add frame number to the pageTable
    # pageNum = index to add frame
    # frame = data
    def addToTable(self, frame, pageNum):
        # adding frame into pageTable
        self.pageTable[pageNum] = frame

    def deleteFrame(self, frame):
        idx = 0
        # print("Trying to delete from page tble")
        for val in self.pageTable:
            if val is frame:
                # print("Deleting at idx %d"%idx)
                self.pageTable[idx] = 0
                break
            idx += 1

    def printTable(self):
        idx = 0
        for x in self.pageTable:
            if x == 0:
                print("Page Number: ", idx, " Frame: ", 0)
            else:
                print("Page Number: ", idx, " Frame: ", self.parsMyFrame(x))
            idx += 1


    # Function to check if page num exists in page table.
    # Returns True if it exists in page table
    # returns False if it doesn't exist in page table
    def isInPageTable(self, pageNum):
        # pull tuple frame from pageTable
        frame = self.pageTable[pageNum]
        # Check to see if frame is valid
        if(frame != 0):
            # if valid flag, frame in pageTable
            return True
        # else frame not in pageTable
        return False

    def frameInPageTable(self, frame):
        for targetFrame in self.pageTable:
            if targetFrame == frame:
                return True
        return False

    def parsMyFrame(self, frame):
        fullFrame = hex(int.from_bytes(frame, byteorder='big', signed=True))
        # Length of the frames - '0x'
        frameLen = len(fullFrame) - 2
        # remove the 0x from the start
        parsedFrame = fullFrame[2:]
        # add leading 0's if frame is smaller than 512 from_bytes
        if frameLen < 512:
            parsedFrame = '0'*(512 - frameLen) + parsedFrame
        # Uppercase the letters.
        return parsedFrame.upper()

    def pageFaultHandler(self, tlb, memory, pageNum, pageOff):
        # Open up the backing store .bin file
        backingStore = open("BACKING_STORE.bin", "rb")
        # Find the position you want to read from the file
        backingStore.seek(self.frames * pageNum)
        # Read and obtain the frame.
        freeFrame = backingStore.read(self.frames)
        test = self.parsMyFrame(freeFrame)
        # Check to see if free fram does not exist in memory
        if not memory.frameInMemory(freeFrame):
            # find a free idx if there is space in the memory
            freeFrameIdx = memory.findFreeFrame()
            # If free frame is available, use it
            if freeFrameIdx != -1:
                # print("Frame not in memory")
                # add frame to memory
                memory.addFrame(freeFrameIdx, freeFrame)
                # if no free frame, use page replacement alg
            else:
                # print("FIFO")
                # TODO page replacement algorithm
                if self.alg == "LRU":
                    self.LRUPageReplacement(memory, tlb, freeFrame)
                elif self.alg == "OPT":
                    self.OPTPageReplacment(memory, tlb, freeFrame)
                else:
                    # memory.printMemory()
                    self.FIFOPageReplacment(memory, tlb, freeFrame)

        # print("\n adding pageNum {} and free frame {}\n".format(pageNum, test))
        # Add new frame to the page table
        self.addToTable(freeFrame, pageNum)

        if tlb.isTLBFull():
            tlb.freeTLBFrame()

        tlb.addToTLB(pageNum, freeFrame)

    def getFrameFromTable(self, pageNum):
        return self.pageTable[pageNum]

    def LRUPageReplacement(self, memory, tlb, freeFrame):
        # memory.printCache()
        val = memory.leastRecentlyUsed()
        self.deleteFrame(val[1])
        tlb.deleteFrameFromTLB(val[1])

        memory.addFrame(val[0], freeFrame)

    def OPTPageReplacment(self, memory, tlb, freeFrame):
        idx, frame = self.optimalPop(memory)
        # delete frame frome pageTable
        self.deleteFrame(frame)
        tlb.deleteFrameFromTLB(frame)
        # Get the free memeory block
        # idx = memory.findFreeFrame()
        # add frame to memory
        memory.addFrame(idx, freeFrame)
        pass

    def optimalPop(self, memory):
        max = -1
        toPop = -1
        for i in range(memory.memorySize):
            if memory.getFrame(i) != 0:
                targetFrame = memory.getFrame(i)

                if self.frameInPageTable(targetFrame):
                    pageNumfound = i
                    if pageNumfound > max:
                        max = pageNumfound
                        toPop = pageNumfound
                else:
                    memory.deleteFrame(i)
                    return i, targetFrame

        frame = memory.getFrame(toPop)
        memory.deleteFrame(toPop)
        return toPop, frame

    def FIFOPageReplacment(self, memory, tlb, freeFrame):

        # Remove the first item of memory and shift everything over
        frame = memory.shiftMemory()
        # print("\n Frame to be deleted {}\n".format(self.parsMyFrame(frame)))
        # delete frame frome pageTable
        self.deleteFrame(frame)
        tlb.deleteFrameFromTLB(frame)
        # Get the free memeory block
        idx = memory.findFreeFrame()
        # add frame to memory
        memory.addFrame(idx, freeFrame)
