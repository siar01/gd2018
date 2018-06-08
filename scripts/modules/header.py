# !/usr/bin/python
# -*- coding: UTF-8 -*-
# 文件名：header.py
# 描述：用于解析文件头的模块，文件头是一段定长的字节序列，具体每个字段的长度由header.xml指出
import xml.etree.ElementTree as ET
import struct

class Header:
    charmap = {1:"B", 2:"H", 4:"L", 8:"Q"}

    #根据给定的标准初始化header
    #参数：
    #   header_standard：文件头标准文件路径
    def __init__(self, header_standard):
        tree = ET.parse(header_standard)
        root = tree.getroot()
        self.standards = header_standard
        self.fieldmap = {} #字段名到位置的映射关系
        self.length = []
        self.values = []
        for i,child in enumerate(root):
            self.fieldmap[child.tag] = i
            self.length.append(int(child.attrib.get("length")))
            self.values.append(0)

    #向文件头赋值
    #参数：
    #   values:值的数组，values的长度必须与文件头中的定义一致
    def set(self, values):
        if len(values) != len(self.values):
            raise Exception("expect %s values, got %s"%(str(len(self.values)), str(len(values))))
        for i in range(0, len(values)):
            self.values[i] = values[i]

    #向文件头某一字段赋值
    #参数：
    #   name：字段名
    #   value:值
    def set_by_name(self, name, value):
        pos = self.fieldmap[name]
        self.values[pos] = value

    #获取某字段的值
    def get(self, name):
        return self.values[self.fieldmap[name]]

    #从打开的文件中读取文件头，会将文件指针置为0之后再读取
    #参数：
    #   f:通过open函数打开的文件指针，二进制读方式("rb")
    #返回值：读取的字节数
    def read(self, f):
        f.seek(0)
        for i,length in enumerate(self.length):
            unpack_str = ">" + Header.charmap[length] #字节序采用大端法
            data = f.read(length)
            self.values[i], = struct.unpack(unpack_str, data)
        return sum(self.length)

    #向打开的文件中写入文件头，会将文件指针置为0之后再写入
    #参数：
    #   f:通过open函数打开的文件指针，二进制写方式("wb")
    #返回值：写入的字节数
    def write(self, f):
        f.seek(0)
        length, data = self.pack()
        f.write(data)
        return length

    #将数值打包成二进制格式
    #返回值：（数据字节数，打包完成的数据）
    def pack(self):
        data = ""
        length = 0
        for i,value in enumerate(self.values):
            packstr = ">" + Header.charmap[self.length[i]]
            length += self.length[i]
            data += struct.pack(packstr, value)
        return length, data

    def show(self):
        print "standards:", self.standards
        print "fieldmap:", self.fieldmap
        print "length:", self.length
        print "values:", self.values
