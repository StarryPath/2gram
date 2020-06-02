#!/usr/bin/env python
#encoding: utf-8
import binascii
import os
import pymysql

fileList = os.listdir("ben")
gram=2
i=1
hex_dict={}

for file in fileList:
    fh = open('ben/'+file, 'rb')
    print(file)
    a = fh.read()
    hexstr = str(binascii.b2a_hex(a))[2:]
    hexstr=hexstr.upper()
    pos=hexstr.find("5045")#PE
    hexstr=hexstr[pos:]
    #去掉PE头
    #print(hexstr[40:42])
    if hexstr[40:42]=="E0":
        i += 1
        hexstr=hexstr[496:]
    elif hexstr[40:42]=="F0":
        i += 1
        hexstr=hexstr[528:]
    else :
        print(file)
    print(i)
    hexstr=hexstr.upper()
    while len(hexstr)>=gram*2:
        if hexstr[0:gram*2] not in hex_dict:
            hex_dict[hexstr[0:gram*2]]=[1,0]
        else:
            hex_dict[hexstr[0:gram * 2]][0]+=1
        hexstr = hexstr[2:]
fileList = os.listdir("ev")
i=1
for filename in fileList:
    print(i)

    i+=1
    file = open(r'ev/'+filename)
    hexstr=""
    while True:
        byt = file.readline()  # 只读取一行内容

        if not byt:
            break
        #ip = ip.strip('\n')
        b_list=byt.split()
        del b_list[0]
        for b_str in b_list:
            hexstr+=b_str
    print(len(hexstr))
    hexstr = hexstr.upper()
        #print(b_list)
    #print(len(ans))
    #print(len(ans))
    while len(hexstr) >= gram * 2:

        if hexstr[0:gram * 2] not in hex_dict:
            hex_dict[hexstr[0:gram * 2]] = [0,1]
        else:
            hex_dict[hexstr[0:gram * 2]][1] += 1
        hexstr = hexstr[2:]
# 打开数据库连接
db = pymysql.connect("localhost", "root", "root", "bishe")
# 使用cursor()方法获取操作游标
cursor = db.cursor()
for key,value in hex_dict.items():
    sql = "INSERT INTO gram2(hexstr, ben,ev) VALUES ('%s','%d','%d')" % (key, value[0],value[1])
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except Exception as c:
        # 如果发生错误则回滚
        print(c)

        db.rollback()

'''
sql = "INSERT INTO gram2(hexstr, ty) VALUES ('%s','%d')" % (hexstr[0:gram*2],ty)

try:
    # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    db.commit()
except Exception as c:
    # 如果发生错误则回滚
    print(c)
    db.rollback()
hexstr=hexstr[2:]
'''