import sys

class LogicalAddress:

      def __init__(self, addr):
          self.address = addr
          self.p = 0
          self.d = 0

      def getPageNum(self):
          return self.address >> 8

      def getPageOffset(self):
          mask = 0xFF
          return self.address & mask

      def getAddress(self):
          return self.address
