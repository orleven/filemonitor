#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'
import os
import threading
from lib.function import confdeal
from lib.function import filedeal
from lib.function import treedeal
from lib.special import special
class Repaire(threading.Thread):
    def __init__(self,t_name,scriptPath,qHeartHeats,qMonitor,qRepaire,sessionDic):
        threading.Thread.__init__(self,name=t_name)
        self.scriptPath = scriptPath
        self.qHeartHeats = qHeartHeats
        self.qRepaire = qRepaire
        self.qMonitor = qMonitor
        self.sessionDic = sessionDic
        self.pathDic = confdeal.getConfPath(scriptPath)
        self.runFlag = 1

    def run(self):
        self.runFlag = 1               #终止递归的判断条件
        while self.runFlag:
            deal,action,fileName = self.qRepaire.get()
            if deal == 'delete':
                if filedeal.delete(fileName):
                    self.qHeartHeats.put([action,fileName,1])
            elif deal == 'restore':
                if self.runDecompress(fileName):
                    self.qHeartHeats.put([action,fileName,1])
            elif deal == 'repaire' :
                self.runDecompress(fileName)
            elif deal == 'safe':
                special.echo("自检/恢复完毕 ！")
                self.qHeartHeats.put(['信息',self.sessionDic['projectName']+'切至安全模式 ...',0]) # 通知监控线程，备份完毕，令其转换成safe 模式
                self.qMonitor.put('True')
            else :
                return

    # 还原函数
    def  runDecompress(self,targetPath):
        flag,content,bakPath = treedeal.lookForFlag(targetPath,self.sessionDic['targetPath'],self.sessionDic['projectName'],self.pathDic['bakPath'],self.sessionDic['flagName'])  # 查找flag文件
        if not flag :
            return
        if not cmp(content[0],'fold'):                                          #如果目标是文件夹，则复原文件夹
            if not os.path.exists(targetPath):
                try :
                    os.mkdir(targetPath)
                except:
                    filedeal.createFold(targetPath)
                    os.mkdir(targetPath)
            self._runDeompress(bakPath,targetPath)
        elif not cmp(content[0],'file'):                                      #如果目标是文件，则直接解压文件
            try :
                filedeal.decompress(bakPath,targetPath)
            except:
                filedeal.createFold(targetPath)
                filedeal.decompress(bakPath,targetPath)
        return True

    # 递归遍历文件夹，解压文件，
    # bakPath  备份地址，即输入文件地址
    # resPath   还原地址，即输出文件地址
    def _runDeompress(self,bakPath,resPath):
        tempFlagPath = bakPath + os.sep +self.sessionDic['flagName']
        with open(tempFlagPath,'r') as output:
            txt = output.read()
        txt = txt.split('\n')
        for line in txt:
            if not line :
                break
            content = line.split(':')
            tempBakPath = bakPath + os.sep + content[1]
            tempResPath = resPath + os.sep + special.decoding(content[2])
            if not cmp(content[0],'fold'):
                if not os.path.exists(tempResPath):
                    try :
                        os.mkdir(tempResPath)
                    except:
                        filedeal.createFold(tempResPath)
                        os.mkdir(tempResPath)
                self._runDeompress(tempBakPath,tempResPath)
            elif not cmp(content[0],'file'):
                try :
                    filedeal.decompress(tempBakPath,tempResPath)
                except:
                    filedeal.createFold(tempResPath)
                    filedeal.decompress(tempBakPath,tempResPath)

    # 线程停止函数
    def stopRun(self):
        self.runFlag = 0