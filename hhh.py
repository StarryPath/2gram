import binascii
import os
import pymysql

fileList = os.listdir("ben")
gram=3
i=1
hex_dict={}

for file in fileList:
    fh = open('ben/'+file, 'rb')
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
