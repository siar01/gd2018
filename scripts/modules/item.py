# !/usr/bin/python
# -*- coding: UTF-8 -*-
import xml.etree.ElementTree as ET
import struct
class Item:
    charmap = {1:"B", 2:"H", 4:"L", 8:"Q", -1:"s"} #-1代表可变长项
    VALUE_INVALID = 0x1
    CONDITIONAL_PAYLOAD = 0x2
    VARIABLE_LENGTH_PAYLOAD = 0x4
    def __init__(self, standard, name):
        tree = ET.parse(standard)
        self.name = name
        self.code = int(tree.getroot().find(name).attrib.get("code"), 16)
        self.fieldmap = {} #属性 -> 位置
        self.fieldtype = []
        self.length = []
        self.flags = []
        self.cond = []
        self.values = []
        self.fmt = ">"
        for i,field in enumerate(tree.getroot().find(name)):
            self.fieldmap[field.tag] = i
            self.fieldtype.append(field.find("type").text)
            self.flags.append(0x1)
            
            if self.__isDigit(field.find("length").text):
                self.length.append(int(field.find("length").text))
            else:
                self.flags[i] |= Item.VARIABLE_LENGTH_PAYLOAD
                self.length.append(field.find("length").text)

            if field.attrib.get("cond"):
                self.flags[i] |= Item.CONDITIONAL_PAYLOAD
                self.cond.append(field.attrib.get("cond"))
            else:
                self.cond.append("NONE")

            self.values.append(0)

    def tell(self):
        print self.name
        print self.code
        print self.fieldmap
        print self.fieldtype
        print self.length
        print self.flags
        print self.cond
        print self.values
        print self.fmt

    #检查flags，计算项中的定长部分
    def readFixedLength(self, ):


    def read(self, f):
        pass

    def write(self, f):
        pass

    def __isDigit(self, str):
        try:
            int(str)
        except:
            return False
        return True
