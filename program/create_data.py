import struct
import sys
class ActivitiesHeader:
    def __init__(self,l,c,n):
        self.length = l
        self.checksum = c
        self.data_num = n

    def writeFile(self):
        data = struct.pack(">QQQ", self.length, self.checksum, self.data_num)
        f=open("file.dat","wb")
        f.write(data)
        f.close()

header = ActivitiesHeader(349012312412,2200123219490249598,5800000)
header.writeFile();

print sys.byteorder
