import os
import pymysql
fileList = os.listdir("ev")
db = pymysql.connect("localhost", "root", "root", "bishe")
cursor = db.cursor()
gram=2
ty=1
hex_dict={}
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
        #print(b_list)
    #print(len(ans))
    #print(len(ans))
    while len(hexstr) >= gram * 2:

        if hexstr[0:gram * 2] not in hex_dict:
            hex_dict[hexstr[0:gram * 2]] = 1
        else:
            hex_dict[hexstr[0:gram * 2]] += 1
        hexstr = hexstr[2:]
for key, value in hex_dict.items():
    sql = "INSERT INTO gram2(hexstr, ev) VALUES ('%s','%d')" % (key, value)
    try:
        # 执行sql语句
        cursor.execute(sql)
        # 提交到数据库执行
        db.commit()
    except Exception as c:
        # 如果发生错误则回滚
        print(c)
        db.rollback()
