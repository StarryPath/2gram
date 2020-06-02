import json
import os
import pickle
import time
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.http import HttpResponse
from django.shortcuts import render
import binascii
import sys
import ast
# Create your views here.
from xcbs import settings

dec_str=[]
def index(request):
    return render(request, 'index.html')
def tree(request):
    return render(request, 'tree.html')
def tree2(request):
    return render(request, 'tree2.html')
def detect(request):
    return render(request, 'detect.html')
@csrf_exempt
def FileUploads(req):
    file = req.FILES.get('file')  # 获取文件对象，包括文件名文件大小和文件内容
    curttime = time.strftime("%Y%m%d")
    #规定上传目录
    upload_url = os.path.join("/home/fy/xcbs/mal/static/",'attachment')
    #判断文件夹是否存在
    folder = os.path.exists(upload_url)
    if not folder:
        os.makedirs(upload_url)
        print("创建文件夹")
    if file:
        file_name = file.name
        #判断文件是是否重名，懒得写随机函数，重名了，文件名加时间
        if os.path.exists(os.path.join(upload_url,file_name)):
            name, etx = os.path.splitext(file_name)
            addtime = time.strftime("%Y%m%d%H%M%S")
            finally_name = name + "_" + addtime + etx
            #print(name, etx, finally_name)
        else:
            finally_name = file.name
        #文件分块上传
        upload_file_to = open(os.path.join(upload_url, finally_name), 'wb+')
        for chunk in file.chunks():
            upload_file_to.write(chunk)
        upload_file_to.close()
        #返回文件的URl
        file_upload_url = "/home/fy/xcbs/mal/static/" + 'attachment/'  +finally_name
        #构建返回值
        response_data = {}
        response_data['FileName'] = file_name
        response_data['FileUrl'] = file_upload_url
        response_json_data = json.dumps(response_data)#转化为Json格式
        return HttpResponse(response_json_data)
def classfiy(myTree, labels, test):
    global classlabel
    global dec_str

    firstStr = list(myTree.keys())[0]  # 需要获取首个特征的列号，以便从测试数据中取值比较
    dec_str.append(firstStr)
    secondDict = myTree[firstStr]  # 获得第二个字典
    featIndex = labels.index(firstStr)  # 获取测试集对应特征数值
    for key in secondDict.keys():
        if (test[featIndex] == key):
            if (type(secondDict[key]).__name__ == 'dict'):  # 判断该值是否还是字典，如果是，则继续递归

                classlabel = classfiy(secondDict[key], labels, test)
            else:
                classlabel = secondDict[key]
    return classlabel
def result(request):
    global dec_str
    sys.setrecursionlimit(1000000)
    name=request.GET["name"]
    filename="/home/fy/xcbs/mal/static/attachment/"+name
    list_file = open('labels.pickle', 'rb')
    labels = pickle.load(list_file)
    #print(labels)
    list2_file = open('id3.pickle', 'rb')
    id3tree = pickle.load(list2_file)
    #print(id3tree)
    list3_file = open('c45.pickle', 'rb')
    list3 = pickle.load(list3_file)
    #print(list3)
    d1=[]
    if name[-4:]==".exe":
        fh = open(filename, 'rb')
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
            print("jia ke")
        data = []
        for lab in labels:
            if hexstr.find(lab) != -1:
                data.append(1)
            else:
                data.append(0)
        res= classfiy(id3tree, labels, data)  # 预测测试数据
        d1=dec_str
        dec_str=[]
        res2=classfiy(list3, labels, data)
    else:
        file = open(filename)
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
        res= classfiy(id3tree, labels, data)  # 预测测试数据
        d1=dec_str
        dec_str=[]
        res2 = classfiy(list3, labels, data)
    print(dec_str)
    print(d1)

    if res==0:
        r1="非恶意代码"
    else:
        r1="恶意代码"
    if res2==0:
        r2="非恶意代码"
    else:
        r2="恶意代码"
    return render(request, 'result.html', {'name':name,'result1': r1,'result2': r2,"d1":d1,"dec_str":dec_str})

