#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'

import threading
import os
import shutil
from lib.function import confdeal
from lib.function import treedeal
from lib.function import filedeal
from lib.function import common
from lib.function import netrequest
class Backup(threading.Thread):
    def __init__(self,t_name,scriptPath,qHeartHeats,qMonitor,sessionDic):       #初始化
        threading.Thread.__init__(self,name=t_name)
        self.scriptPath = scriptPath
        self.qHeartHeats = qHeartHeats
        self.qMonitor = qMonitor
        self.sessionDic = sessionDic
        pathDic = confdeal.getConfPath(scriptPath)
        treedeal.checkTopFlag(pathDic['bakPath'],sessionDic['sessionName'],sessionDic['projectName'])# 写入顶级flag文件
        self.rarTopPath = pathDic['rarPath']
        self.bakPath = pathDic['bakPath'] + os.sep + sessionDic['sessionName']
        self.rarPath = os.sep.join([pathDic['rarPath'],'upload',sessionDic['sessionName']])
        self.cashPath = pathDic['cashPath'] + os.sep + sessionDic['sessionName']
        self.runFlag = 1

    def run(self):      # 开始备份
        if  os.path.exists(self.bakPath):                                        #  判断项目是否存在，不存在则创建文件夹
            shutil.rmtree(self.bakPath)                                                 #如果存在，则删除  ,然后重建
        os.mkdir(self.bakPath)
        if  os.path.exists(self.cashPath):                                       # 判断项目是否存在，不存在则创建文件夹
            shutil.rmtree(self.cashPath)                                                 #如果存在，则删除  ,然后重建
        os.mkdir(self.cashPath)
        self.runCompress(self.sessionDic['targetPath'],self.bakPath)                     # 开始备份
        self.runFlagTree(self.bakPath)
        filedeal.comZip(self.cashPath,self.rarPath+'_flag')          # 压缩文件夹，并且上传，之后删除
        filedeal.comZip(self.bakPath,self.rarPath)
        # shutil.rmtree(self.rarPath)
        shutil.rmtree(self.cashPath)
        if not self.runFlag:                                                #终止递归的判断条件
            return
        if self.runFlag:                                                                            # 从临时模式切换至安全模式
            self.qHeartHeats.put(['信息',self.sessionDic['projectName'] + '切至安全模式 ...',0]) # 通知监控线程，备份完毕，令其转换成safe 模式
            self.qMonitor.put('True')
        remoteDic = confdeal.getConfRemote(self.scriptPath)
        netrequest.upload(remoteDic['remoteHost'],remoteDic['remotePort'],self.rarTopPath,self.sessionDic['sessionName']+'_flag',1)
        netrequest.upload(remoteDic['remoteHost'],remoteDic['remotePort'],self.rarTopPath,self.sessionDic['sessionName'],0)


    # 递归遍历项目，并生成md5 ，压缩文件，生成.flag文件,同时生成sock文件 用于压缩
    # projectPath  备份项目路径
    def runCompress(self,projectPath,bakPath):
        if not self.runFlag:                                                #终止递归的判断条件
            return
        pList=os.listdir(projectPath)
        pList.sort()
        for i in pList:                                #遍历目录
            filePath = os.sep.join([projectPath,i])
            fileName = i                           #获取文件名
            if os.path.isdir(filePath):                                       #判断file是否为文件夹
                md5 = common.getMd5(fileName)
                bakPath += os.sep + md5     #计算文件名的md5
                os.mkdir(bakPath)
                if not os.listdir(bakPath):                     # 判断文件夹是否为空，空则创建flag文件
                    output = open(bakPath+ os.sep + self.sessionDic['flagName'], 'w')
                    output.close( )
                flagFileInfo="fold:"+md5+":"+fileName+"\n"            #.flag文件信息
                with open(bakPath[0:-17]+ os.sep + self.sessionDic['flagName'], 'a') as output:
                    output.write(flagFileInfo)
                self.runCompress(filePath,bakPath)
                bakPath = bakPath[0:-17]
            elif os.path.isfile(filePath):                                  #判断是否为文件，是则进行压缩
                with open(filePath, 'rb') as output:
                    text = output.read()
                md5=common.getMd5(text)         #计算文件内容哈希值
                bakPath += os.sep +md5
                flagFileInfo="file:"+md5+":"+fileName+"\n"
                filedeal.compress(filePath, bakPath)                    #调用压缩函数
                bakPath = bakPath[:-17]
                with open(bakPath+os.sep+self.sessionDic['flagName'], 'a') as output:
                    output.write(flagFileInfo)

   # 从备份文件里复制出一份flag树
    def runFlagTree(self,targetPath):
        for i in os.listdir(targetPath):
            filePath = os.sep.join([targetPath,i])
            tempFile = self.cashPath + filePath[len(self.bakPath):]
            if os.path.isdir(filePath):                                                                          #判断file是否为文件夹
                os.mkdir(tempFile)
                self.runFlagTree(filePath)
            elif os.path.isfile(filePath):
                if i == self.sessionDic['flagName'] :
                    shutil.copyfile(filePath,tempFile)


    def stopRun(self):
        self.runFlag = 0


