#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'

import threading
import os
import shutil
from lib.function import confdeal
from lib.function import filedeal
from lib.function import treedeal
from lib.function import common
from lib.function import netrequest
from lib.special import special
class Check(threading.Thread):
    def __init__(self,t_name,scriptPath,qHeartHeats,qMonitor,qRepaire,backup,sessionDic):       #初始化
        threading.Thread.__init__(self,name=t_name)
        self.scriptPath = scriptPath
        self.qHeartHeats = qHeartHeats
        self.qMonitor = qMonitor
        self.qRepaire = qRepaire
        self.sessionDic = sessionDic
        self.backup = backup
        pathDic = confdeal.getConfPath(scriptPath)
        treedeal.checkTopFlag(pathDic['bakPath'],sessionDic['sessionName'],sessionDic['projectName'])
        self.rarTopPath = pathDic['rarPath']
        self.bakTopPath = pathDic['bakPath']
        self.cashTopPath = pathDic['cashPath']
        self.bakPath = pathDic['bakPath'] + os.sep + sessionDic['sessionName']
        self.cashPath = pathDic['cashPath'] + os.sep + sessionDic['sessionName']
        self.runFlag = 1
        self.checkFlag = 1

    def run(self):
        if  os.path.exists(self.cashPath):                                       # 判断项目是否存在，不存在则创建文件夹
            shutil.rmtree(self.cashPath)                                                 #如果存在，则删除  ,然后重建
        os.mkdir(self.cashPath)
        remoteDic = confdeal.getConfRemote(self.scriptPath)
        if self.decomZiptoDir(remoteDic,self.cashTopPath,1):
            if self.checkBakFold():                                                              # 检查备份文件是否正常
                if not self.checkWebSource():                                                                    # 如果网站源码不正常
                    if not self.runFlag:                                                         # 终止、
                        special.echo("自检失败 ！")
                        return
                    special.echo("网站源文件出现异常 ！ 正在还原 ...")
                    self.runRepair(self.sessionDic['targetPath'])                                          # 还原项目
                    if not self.runFlag:                                                         # 终止
                        special.echo("自检失败 ！")
                        return
                if not self.runFlag:                                                #终止递归的判断条件
                    return
                elif self.runFlag:                                                                            # 从临时模式切换至安全模式
                    self.qRepaire.put(['safe','safe','safe'])
            else :                                                                               # 如果备份文件是不正常
                special.echo("备份文件出现异常 ！正在还原 ...")
                if self.decomZiptoDir(remoteDic,self.bakTopPath,0):
                    self.runRepair(self.sessionDic['targetPath'] )                                              #还原项目
                    if not self.runFlag:                                                #终止递归的判断条件
                        return
                    elif self.runFlag:                                                                            # 从临时模式切换至安全模式
                        self.qRepaire.put(['safe','safe','safe'])
                else:
                    special.echo("没有找到备份文件 ！\n开启备份模式 ！")
                    self.backup.start()
        else :
            special.echo("没有找到备份文件 ！\n开启备份模式 ！")
            self.backup.start()
        if not self.runFlag:                                                                   #终止
            special.echo("自检失败 ！")

    def decomZiptoDir(self,remoteDic,targetDir,isFlag):
        if isFlag:
            flagSuffix = '_flag'
        else:
            flagSuffix = ''
        if netrequest.downLoad(remoteDic['remoteHost'],remoteDic['remotePort'],self.rarTopPath,self.sessionDic['sessionName']+flagSuffix,isFlag):    # 下载flag文件
            if filedeal.decomZip(os.sep.join([self.rarTopPath,'download',self.sessionDic['sessionName']+flagSuffix]),targetDir):
                return True
            else:
                if filedeal.decomZip(os.sep.join([self.rarTopPath,'upload',self.sessionDic['sessionName']+flagSuffix]),targetDir):
                    return True
        else :
            if filedeal.decomZip(os.sep.join([self.rarTopPath,'upload',self.sessionDic['sessionName']+flagSuffix]),targetDir):
                return True
        return False

    # 备份文件是否正常
    def checkBakFold(self):
        self.checkFlag = 1
        if not self.runFlag:                                                #终止递归的判断条件
            self.checkFlag = 0
            return self.checkFlag
        self._checkBakFlag(self.cashPath)                                     # 检查flag文件是否正常
        shutil.rmtree(self.cashPath)
        if not self.runFlag:                                                #终止递归的判断条件
            return self.checkFlag
        self._runBakCheck(self.bakPath)                                     # 检查备份文件
        return self.checkFlag

    # 根据接收到flag树 来对比备份的flag树文件是否一致
    def _checkBakFlag(self,projectPath):
        if not self.checkFlag:
            return
        pList=os.listdir(projectPath)
        pList.sort()
        for i in pList:                                #遍历目录
            rarFile = os.sep.join([projectPath,i])
            if os.path.isdir(rarFile):
                self._checkBakFlag(rarFile)
            elif os.path.isfile(rarFile):
                bakFile = self.bakPath+rarFile[len(self.bakPath)+1:]
                if not os.path.exists(bakFile):
                    self.checkFlag = 0
                    return
                with open (rarFile, 'rb')as sockOutput,open(bakFile, 'rb') as bakOutput:     #读取flag内容进行对比
                    sockText,bakText = sockOutput.read(),bakOutput.read()
                    if not common.compareFileStr(bakText,sockText):
                        self.checkFlag=0
                        return
    # 检查备份文件
    def _runBakCheck(self,targetPath):
        if not self.checkFlag:
            return
        pList = os.listdir(targetPath)
        pList.sort()
        for i in pList:                                #遍历目录
            if not self.checkFlag:
                return
            bakFile = os.sep.join([targetPath,i])
            if os.path.isdir(bakFile):
                self._runBakCheck(bakFile)
            elif os.path.isfile(bakFile):
                if bakFile[bakFile.rfind(os.sep)+1:] == self.sessionDic['flagName']:
                    with open(bakFile,'r') as bakInput :                   # 读取flag文件信息
                        Text=bakInput.read()
                    fileType=Text[:4]
                    fileName=Text[5:21]
                    filePath=bakFile[:-16]+fileName
                    if fileType=='fold':
                        if not os.path.isdir(filePath):
                            self.checkFlag=0
                            return
                    elif fileType=='file':                          # 如果是文件，则对比内容md5
                        if not os.path.isfile(filePath):
                            self.checkFlag=0
                            return
                        textMd5=common.getMd5(filedeal.getZipContent('file',filePath))
                        if  textMd5 != fileName:
                            self.checkFlag=0
                            return



    # 检查网站源码
    def checkWebSource(self):
        if  not os.path.exists(self.cashPath):                                       # 判断项目是否存在，不存在则创建文件夹
            os.mkdir(self.cashPath)
        if not self.runFlag:                                                #终止递归的判断条件
            self.checkFlag =0
            return self.checkFlag
        self._runWebCheck(self.sessionDic['targetPath'],self.cashPath)                                  # 开始备份
        if not self.runFlag:                                                # 终止递归的判断条件
            self.checkFlag =0
            return self.checkFlag
        self._checkWebFlag(self.bakPath)                                    # 开始对比临时文件和备份文件
        if not self.runFlag:                                                # 终止递归的判断条件
            self.checkFlag =0
            return self.checkFlag
        shutil.rmtree(self.cashPath)                                         # 删除临时文件
        return self.checkFlag

    # 根据网站源码创建flag树
    def _runWebCheck(self,projectPath,tempPath):
        pList = os.listdir(projectPath)
        pList.sort()
        for i in pList:                                                              # 遍历目录
            file = os.sep.join([projectPath,i])
            fileName = file[file.rfind(os.sep)+1:]                                            # 获取文件名
            if os.path.isdir(file):                                                     # 判断file是否为文件夹
                md5=common.getMd5(fileName)  #计算文件名的md5
                tempPath += os.sep+md5
                if not os.path.exists(tempPath):                               # 判断file是否存在，不存在则创建文件夹
                    os.mkdir(tempPath)
                if not os.listdir(tempPath):                                # 判断文件是否为空，空则创建flag文件
                    output = open(tempPath+os.sep+self.sessionDic['flagName'], 'a')
                    output.close()
                flagFileInfo="fold:"+md5+":"+fileName+"\n"                          #.flag文件信息
                with open(tempPath[:-17]+os.sep+self.sessionDic['flagName'], 'a') as output:
                    output.write(flagFileInfo)
                self._runWebCheck(file,tempPath)
                tempPath=tempPath[0:-17]
            elif os.path.isfile(file):                                  #判断是否为文件，是则计算hash
                with open(file, 'rb') as output:
                    text = output.read()
                md5=common.getMd5(text)   #计算文件内容哈希值
                tempPath=tempPath+os.sep+md5
                flagFileInfo="file:"+md5+":"+fileName+"\n"
                tempPath=tempPath[0:-17]
                with open(tempPath+os.sep+self.sessionDic['flagName'], 'a') as output:
                    output.write(flagFileInfo)

    # 根据备份flag树来对比临时flag树
    def _checkWebFlag(self,projectPath):
        if not self.checkFlag:
            return
        pList = os.listdir(projectPath)
        pList.sort()
        for i in pList:                                #遍历目录
            bakFile =os.sep.join([projectPath,i])
            if os.path.isdir(bakFile):
                self._checkWebFlag(bakFile)
            elif os.path.isfile(bakFile):
                if bakFile[bakFile.rfind(os.sep)+1:] == self.sessionDic['flagName'] :
                    tempFile = self.cashPath + bakFile[len(self.cashPath)-1:]
                    if not os.path.exists(tempFile):
                        self.checkFlag = 0
                        return
                    with open (tempFile, 'r')as tempOutput,open(bakFile, 'r') as bakOutput:     #读取flag内容进行对比
                        tempText,bakText = tempOutput.read(),bakOutput.read()
                        if not common.compareFileStr(bakText,tempText):
                            self.checkFlag=0
                            return

    # 修复函数
    def runRepair(self,targetPath):
        self._runRepair(targetPath)                     # 删除不符合的
        self.qRepaire.put(['repaire','repaire',targetPath])

    def _runRepair(self,targetPath):
        pList = os.listdir(targetPath)
        pList.sort()
        for i in pList:
            fold = os.sep.join([targetPath,i])
            flag,bakPath = treedeal.bakIsExist(special.decoding(fold),self.sessionDic['targetPath'],self.sessionDic['projectName'],self.bakTopPath,self.sessionDic['flagName'])
            if os.path.isdir(fold):
                if flag == 'fold':
                    self._runRepair(fold)
                else :
                    filedeal.delete(special.decoding(fold))
            elif os.path.isfile(fold):
                if flag != 'file':
                    filedeal.delete(special.decoding(fold))
            else :
                filedeal.delete(special.decoding(fold))


    # 线程停止函数
    def stopRun(self):
        self.runFlag = 0