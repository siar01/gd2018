# !/usr/bin/python
# -*- coding: UTF-8 -*-
import xml.etree.ElementTree as ET
tree = ET.parse("/home/siar/gd2018/standards/activities/activities.xml")
root = tree.getroot()

import struct
struct.pack('Q',5)
WriteFileData = open("file.dat",'wb')
WriteFileData.write(struct.pack('Q',123456789))
WriteFileData.close()

readfile = open('file.dat','rb')
a,= struct.unpack("Q",readfile.read(8))
print a


# print not root.find("video_act").find("record_type").find("1231")
# from Tkinter import *           # 导入 Tkinter 库
# root = Tk()                     # 创建窗口对象的背景色
#                                 # 创建两个列表
# li     = ['C','python','php','html','SQL','java']
# movie  = ['CSS','jQuery','Bootstrap']
# listb  = Listbox(root)          #  创建两个列表组件
# listb2 = Listbox(root)
# for item in li:                 # 第一个小部件插入数据
#     listb.insert(0,item)
#
# for item in movie:              # 第二个小部件插入数据
#     listb2.insert(0,item)
#
# listb.pack()                    # 将小部件放置到主窗口中
# listb2.pack()
# root.mainloop()                 # 进入消息循环

item=["校验和","数据结构","值域","引用完整性","","","","","",""]
