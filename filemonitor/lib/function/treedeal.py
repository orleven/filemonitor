#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'

import os
from lib.function import common
from lib.special import special


def getTopFlag():
    return common.getMd5('flag@orleven')

def checkTopFlag(targetPath,projectMd5,projectName):        # 写入顶级flag文件
    bakTopFlagPath = targetPath + os.sep + getTopFlag()
    flag = 0
    if  os.path.exists(bakTopFlagPath):               #查看顶级flag文件  如果记录已经存在则不追加
        with open(bakTopFlagPath, 'r') as output:
            while True:                                                             #如果已有记录，则不动
                line = output.readline()
                if not line:
                    break
                if not cmp(line, "fold:"+projectMd5+":"+projectName+"\n") :
                    flag = 1
                    break
    if flag == 0:                                                              # 追加记录
        with open(bakTopFlagPath, 'a+') as output:
            output.write("fold:"+projectMd5+":"+projectName+"\n")

# 查找flag文件
def lookForFlag(targetPath,projectPath,projectName,bakPath,flagName):
    targetPath = targetPath[len(projectPath)-len(projectName):]
    pathList = targetPath.split(os.sep)  #  根据各级的flag文件，查找目标文件的备份路径
    content = ''
    flag = 0
    flagPath = bakPath + os.sep + getTopFlag()
    for tempName in pathList:
        with open(flagPath,'r') as output:
            while 1:
                line = output.readline()
                if not line:
                    break
                content = line.split(':')
                if content[2][:-1] == special.coding(tempName):
                # if content[2][:-1] == tempName:
                    flag += 1
                    bakPath += os.sep + content[1]
                    flagPath = os.sep.join([flagPath [0:-17 ],content[1],flagName])
                    break
    if flag != len(pathList):# 备份文件flag里没有
        return False,content,bakPath
    else :
        return True,content,bakPath

def bakIsExist(targetPath,projectPath,projectName,bakPath,flagName):
    try:
        flag,content,bakPath = lookForFlag(targetPath,projectPath,projectName,bakPath,flagName)
        if not flag:                     #如果不存在则返回空
            return  'no',bakPath
        if not cmp(content[0],'fold'):                                          #如果目标是文件夹，则返回文件夹
            return 'fold',bakPath
        elif not cmp(content[0],'file'):                                      #如果目标是文件，则返回文件
            return 'file',bakPath
    except:
        return 'no',None


def getWebSourceFolePath(command,projectPath):
    foldPathList=[]
    if command =='getPath':
        for i in os.listdir(projectPath):
            fold=os.path.join(projectPath,i)
            if os.path.isdir(fold):
                foldIn=fold.replace('\\','/')
                dic={"text":i,"attributes":{"path":foldIn},"state":"closed","children":[{"text":"..."}]}
                foldPathList.append(dic)
    elif command=='getWhitePath':
        foldPathList=_getWebSourceFolePath(projectPath)
    return foldPathList

def _getWebSourceFolePath(projectPath):
    list=[]
    for i in os.listdir(projectPath):
        fold=os.path.join(projectPath,i)
        if os.path.isdir(fold):
            tempList=_getWebSourceFolePath(fold)
            foldIn=fold.replace('\\','/')
            if tempList is [] or tempList ==[] :
                dic={"text":i,"attributes":{"path":foldIn},"state":"closed","children":[{"text":"..."}]}
            else:
                dic={"text":i,"attributes":{"path":foldIn},"children":tempList}
            list.append(dic)
    return list