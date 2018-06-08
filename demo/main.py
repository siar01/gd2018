# !/usr/bin/python
# -*- coding: UTF-8 -*-
#检查数据中存在的下列错误：
#1.header读取错误
#2.文件版本号与指明的版本号不符
#3.文件头记录类型与文件名不一致
#4.校验错误
#5.分片错误
#6.数据项读取错误（文件头数据项数量填错或者数据填充不符合标准导致）
from __future__ import print_function
import sys
sys.path.append("/home/siar/gd2018/scripts/modules")
from directoryParser import *

import header
import item
import binascii

standard_dir_table = parseDirectory("/home/siar/gd2018")
checkStandarsFile(standard_dir_table)
meta_table = parseMeta(standard_dir_table)

data_dir_table = parseDirectory("/home/siar/testdata")
file_table = collectDataFile(data_dir_table, meta_table)

meta_name = {0x0:"demographics", 0x1:"activities", 0x2:"contents", 0x3:"resources"}

for version in meta_table:
    file_header = header.Header(os.path.join(standard_dir_table[version]["header"], "header.xml"))
    vmeta_table = meta_table[version]
    for meta in vmeta_table:
        code = vmeta_table[meta]
        class_name = meta_name[vmeta_table[meta] >> 8] #根据元数据代码的高8位确定所在分类
        class_file = os.path.join(standard_dir_table[version][class_name], class_name+".xml")
        data_path = data_dir_table[version][class_name]
        body_entry = item.Item(class_file, meta)

        for i,filename in enumerate(file_table[version][meta]):
            filepath = os.path.join(data_dir_table[version][class_name], filename)
            fp = open(filepath, "rb")
            logstr = "verifieing file " + filepath + " ... "
            print (logstr, end='')
            sys.stdout.flush()

            #读取文件头，读取前会将文件指针指向文件开头
            try:
                file_header.read(fp)
            except Exception:
                print ("failed to read header")
                continue

            #检测校验码是否正确
            crc32 = file_header.get("crc32") & 0xffffffff
            body = fp.read()
            file_header.set_by_name("crc32", 0)
            l,head = file_header.pack()
            if binascii.crc32(head + body) & 0xffffffff != crc32:
                print ("crc32 checksum failed!")
                continue

            #检测标准版本是否一致
            if file_header.get("version") != version:
                print ("standard version mismatch!")
                continue

            #检测文件记录类型是否一致
            if file_header.get("datatype") != code:
                print ("datatype mismatch!")
                continue

            #检测文件长度是否一致
            if fp.tell() - sum(file_header.length) != file_header.get("body_length"):
                print ("file length mismatch!")
                continue

            #检测分片
            if file_header.get("flags") & 0x1 != 0:
                filelist = file_table[version][meta]
                if i < len(filelist) - 1:
                    if int(filelist[i + 1].split("_")[-1]) != int(filename.split("_")[-1]) + 1:
                        logstr += filelist[i + 1] + "is not the expected file, some file may be missing!"
                        print (logstr)
                        continue
                else:
                    print ("last file with slice flag setted")
                    continue

            #尝试读取数据
            file_header.read(fp)
            total_entry = file_header.get("total_entry")
            n = 0
            while(n < total_entry):# 此处不能使用for in range，因为total_entry如果错误地填写成很大的数,range将会耗尽内存
                n += 1
                try:
                    body_entry.read(fp)
                except Exception:
                    print ("Bad data!(some entry malformed or total_entry is wrong)")
                    break

            if n == total_entry:
                print ("OK!")

            fp.close()
