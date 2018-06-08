# !/usr/bin/python
# -*- coding: UTF-8 -*-

#文件名:item.py
#描述：用于解析元数据项的模块，通过解析标准文件，控制一条数据的二进制格式
#功能：
#   1.解析标准，识别条件字段、变长字段
#   2.根据标准，读取数据并解析INT，FLOAT类型数据
#   3.根据标准，将数据打包成二进制格式并写入文件

import xml.etree.ElementTree as ET
import struct
import json
import os, sys
import random
class Item:
    #struct.pack所要求的格式字符
    intmap = {1:"B", 2:"H", 4:"L", 8:"Q"}
    floatmap = {4:"f", 8:"d"}

    #空值的掩码（最高位）
    noneMask = {1:0x80, 2:0x8000, 4:0x80000000, 8:0x8000000000000000}

    #标记条件字段和变长字段的标志位
    CONDITIONAL_PAYLOAD = 0x1
    VARIABLE_LENGTH_PAYLOAD = 0x2

    #根据标准初始化一项元数据项
    #参数：
    #   standard：标准文件路径
    #   name：元数据名
    def __init__(self, standard, name):
        tree = ET.parse(standard)
        self.name = name
        self.code = int(tree.getroot().find(name).attrib.get("code"), 16)
        self.fieldmap = {} #属性名 -> 位置
        self.fieldtype = []
        self.valtype = []
        self.fieldrange = []
        self.length = []
        self.flags = []
        self.cond = []
        self.values = []
        for i,field in enumerate(tree.getroot().find(name)):
            self.fieldmap[field.tag] = i
            self.fieldtype.append(field.find("type").text)
            self.valtype.append(field.find("valtype").text)
            self.flags.append(0)

            #从json中读取值域，
            if field.find("valmap") is not None:
                path, f= os.path.split(standard)
                json_name = field.find("valmap").text
                fp = open(os.path.join(path, json_name))
                self.fieldrange.append(json.load(fp))
                fp.close()
            else:
                self.fieldrange.append("FREE")

            #处理变长属性
            if self.__isDigit(field.find("length").text):
                self.length.append(int(field.find("length").text))
            else:
                self.flags[i] |= Item.VARIABLE_LENGTH_PAYLOAD
                self.length.append(field.find("length").text)

            #处理条件属性
            if field.attrib.get("cond"):
                self.flags[i] |= Item.CONDITIONAL_PAYLOAD
                self.cond.append(field.attrib.get("cond"))
            else:
                self.cond.append("NONE")

            self.values.append(None)

    #给项目赋值
    #参数values:值的数组
    def set(self, values):
        if len(values) != len(self.values):
            raise Exception("expect %s values, got %s"%(str(len(self.values)), str(len(values))))
        for i in range(0, len(values)):
            self.values[i] = values[i]

    #从打开的文件中读取一条记录,从当前文件指针位置开始读取
    #参数：
    #   f:打开的文件，打开方式为二进制读模式(rb)
    def read(self, f):
        self.__dropAllValues()
        #找到确定字段的个数(i)
        n = 0
        for i,flag in enumerate(self.flags):
            if flag & Item.CONDITIONAL_PAYLOAD != 0 or flag & Item.VARIABLE_LENGTH_PAYLOAD != 0:
                n = i
                break

        #读取定长字段
        for i,length in enumerate(self.length[:n]):
            unpackfmt = ">"
            if self.fieldtype[i] == "INT":
                unpackfmt += Item.intmap[length]
            elif self.fieldtype[i] == "FLOAT":
                unpackfmt += Item.floatmap[length]
            elif self.fieldtype[i] == "TEXT":
                unpackfmt = unpackfmt + str(length) + "s"
                
            value, = struct.unpack(unpackfmt, f.read(length))

            if value & Item.noneMask[length] != 0:
                value = None
            self.values[i] = value

        #读取变长字段和条件字段
        for i,length in enumerate(self.length[n:]):
            i += n #让i等于位置

            if self.flags[i] & Item.CONDITIONAL_PAYLOAD != 0 and not self.__judge(i):
                self.values[i] = None
                continue

            unpackfmt = ">"
            data = ""
            if self.fieldtype[i] == "INT":
                unpackfmt += Item.intmap[self.length[i]]
                data = f.read(length)
            elif self.fieldtype[i] == "FLOAT":
                unpackfmt += Item.floatmap[self.length[i]]
                data = f.read(length)
            elif self.fieldtype[i] == "TEXT":
                unpackfmt = unpackfmt + str(self.values[self.fieldmap[self.length[i]]]) + "s"
                data = f.read(self.values[self.fieldmap[self.length[i]]])

            self.values[i], = struct.unpack(unpackfmt, data)

    #向打开的文件中写入文件
    #参数f：打开的文件
    def write(self, f):
        length,data = self.pack()
        f.write(data)
        return length

    #打包成二进制数据
    def pack(self):
        data = ""
        total_length = 0
        for i,value in enumerate(self.values):
            #判断该值是否应该打包
            if self.flags[i] & Item.CONDITIONAL_PAYLOAD != 0:
                if not self.__judge(i):
                    continue

            #处理空值
            if value is None:
                value = Item.noneMask[self.length[i]]

            #根据值是否变长设置打包格式
            packfmt = ">"
            if self.flags[i] & Item.VARIABLE_LENGTH_PAYLOAD != 0:
                length = self.values[self.fieldmap[self.length[i]]]
                packfmt = packfmt + str(length) + 's'
                total_length += length
            else:
                packfmt += Item.intmap[self.length[i]]
                total_length += self.length[i]
            data += struct.pack(packfmt, value)

        return total_length, data

    def show(self):
        print "standard:", self.name
        print "meta code:", self.code
        print "fieldmap:", self.fieldmap
        print "fieldtype:", self.fieldtype
        print "valtype:", self.valtype
        print "fieldrange:", self.fieldrange
        print "length:", self.length
        print "flags:", self.flags
        print "cond:", self.cond
        print "values:", self.values

    #判断条件字段中的条件是否成立
    #参数：
    #   i: 字段位置
    def __judge(self, i):
        condstr = self.cond[i]
        #将表达式替换为可执行语句
        condstr = condstr.replace("||", "or")
        condstr = condstr.replace("&&", "and")
        for field in self.fieldmap:
            pos = self.fieldmap[field]
            condstr = condstr.replace(field, "self.values[%s]" % pos)
            if self.valtype[pos] == "SET":
                for key in self.fieldrange[pos]:
                    condstr = condstr.replace(key, str(self.fieldrange[pos][key]))

        return eval(condstr)

    def __isDigit(self, str):
        try:
            int(str)
        except:
            return False
        return True

    def __dropAllValues(self):
        for i in range(0, len(self.values)):
            self.values[i] = None

    def fillRandom(self):
        max_int_value = {1:0x7f, 2:0x7fff, 4:0x7fffffff, 8:0x7fffffffffffffff}
        max_variable_length = 1024
        self.__dropAllValues()

        #填写变长字段长度
        for i,length in enumerate(self.length):
            if not self.__isDigit(length):
                self.values[self.fieldmap[length]] = random.randint(0, max_variable_length)

        #填写其余字段
        for i,value in enumerate(self.values):
            if value is None: # 避免重写变长长度部分
                if self.fieldtype[i] == "INT":
                    self.values[i] = random.randint(0, max_int_value[self.length[i]])
                elif self.fieldtype[i] == "FLOAT":
                    self.values[i] = random.random() * 10000 + 10000
                elif self.fieldtype[i] == "TEXT":
                    self.values[i] = "c" * self.values[self.fieldmap[self.length[i]]]
