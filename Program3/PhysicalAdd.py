import sys

class PhysicalAddress:

      def __init__(self, f, d):
          self.frame = f
          self.pageOff = d

      def getByteReference(self):
          address = self.frame[self.pageOff]
          if address > 127:
              address -= 256
          # val = int.from_bytes(val, 'big')
          return address


      # def getPageOffset(self):
      #     pass
