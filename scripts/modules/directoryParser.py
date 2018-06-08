# !/usr/bin/python
# -*- coding: UTF-8 -*-
import xml.etree.ElementTree as ET
import os
import re

#从directory下的manifest.xml中解析目录
#返回值：dir_table,代表路径表的字典，dir_table[版本号][名称] = 所在文件夹
def parseDirectory(directory):

    ptree = ET.parse(os.path.join(directory, "manifest.xml"))
    root = ptree.getroot()
    dir_table = {}

    #遍历每个版本
    for version in root:
        version_code = int(version.attrib.get("code"),16)
        vdir_table = {}
        #读取文件目录
        for name in version:
            vdir_table[name.tag] = os.path.join(directory, name.text)
        dir_table[version_code] = vdir_table
    return dir_table

#检查标准文件是否齐全
#参数1：dir_table，parseDirectory解析得到的路径表
def checkStandarsFile(dir_table):
    for version in dir_table:
        vdir_table = dir_table[version]
        if not os.path.exists(os.path.join(vdir_table["header"], "header.xml")):
            raise Exception("header.xml not found")
        if not os.path.exists(os.path.join(vdir_table["demographics"], "demographics.xml")):
            raise Exception("demographics.xml not found")
        if not os.path.exists(os.path.join(vdir_table["activities"], "activities.xml")):
            raise Exception("activities.xml not found")
        if not os.path.exists(os.path.join(vdir_table["contents"], "contents.xml")):
            raise Exception("contents.xml not found")
        if not os.path.exists(os.path.join(vdir_table["resources"], "resources.xml")):
            raise Exception("resources.xml not found")

#从标准中解析元数据。
#参数1：dir_table, 从parseDirectory得到的路径表, 这里需要对标准文件夹进行解析得到的标准路径表
#返回值：meta_table, 代表元数据的字典, meta_table[版本号][元数据名称] = 元数据代码
def parseMeta(dir_table):
    meta_table = {}
    #遍历每个版本
    for version in dir_table:
        vdir_table = dir_table[version]
        vdem= ET.parse(os.path.join(vdir_table["demographics"], "demographics.xml"))
        vact = ET.parse(os.path.join(vdir_table["activities"], "activities.xml"))
        vcon = ET.parse(os.path.join(vdir_table["contents"], "contents.xml"))
        vres = ET.parse(os.path.join(vdir_table["resources"], "resources.xml"))
        vstandards = [vdem, vact, vcon, vres]
        vmeta_table = {} #某个版本的元数据表
        for standard in vstandards:
            for meta in standard.getroot():
                vmeta_table[meta.tag] = int(meta.attrib.get("code"), 16)
        meta_table[version] = vmeta_table
    return meta_table

#提取符合标准的文件的
#参数1：dir_table, 从parseDirectory得到的路径表, 这里需要对数据文件夹进行解析得到的数据路径表
#参数2：meta_table, 从parseMeta得到的元数据表
#返回值：file_table,file_table[版本号][元数据名称] = 存储该元数据的文件list，list按文件分片号升序排序
def collectDataFile(dir_table, meta_table):
    file_table = {}
    #遍历版本
    for version in meta_table:
        vdir_table = dir_table[version]
        vmeta_table = meta_table[version]
        vfile_table = {}

        #初始化该版本的文件列表
        for meta in vmeta_table:
            vfile_table[meta] = [];

        #从每个数据类型的目录中列取文件
        for data_name in vdir_table:
            filelist = os.listdir(vdir_table[data_name])

            #元数据名匹配文件名
            for meta in vmeta_table:
                pattern = meta + "_\d+"
                for filename in filelist:
                    if re.match(pattern, filename):
                        vfile_table[meta].append(filename)
                #根据文件分片号排序
                vfile_table[meta].sort(key = lambda x:int(x.split("_")[-1]))

        file_table[version] = vfile_table

    return file_table
