from math import log
import operator
import pymysql
import binascii
import os
import sys
import json
import pickle
id3tree={}
id3cnt=0
def calcShannonEnt(dataSet):  # 计算数据的熵(entropy)
    numEntries=len(dataSet)  # 数据条数
    labelCounts={}
    for featVec in dataSet:
        currentLabel=featVec[-1] # 每行数据的最后一个字（类别）
        if currentLabel not in labelCounts.keys():
            labelCounts[currentLabel]=0
        labelCounts[currentLabel]+=1  # 统计有多少个类以及每个类的数量
    shannonEnt=0
    for key in labelCounts:
        prob=float(labelCounts[key])/numEntries # 计算单个类的熵值
        shannonEnt-=prob*log(prob,2) # 累加每个类的熵值
    return shannonEnt

def createDataSet1():    # 创造示例数据
    db = pymysql.connect("localhost", "root", "root", "bishe")
    cursor = db.cursor()
    sql = "select hexstr,gain from gram2 order by gain desc limit 1000"
    cursor.execute(sql)
    features = []
    dataset = []
    for hexs in cursor.fetchall():
        features.append(hexs[0])
    #print(features)
    fileList = os.listdir("ben")
    for file in fileList:
        # print(file)
        data = []
        fh = open('ben/' + file, 'rb')
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
        for fe in features:
            if hexstr.find(fe) != -1:
                data.append(1)
            else:
                data.append(0)
        data.append(0)
        dataset.append(data)
    fileList = os.listdir("ev")
    for filename in fileList:
        file = open(r'ev/' + filename)
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
        for fe in features:
            if hexstr.find(fe) != -1:
                data.append(1)
            else:
                data.append(0)
        data.append(1)
        dataset.append(data)
    '''
    dataSet = [['长', '粗', '男'],
               ['短', '粗', '男'],
               ['短', '粗', '男'],
               ['长', '细', '女'],
               ['短', '细', '女'],
               ['短', '粗', '女'],
               ['长', '粗', '女'],
               ['长', '粗', '女']]
    labels = ['头发','声音']  #两个特征
    '''
    return dataset,features

def splitDataSet(dataSet,axis,value): # 按某个特征分类后的数据
    retDataSet=[]
    for featVec in dataSet:
        if featVec[axis]==value:
            reducedFeatVec =featVec[:axis]
            reducedFeatVec.extend(featVec[axis+1:])
            retDataSet.append(reducedFeatVec)
    return retDataSet

def chooseBestFeatureToSplit(dataSet):  # 选择最优的分类特征
    numFeatures = len(dataSet[0])-1
    baseEntropy = calcShannonEnt(dataSet)  # 原始的熵
    bestInfoGain = 0
    bestFeature = -1
    for i in range(numFeatures):
        featList = [example[i] for example in dataSet]
        uniqueVals = set(featList)
        #print(uniqueVals)
        newEntropy = 0
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet,i,value)
            prob =len(subDataSet)/float(len(dataSet))
            newEntropy +=prob*calcShannonEnt(subDataSet)  # 按特征分类后的熵
        infoGain = baseEntropy - newEntropy  # 原始熵与按特征分类后的熵的差值
        if (infoGain>bestInfoGain):   # 若按某特征划分后，熵值减少的最大，则次特征为最优分类特征
            bestInfoGain=infoGain
            bestFeature = i
    return bestFeature
def c45(dataSet):
    numFeatures = len(dataSet[0]) - 1
    baseEntropy = calcShannonEnt(dataSet)  # 原始的熵
    bestInfoGain = 0
    bestFeature = 0
    for i in range(numFeatures):
        featList = [example[i] for example in dataSet]
        uniqueVals = set(featList)
        # print(uniqueVals)
        newEntropy = 0
        IV=0
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet) / float(len(dataSet))
            newEntropy += prob * calcShannonEnt(subDataSet)  # 按特征分类后的熵
            IV-=prob*log(prob,2)
        infoGain = baseEntropy - newEntropy  # 原始熵与按特征分类后的熵的差值
        if IV==0:
            continue
        Gain_ratio=infoGain/IV
        #print(Gain_ratio)
        if (Gain_ratio > bestInfoGain):  # 若按某特征划分后，熵值减少的最大，则次特征为最优分类特征
            bestInfoGain = Gain_ratio
            bestFeature = i
    return bestFeature
def majorityCnt(classList):    #按分类后类别数量排序，比如：最后分类为2男1女，则判定为男；
    classCount={}
    for vote in classList:
        if vote not in classCount.keys():
            classCount[vote]=0
        classCount[vote]+=1
    sortedClassCount = sorted(classCount.items(),key=operator.itemgetter(1),reverse=True)
    return sortedClassCount[0][0]

def createTreeID3(dataSet,labels):
    classList=[example[-1] for example in dataSet]  # 类别：男或女
    if classList.count(classList[0])==len(classList):
        return classList[0]
    if len(dataSet[0])==1:
        return majorityCnt(classList)
    bestFeat=chooseBestFeatureToSplit(dataSet) #选择最优特征
    #bestFeat = c45(dataSet)
    bestFeatLabel=labels[bestFeat]
    myTree={bestFeatLabel:{}} #分类结果以字典形式保存

    del(labels[bestFeat])
    featValues=[example[bestFeat] for example in dataSet]
    uniqueVals=set(featValues)
    for value in uniqueVals:
        subLabels=labels[:]
        myTree[bestFeatLabel][value]=createTreeID3(splitDataSet\
                            (dataSet,bestFeat,value),subLabels)
    return myTree

def createTreeC45(dataSet,labels):
    classList=[example[-1] for example in dataSet]  # 类别：男或女
    if classList.count(classList[0])==len(classList):
        return classList[0]
    if len(dataSet[0])==1:
        return majorityCnt(classList)
    #bestFeat=chooseBestFeatureToSplit(dataSet) #选择最优特征
    bestFeat = c45(dataSet)
    bestFeatLabel=labels[bestFeat]
    myTree={bestFeatLabel:{}} #分类结果以字典形式保存
    del(labels[bestFeat])
    featValues=[example[bestFeat] for example in dataSet]
    uniqueVals=set(featValues)
    for value in uniqueVals:
        subLabels=labels[:]
        myTree[bestFeatLabel][value]=createTreeC45(splitDataSet\
                            (dataSet,bestFeat,value),subLabels)
    return myTree
# 分类器预测  （嵌套字典 列表特征名 列表测试数据）
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
def c_json(myTree):
    tree_dict={}
    firstStr = list(myTree.keys())[0]
    tree_dict["name"]=firstStr
    secondDict = myTree[firstStr]
    for key in secondDict.keys():
        if (type(secondDict[key]).__name__ == 'dict'):
            tree_dict["children"]=c_json(secondDict[key])
        else:
            tree_dict["children"]=secondDict[key]
    return tree_dict
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
if __name__=='__main__':
    sys.setrecursionlimit(1000000)
    dataSet, labels=createDataSet1()  # 创造示列数据
    print(labels)
    list_file = open('labels.pickle', 'wb')
    pickle.dump(labels, list_file)
    list_file.close()
    templabels1=labels[:]
    templabels2 = labels[:]
    tree1=createTreeID3(dataSet, templabels1)  # 输出决策树模型结果
    tree2=createTreeC45(dataSet, templabels2)
    list2_file = open('id3.pickle', 'wb')
    pickle.dump(tree1, list2_file)
    list2_file.close()
    list3_file = open('c45.pickle', 'wb')
    pickle.dump(tree2, list3_file)
    list3_file.close()

    print(tree1)
    json_str = json.dumps(tree1, indent=4)
    with open('/home/fy/xcbs/mal/static/id3_tree.json', 'w') as json_file:
        json_file.write(json_str)
    print(tree2)
    json_str = json.dumps(tree2, indent=4)
    with open('/home/fy/xcbs/mal/static/c45_tree.json', 'w') as json_file:
        json_file.write(json_str)
    r1=testTree(tree1)
    r2 = testTree(tree2)
    print("ID3:",r1)
    print("C45:",r2)
