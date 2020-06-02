import pymysql
import binascii
import os
db = pymysql.connect("localhost", "root", "root", "bishe")
cursor = db.cursor()
sql="select hexstr,gain from gram2 order by gain desc limit 20"
cursor.execute(sql)
features=[]
dataset=[]
for hexs in cursor.fetchall():
    features.append(hexs[0])
print(features)
fileList = os.listdir("ben")
hex_dict={}
for file in fileList:
    #print(file)
    data=[]
    fh = open('ben/'+file, 'rb')
    a = fh.read()
    hexstr = str(binascii.b2a_hex(a))[2:]
    hexstr = hexstr.upper()
    for fe in features:
        if hexstr.find(fe)!=-1:
            data.append(1)
        else:
            data.append(0)

    data.append(0)
    print(data)
    dataset.append(data)
print(dataset)
fileList = os.listdir("ev")
for filename in fileList:
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
    data = []
    hexstr = hexstr.upper()
    for fe in features:
        if hexstr.find(fe)!=-1:
            data.append(1)
        else:
            data.append(0)
    data.append(1)
    print(data)
    dataset.append(data)

