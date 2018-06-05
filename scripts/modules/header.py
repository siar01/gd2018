# !/usr/bin/python
# -*- coding: UTF-8 -*-
import xml.etree.ElementTree as ET
import struct

class Header:
    charmap = {1:"B", 2:"H", 4:"L", 8:"Q"}
    def __init__(self, header_standard):
        tree = ET.parse(header_standard)
        root = tree.getroot()
        self.standards = header_standard
        self.argmap = {}
        self.length = []
        self.values = []
        self.fmt = ">"
        for i,child in enumerate(root):
            self.argmap[child.tag] = i
            self.length.append(int(child.attrib.get("length")))
            self.fmt += Header.charmap[self.length[i]]

    def set(self, values):
        self.values = values

    #从打开的文件中读取文件头
    def read(self, f):
        length = sum(self.length)
        f.seek(0)
        self.values = struct.unpack(self.fmt,f.read(length))
        return length

    #向打开的文件中写入文件头
    def write(self, f):
        f.seek(0)
        f.write(struct.pack(self.fmt,self.values))
        return sum(self.length);

    def tell(self):
        print "standards:", self.standards
        print "argmap:", self.argmap
        print "length:", self.length
        print "values:", self.values
        print "fmt:", self.fmt
