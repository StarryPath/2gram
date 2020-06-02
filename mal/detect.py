import json
import os
import pickle
import time

import binascii
import sys
sys.setrecursionlimit(1000000)
list_file = open('labels.pickle','rb')
labels = pickle.load(list_file)
print(labels)
list2_file = open('id3.pickle', 'rb')
id3tree = pickle.load(list2_file)
print(id3tree)
list3_file = open('c45.pickle', 'rb')
list3 = pickle.load(list3_file)
print(list3)


def classfiy(myTree, labels, test):
    global classlabel
    firstStr = list(myTree.keys())[0]  # 需要获取首个特征的列号，以便从测试数据中取值比较
    secondDict = myTree[firstStr]  # 获得第二个字典
    featIndex = labels.index(firstStr)  # 获取测试集对应特征数值
    for key in secondDict.keys():
        if (test[featIndex] == key):
            if (type(secondDict[key]).__name__ == 'dict'):  # 判断该值是否还是字典，如果是，则继续递归
                classlabel = classfiy(secondDict[key], labels, test)
            else:
                classlabel = secondDict[key]
    return classlabel
def testTree(myTree):
    sum=0
    ans=0
    fileList = os.listdir("testben")
    for file in fileList:
        fh = open('testben/' + file, 'rb')
        a = fh.read()
        hexstr = str(binascii.b2a_hex(a))[2:]
        hexstr = hexstr.upper()
        pos = hexstr.find("5045")  # PE
        hexstr = hexstr[pos:]
        # 去掉PE头
        # print(hexstr[40:42])
        if hexstr[40:42] == "E0":
            hexstr = hexstr[496:]
        elif hexstr[40:42] == "F0":
            hexstr = hexstr[528:]
        else:
            continue
        data = []
        for lab in labels:
            if hexstr.find(lab) != -1:
                data.append(1)
            else:
                data.append(0)
        result = classfiy(myTree, labels, data)  # 预测测试数据
        ans += 1
        if result == 0:
            sum += 1
    sum2 = 0
    fileList = os.listdir("testbingdu")
    for filename in fileList:
        file = open(r'testbingdu/' + filename)
        hexstr = ""
        while True:
            byt = file.readline()  # 只读取一行内容

            if not byt:
                break
            # ip = ip.strip('\n')
            b_list = byt.split()
            del b_list[0]
            for b_str in b_list:
                hexstr += b_str
        data = []
        hexstr = hexstr.upper()
        for lab in labels:
            if hexstr.find(lab) != -1:
                data.append(1)
            else:
                data.append(0)
        result = classfiy(myTree, labels, data)  # 预测测试数据
        if result == 1:
            sum2 += 1
    ans+=len(fileList)
    return (sum+sum2)/ans
r1=testTree(id3tree)
r2 = testTree(list3)
print("ID3:",r1)
print("C45:",r2)
