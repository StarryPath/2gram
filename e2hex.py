#!/usr/bin/env python
#encoding: utf-8
import binascii
import os
import pymysql

fileList = os.listdir("ben")
gram=2
ty=0 #0为正常文件,1为病毒
# 打开数据库连接
db = pymysql.connect("localhost", "root", "root", "bishe")
i=1
# 使用cursor()方法获取操作游标
cursor = db.cursor()
hex_dict={}
j=1
for file in fileList:
    #print(file)
    print(i)
    i+=1
    fh = open('ben/'+file, 'rb')
    a = fh.read()
    #print 'raw: ',`a`,type(a)
    hexstr = str(binascii.b2a_hex(a))[2:]
    print(len(hexstr))

    while len(hexstr)>=gram*2:

        if hexstr[0:gram*2] not in hex_dict:
            hex_dict[hexstr[0:gram*2]]=1
        else:
            hex_dict[hexstr[0:gram * 2]]+=1
        hexstr = hexstr[2:]
j=1
for key,value in hex_dict.items():
    #sql = "INSERT INTO gram2(hexstr, ben) VALUES ('%s','%d')" % (key, value)

    sql="update gram2 set ben='"+str(value)+"'where hexstr='"+key+"'"
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except Exception as c:
        # 如果发生错误则回滚
        print(c)
        try:
            sql="insert into gram2(hexstr, ben) VALUES ('%s','%d')" % (key, value)
            cursor.execute(sql)
            # 提交到数据库执行
            db.commit()
        except Exception as e:
            print(e)
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