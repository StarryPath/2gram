import sys
import json
import pickle
i=0
list2_file = open('c45.pickle', 'rb')
c45tree = pickle.load(list2_file)
def c_json(myTree,k):

    tree_dict={}
    firstStr = list(myTree.keys())[0]

    tree_dict["name"]=firstStr
    if k!=-1:
        tree_dict["name"]=str(k)+" "+firstStr
    tree_dict["children"]=[]
    secondDict = myTree[firstStr]
    for key in secondDict.keys():
        print(key)

        if (type(secondDict[key]).__name__ == 'dict'):
            tree_dict["children"].append(c_json(secondDict[key],key))
        else:
            ddd={}
            ddd["name"]=str(key)+" "
            if secondDict[key]==0:
                ddd["name"]+="非恶意"
            else:
                ddd["name"] +="恶意代码"
            tree_dict["children"].append(ddd)
    return tree_dict
if __name__=='__main__':
    sys.setrecursionlimit(1000000)
    mm=c_json(c45tree,-1)
    print(mm)
    json_str = json.dumps(mm, indent=4)
    with open('/home/fy/xcbs/mal/static/tree2.json', 'w') as json_file:
        json_file.write(json_str)