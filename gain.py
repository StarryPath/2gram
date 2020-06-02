import pymysql
import numpy as np
db = pymysql.connect("localhost", "root", "root", "bishe")
cursor = db.cursor()
sum_ben=0
sum_ev=0
sql="select sum(ben) from gram2"
try:
    # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    db.commit()
    sum_ben = cursor.fetchone()[0]
    print(sum_ben)
except Exception as c:
    # 如果发生错误则回滚
    print(c)
    db.rollback()
sql="select sum(ev) from gram2"
try:
    # 执行sql语句
    cursor.execute(sql)
    # 提交到数据库执行
    db.commit()
    sum_ev = cursor.fetchone()[0]
    print(sum_ev)
except Exception as c:
    # 如果发生错误则回滚
    print(c)
    db.rollback()

sum=sum_ben+sum_ev
pben=sum_ben/sum
pev=sum_ev/sum
prob1=[pben,pev]
a = np.asarray(prob1, dtype =  float)
print(a)
#ent=sum(np.log2(a)*a*(-1))
#print(ent)
print(np.log2(a)*a*(-1))
g1=np.sum(np.log2(a)*a*(-1))#整体熵
sql="select hexstr,ben,ev,id from gram2"
cursor.execute(sql)
for hexs in cursor.fetchall():
    ben=hexs[1]
    ev=hexs[2]
    id=hexs[3]
    #print(ben,ev,id)
    sumbv=ben+ev
    sumother=sum-sumbv
    pb1=ben/sumbv
    pe1=ev/sumbv
    pro1 = np.asarray([pb1, pe1], dtype =  float)
    pb2=(sum_ben-ben)/sumother
    pe2=(sum_ev-ev)/sumother
    pro2 = np.asarray([pb2,pe2], dtype =  float)
    eg1=np.sum(np.log2(pro1)*pro1*(-1))
    eg2=np.sum(np.log2(pro2)*pro2*(-1))
    gain=g1-eg1*float(sumbv/sum)-eg2*float(sumother/sum)
    print(gain)
    gain=gain*100000

    sql="update gram2 set gain="+str(gain)+" where id="+str(id)
    try:
        # 执行sql语句
        print(sql)
        cursor.execute(sql)
        db.commit()
    except Exception as c:
        # 如果发生错误则回滚
        print(c)
        db.rollback()

