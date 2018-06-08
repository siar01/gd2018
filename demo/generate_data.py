# !/usr/bin/python
# -*- coding: UTF-8 -*-
import os, sys
sys.path.append("/home/siar/gd2018/scripts/modules")
import header
import item
from directoryParser import *
import random
import binascii

standard_dir_table = parseDirectory("/home/siar/gd2018")
checkStandarsFile(standard_dir_table)
meta_table = parseMeta(standard_dir_table)

data_dir_table = parseDirectory("/home/siar/testdata")
file_table = collectDataFile(data_dir_table, meta_table)

meta_name = {0x0:"demographics", 0x1:"activities", 0x2:"contents", 0x3:"resources"}



max_length = 1 * 2 ** 20 # 1MB
for version in meta_table:
    file_header = header.Header(os.path.join(standard_dir_table[version]["header"], "header.xml"))
    vmeta_table = meta_table[version]
    for meta in vmeta_table:
        code = vmeta_table[meta]
        class_name = meta_name[vmeta_table[meta] >> 8]
        class_file = os.path.join(standard_dir_table[version][class_name], class_name+".xml")
        data_path = data_dir_table[version][class_name]
        body_entry = item.Item(class_file, meta)

        for i in range(0,5):
            filename = meta + "_" + str(i)
            fp = open(os.path.join(data_path, filename), "wb")
            entry = item.Item(class_file, meta)
            isSlice = 0x1 if i != 4 else 0x0
            file_header.write(fp)
            body_length = 0
            total_entry = 0
            body = ""
            while(body_length < max_length):
                entry.fillRandom()
                body_length += entry.write(fp)
                total_entry += 1
                l,data = entry.pack()
                body += data

            #模拟文件头填错的情况
            bad_version = version
            bad_code = code
            bad_body_length = body_length
            bad_total_entry = total_entry
            bad_flags = isSlice

            # 20% become bad
            if random.random() < 0.2:
                op  = random.randint(0, 4)
                if op == 0:
                    bad_version = random.randint(0,0x7f)
                elif op == 1:
                    bad_code = random.randint(0,0x7fff)
                elif op == 2:
                    bad_body_length = random.randint(0,0x7fffffff)
                elif op == 3:
                    bad_total_entry = random.randint(0,0x7fffffff)
                elif op == 4:
                    bad_flags = random.randint(0,0x7fff)

            file_header.set([bad_version,bad_code,bad_body_length,bad_total_entry,bad_flags,0])
            l,head = file_header.pack()
            crc = binascii.crc32(head + body) & 0xffffffff
            file_header.set_by_name("crc32", crc)
            file_header.write(fp)


            #模拟文件损坏的情况
            if random.random() < 0.05:
                fp.seek(random.randint(0, fp.tell()))
                fp.write("c" * random.randint(0,100))

            fp.close()
