import sys
from LogicalAdd import LogicalAddress
from PhysicalAdd import PhysicalAddress
from PageTable import PageTable
from TLB import TLB
from PhysicalMemory import PhysicalMemory

def main():
    # Check for cmd line arguments and retrive needed params
    ref_seq, frame, pra = checkArgs()
    # if we have bad command line args print usage
    if frame == -1:
        return -1
    # Create a page table object
    pageTable = PageTable(frame, pra)
    # Create a memory object
    memory = PhysicalMemory(frame)
    # Create a TLB Object
    tlb = TLB()
    # start tranlating logical to Physical Addresses
    translate(ref_seq, pageTable, memory, tlb)
    ref_seq.close()
    return 0

def checkArgs():
    # Get the length of the cmd line argumnets
    argc = len(sys.argv)
    # Only passed a reference file
    if argc == 2:
        # opend the reference file
        ref_seq = open(sys.argv[1], 'r')
        # default frame 256
        frame = 256
        # default page replacement alg is FIFO
        pra = "FIFO"
    # Passes reference file and frame number
    elif argc == 3:
        # Open up reference file
        ref_seq = open(sys.argv[1], 'r')
        if (sys.argv[2].upper() == "FIFO" or sys.argv[2].upper() == "LRU"
        or sys.argv[2].upper() == "OPT"):
            # default page replacement alg
            pra = sys.argv[2].upper()
            frame = 256
        else:
            # get the number of frames desiered
            frame = int(sys.argv[2])
            pra = "FIFO"
    # Passed reference file, frame number, and page replacement alg
    elif argc == 4:
        # open file
        ref_seq = open(sys.argv[1], 'r')
        # get and convert frame number
        frame = int(sys.argv[2])
        # get page replacement alg
        pra = sys.argv[3].upper()
    # if else, there was an improper cmd line args
    else:
        # Print usage error
        print("usage: memSim <reference-sequence-file.txt> <FRAMES> <PRA>")
        # return all -1 because of error
        return -1, -1, -1

    if frame > 256 or frame < 0:
        print("Usage: Frame <= 256 and > 0")
        return -1, -1, -1
    # Return all args
    return ref_seq, frame, pra

def translate(ref_seq, pageTable, memory, tlb):
    TLBHit = False
    # Gets the total number of addresses read
    translatedAddr = 0
    # Gets the number of page faults occured
    numPageFaults = 0
    # gets the Number of TLB hits occrured
    numTLBHits = 0
    # Gets the number of TLB misses occured
    numTLBMiss = 0
    # get each address
    for address in ref_seq:
        # Create a logical page
        logicAdd = LogicalAddress(int(address))
        # function that extracts the page number from the address
        pageNum = logicAdd.getPageNum()
        # function that extracts the page offset from the address
        pageOff = logicAdd.getPageOffset()

        # f = tlb.getFromTLB(pageNum)
        # Check the TLB if pageNum is in the TLB Table
        if tlb.pageNumInTLB(pageNum):
            # Increment the number of TLB hits
            numTLBHits += 1
            f = tlb.getFromTLB(pageNum)
            # print("TLB HIt")
        # If page number not in TLB we have a TLB Miss.
        else:
            # print("TLBMISS")
            # Increment the number of TLB misses
            numTLBMiss += 1
            # if True, pageNum in Page tabel.
            if pageTable.isInPageTable(pageNum):
                # print("In pageTable")
                # print("pageNum: %d"%pageNum)
                # if pageNum == 178:
                #     pageTable.printTable()
                # Get frame from Table
                f = pageTable.getFrameFromTable(pageNum)
            # else we have a page fault
            else:
                # print("Page Fault")
                # increment the number of page faults
                numPageFaults += 1
                # Hnadle the page fault
                pageTable.pageFaultHandler(tlb, memory, pageNum, pageOff)
                # Get frame from Table
                f = pageTable.getFrameFromTable(pageNum)
                # if pageNum == 178:
                #     pageTable.printTable()

        # get page offset
        d = pageOff
        # Create a Physical address
        physAdd = PhysicalAddress(f,d)
        # Get byte reference based on the frame and page offset
        byteRef = physAdd.getByteReference()
        # get the index of the frame
        idx = memory.getIdx(f)
        # Increment the number of address that we read from file
        translatedAddr += 1
        # parse the Frame in order to print out the entire frame
        f = parsFrame(f)

        print("{}, {}, {}, {}".format(logicAdd.getAddress(), byteRef, idx, f))
    printStats(translatedAddr, numPageFaults, numTLBHits, numTLBMiss)

def printStats(translatedAddr, pagefaults, hit, miss):
    print("Number of Translated Addresses = %d" % translatedAddr)
    print("Page Faults = %d" % pagefaults)
    print("Page Fault Rate = %.3f" % (pagefaults/translatedAddr))
    print("TLB Hits = %d" % hit)
    print("TLB Misses = %d" % miss)
    print("TLB Hit Rate = %.3f" % (hit/translatedAddr))

def parsFrame(frame):
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


if __name__ == '__main__':
    main()
