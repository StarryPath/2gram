from math import log
import pandas as pd
import numpy as np
from math import log
import operator
import pymysql
import binascii
import os

# 数据集种类越多越复杂熵越大

# 创建数据集 （返回DataFrame）
def createdata():
    db = pymysql.connect("localhost", "root", "root", "bishe")
    cursor = db.cursor()
    sql = "select hexstr,gain from gram2 order by gain desc limit 20"
    cursor.execute(sql)
    features = []
    dataset={}
    for hexs in cursor.fetchall():
        features.append(hexs[0])
        dataset[hexs[0]]=[]
    dataset['type']=[]
    fileList = os.listdir("ben")

    for file in fileList:
        fh = open('ben/' + file, 'rb')
        a = fh.read()
        hexstr = str(binascii.b2a_hex(a))[2:]
        hexstr = hexstr.upper()
        for fe in features:
            if hexstr.find(fe) != -1:
                dataset[fe].append(1)
            else:
                dataset[fe].append(0)

        dataset['type'].append(0)
    #print(dataset)
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
                dataset[fe].append(1)
            else:
                dataset[fe].append(0)

        dataset['type'].append(1)
    data=pd.DataFrame(dataset)
    print(data)
   # data = pd.DataFrame(
     #   {'water': [1, 1, 1, 0, 0], 'feet': [1, 1, 0, 1, 1], 'survive': ['yes', 'yes', 'no', 'no', 'no']})
    return data


# 计算香农熵  （DataFrame）
def calculateshang(data):
    names = data[data.columns[-1]]  # 依据公式求某列特征的熵 目标变量作为概率依据
    n = len(names)
    labels = {}
    for i, j in names.value_counts().items():
        labels[i] = j
    shang = 0
    for i in labels:  # 利用循环求熵
        pi = labels[i] / n
        shang -= pi * log(pi, 2)
    return shang


# 划分数据集  （DataFrame,特征列名,该列某个特征值）
def splitdataSet(data, feature, feature_value):
    recvdata = []
    n = len(data)
    for i in range(n):  # 如果该行的这个特征值==循环到的这个特征值，去掉该特征加入返回列表
        if (data.iloc[[i], :][feature].values[0] == feature_value):
            temp = data.iloc[[i], :]  # 问题一：DataFrame如何取一行为Series，就可以直接drop了
            k = temp.index.values[0]
            temp_t = temp.loc[k]  # 问题二：DataFrame为什么这里使用iloc或loc不行，明明我是按照位置取值的而非行号
            tem = temp_t.drop(feature)
            recvdata.append(tem)
    recvDF = pd.DataFrame(recvdata)  # 将满足条件的所有行定义为DataFrame
    return recvDF


# 得出最好的特征名，用来划分数据集 （DataFrame）
def choosebestfeaturetosplit(data):
    nameFeatures = data.columns
    baseEntropy = calculateshang(data)  # 基础最大原始香农熵
    bestinfoGain = 0.0  # 初始化最好信息增益
    bestFeature = -1  # 初始化最好的特征名
    for Feature in nameFeatures[:-1]:  # 循环所有特征
        uniquevalue = set(data[Feature])  # 该特征的所有唯一值
        newEntropy = 0.0  # 中间熵
        for value in uniquevalue:
            subdata = splitdataSet(data, Feature, value)
            pi = len(subdata) / len(data)
            newEntropy += pi * calculateshang(subdata)
        infoGain = baseEntropy - newEntropy  # 中间信息增益
        if (infoGain > bestinfoGain):
            bestinfoGain = infoGain
            bestFeature = Feature  # 循环比较所有特征，返回信息增益最大的特征列名
    return bestFeature


# 若创建数结束后目标变量仍不唯一，则以最多的一类为准  (Series)
def major_k(classlist):
    classcount = classlist.value_counts()
    result = classcount.sort_values(ascending=False).index[0]
    return result


# 建立决策树  （DataFrame）（返回dict）： {'water': {0: 'no', 1: {'food': {0: 'no', 1: 'yes'}}}}
def createtree(data):
    print("------")
    labels = data.columns
    print(labels)
    classlist = data[labels[-1]]
    print("------")
    print(classlist)
    if (len(classlist.values) == classlist.value_counts()[0]):  # 结束条件1：该分支目标变量唯一
        return classlist.values[0]
    if (len(labels) == 1):  # 结束条件2：所有特征名都循环完了
        return major_k(classlist)  # 这里并不能直接返回目标变量名，可能不唯一，所以调用major_k
    bestFeature = choosebestfeaturetosplit(data)
    myTree = {bestFeature: {}}  # 这里很巧妙，以此来创建嵌套字典
    unique = set(data[bestFeature])
    for value in unique:
        myTree[bestFeature][value] = createtree(splitdataSet(data, bestFeature, value))  # 递归创建树
    return myTree


# 分类器预测  （嵌套字典 列表特征名 列表测试数据）
def classfiy(myTree, labels, test):
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


# 画决策树pdf图   （DataFrame）
def showtree_pdf(data):
    from sklearn import tree  # 导入sklearn的决策树模型（包括分类和回归两种）
    import pydotplus  # 画句子的依存结构树

    a = data.iloc[:, :-1]  # 特征矩阵
    b = data.iloc[:, -1]  # 目标变量
    clf = tree.DecisionTreeClassifier()  # 分类决策树
    clf.fit(a, b)
    dot_data = tree.export_graphviz(clf, out_file=None)  # 利用export_graphviz将树导出为Graphviz格式
    graph = pydotplus.graph_from_dot_data(dot_data)
    graph.write_pdf("iris1.pdf")  # 保存树图iris.pdf到本地


if __name__ == "__main__":
    data = createdata()  # 创建数据集

    myTree = createtree(data)  # 创建嵌套字典树
    print(myTree)

    result = classfiy(myTree, list(data.columns), [1,0,1,1,1,1,1,0,0,0,1,1,0,1,0,1,0,1,1,1])  # 预测测试数据
    print(result)

    showtree_pdf(data)  # 使用sklearn和pydotplus来画决策树，windows需要提前安装graphviz工具
