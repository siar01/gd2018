# !/usr/bin/python
# -*- coding: UTF-8 -*-
import xml.etree.ElementTree as ET
import os, sys
import re

class Error:
    CRC_FAILED = 0
    ENTRY_MISMATCH = 1
    UNEXPECTED_SLICE_ENDING = 2

    def __init__(self, errortype, filename):
        self.type = errortype
        self.filename = filename

    def what(self):
        if self.type == Error.CRC_FAILED:
            print "crc check faild in " + self.filename
        elif self.type == Error.ENTRY_MISMATCH:
            print "total entry detected doesn't math header in " + self.filename
        elif self.type == Error.UNEXPECTED_SLICE_ENDING:
            print "expect more slice after " + self.filename

#从directory 中的 manifest.xml中读取文件目录
def parseDirectory(directory):
    #解析manifest.xml
    ptree = ET.parse(directory + "/manifest.xml")
    root = ptree.getroot()
    dir = {}

    #遍历每个版本
    for version in root:
        version_code = int(version.attrib.get("code"),16)
        vdir = {}
        #读取文件目录
        for d in version:
            vdir[d.tag] = directory + "/" +d.text
        dir[version_code] = vdir
    return dir

#检查标准文件是否齐全
def checkStandarsFile(directory):
    for version in directory:
        d = directory[version]
        if not os.path.exists(d["header"] + "/header.xml"):
            raise Exception("header.xml not found")
        if not os.path.exists(d["demographics"] + "/demographics.xml"):
            raise Exception("demographics.xml not found")
        if not os.path.exists(d["activities"] + "/activities.xml"):
            raise Exception("activities.xml not found")
        if not os.path.exists(d["contents"] + "/contents.xml"):
            raise Exception("contents.xml not found")
        if not os.path.exists(d["resources"] + "/resources.xml"):
            raise Exception("resources.xml not found")

#从标准中解析元数据，一并解析编码。
def parseStandards(directory):
    meta_table = {}
    #遍历每个版本
    for version in directory:
        vd = directory[version]
        vdem_tree = ET.parse(vd["demographics"] + "/demographics.xml")
        vact_tree = ET.parse(vd["activities"] + "/activities.xml")
        vcon_tree = ET.parse(vd["contents"] + "/contents.xml")
        vres_tree = ET.parse(vd["resources"] + "/resources.xml")

        vtrees = [vdem_tree, vact_tree, vcon_tree, vres_tree]
        vmeta_table = {} #某个版本的元数据表
        for tree in vtrees:
            for elem in tree.getroot():
                vmeta_table[elem.tag] = int(elem.attrib.get("code"), 16)
        meta_table[version] = vmeta_table
    return meta_table

#检查数据中有多少文件
def checkDataFile(directory, meta_table):
    file_table = {}
    #遍历版本
    for version in meta_table:
        vd = directory[version]
        vmeta_table = meta_table[version]
        vfile_table = {}

        #从每个数据类型的目录中列取文件
        for dir in vd:
            filelist = os.listdir(vd[dir])

            #初始化该版本的文件列表
            for elem in vmeta_table:
                vfile_table[elem] = [];

            #元数据名匹配文件名
            for elem in vmeta_table:
                fname = elem + "_\d+"
                for filename in filelist:
                    if re.match(fname, filename):
                        vfile_table[elem].append(filename)
                #根据文件分片号排序
                vfile_table[elem].sort(key = lambda x:int(x.split("_")[-1]))

        file_table[version] = vfile_table



def main():
    if len(sys.argv) != 2:
        print "usage: main.py <data_directory>"
        return

    standards_dir = parseDirectory(".")
    checkStandarsFile(standards_dir)
    for v in standards_dir:
        sys.path.append(standards_dir[v]["modules"])
    meta_table = parseStandards(standards_dir)

    data_dir = parseDirectory(sys.argv[1])
    file_table = checkDataFile(data_dir, meta_table)

    # import header
    # file_header = header.Header(standards_dir[0]["header"] + "/header.xml")
    # file_header.set([0,0,0,0,0,0])
    # file_header.tell()

    from item import Item
    file_item = Item(standards_dir[0]["activities"] + "/activities.xml", "video_act")
    file_item.tell()



if __name__ == "__main__":
    main()
