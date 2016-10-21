#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'
import os
import win32file
import win32con
import threading
from lib.function import confdeal
from lib.function import common
from lib.function import treedeal
from lib.function import filedeal
class Monitor(threading.Thread):
    def __init__(self,t_name,scriptPath,qHeartHeats,qMonitor,qRepaire,backup,check,sessionDic):
        threading.Thread.__init__(self,name=t_name)
        self.ACTIONS = {
            1 : "Created",                            # 增
            2 : "Deleted",                            # 删
            3 : "Updated",                            # 该
            4 : "Renamed from something",          # 重命名之前
            5 : "Renamed to something"              # 重命名之后
        }
        FILE_LIST_DIRECTORY = win32con.GENERIC_READ | win32con.GENERIC_WRITE
        self.qHeartHeats = qHeartHeats
        self.qMonitor = qMonitor
        self.qRepaire = qRepaire
        self.backup = backup
        self.check =check
        self.hDir = win32file.CreateFile (
            sessionDic['targetPath'],
            FILE_LIST_DIRECTORY,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS,
            None
        )
        self.monitorPath = sessionDic['targetPath']
        self.projectName = self.monitorPath.split(os.sep)[-1]
        self.whiteList = sessionDic['whiteList']
        self.blackList = sessionDic['blackList']
        self.mode = sessionDic['mode']
        self.doBak = sessionDic['doBak']
        self.bakPath = confdeal.getConfPath(scriptPath)['bakPath']
        self.remoteDic = confdeal.getConfRemote(scriptPath)
        self.flagName = sessionDic['flagName']
        self.runFlag = 1

    # 线程运行函数
    def run(self):    #   运行前初始化
        self.runFlag  = 1
        if self.mode == 'safe':
            self.mode = 'temp'  # 进入临时模式
            self.qHeartHeats.put(['Info',''.join([self.projectName,'进入临时模式 ...']),0])
        elif self.mode == 'human':
            self.qHeartHeats.put(['Info',''.join([self.projectName,'进入人工模式 ...']),0])
        while self.runFlag :
            self.results = win32file.ReadDirectoryChangesW (
                self.hDir,  #handle: Handle to the directory to be monitored. This directory must be opened with the FILE_LIST_DIRECTORY access right.
                1024,  #size: Size of the buffer to allocate for the results.
                True,  #bWatchSubtree: Specifies whether the ReadDirectoryChangesW function will monitor the directory or the directory tree.
                win32con.FILE_NOTIFY_CHANGE_FILE_NAME |
                win32con.FILE_NOTIFY_CHANGE_DIR_NAME |
                win32con.FILE_NOTIFY_CHANGE_ATTRIBUTES |
                win32con.FILE_NOTIFY_CHANGE_SIZE |
                win32con.FILE_NOTIFY_CHANGE_LAST_WRITE |
                win32con.FILE_NOTIFY_CHANGE_SECURITY,
                None,
                None)
            for act, filename in self.results:               # 监控事件发生
                filename = self.monitorPath + os.sep + filename
                action = self.ACTIONS.get (act, "Unknown")
                if self.mode == 'human':# human模式
                    self.qHeartHeats.put([action,filename,0])
                elif self.mode == 'temp':#  临时模式
                    if self.qMonitor.empty():# 备份/自检 中出现文件操作
                        if self.doBak:                    # 不是自检
                            self.qHeartHeats.put([action,filename,0])
                            self.backup.stopRun()
                            self.check.stopRun()
                            self.qRepaire.put(['close','close','close'])
                            self.qHeartHeats.put([action,'备份时请勿操作文件 ！停止监控'+self.projectName+' ...',0])
                            self.stopRun()
                        else :                                                      # 自检
                            self.safeModeDeal(action,filename)
                    else:           # 备份中没有出现文件操作，切换至安全模式
                        if self.qMonitor.get() == 'True':
                            self.mode = 'safe'
                        self.safeModeDeal(action,filename)
                elif self.mode =='safe':# safe模式，即防篡改模式
                    self.safeModeDeal(action,filename)# 处理发生的事件

     # 处理发生的事件
    def safeModeDeal(self,action,filename):
        if self.mode == 'safe':
            whiteNum = len(self.whiteList)
            flag = False
            for i in xrange(0,whiteNum):# 判断是否在白名单里面
                if len(filename) > len(self.whiteList[i]):
                    if filename[:len(self.whiteList[i])] in self.whiteList:                #在白名单里
                        flag=True
                        suffix=filename.find('.') # 判断是否在黑名单里面
                        blackFlag=False
                        if suffix!=-1:
                            suffix=filename[suffix+1:]
                            for x in xrange(0,len(self.blackList)):
                                if self.blackList[x].lower() in suffix.lower():
                                    blackFlag=True
                        if blackFlag:# 黑名单修复
                            self.repair(action,filename)
                        else:# 百名单跳过
                            flag,bakPath = treedeal.bakIsExist(filename,self.monitorPath,self.projectName,self.bakPath,self.flagName)
                            if flag!='fold':
                                self.qHeartHeats.put([action,filename,0])
                        break;
            if not flag:        # 不在白名单
                self.repair(action,filename)
        else :
            self.repair(action,filename)

    def repair(self,action,filename):
        flag,bakPath = treedeal.bakIsExist(filename,self.monitorPath,self.projectName,self.bakPath,self.flagName)
        if action == 'Created'  or  action == 'Renamed to something':   #重命名:
            if flag == 'no':
                self.dealAndMessage(action,filename,'delete')
            else : # 计算md5值
                bakFileText = filedeal.getZipContent(flag,bakPath)
                if os.path.isdir(filename):                                       #判断file是否为文件夹
                    if not common.compareFoldStr(filename,bakFileText) :
                        self.dealAndMessage(action,filename,'restore')
                elif os.path.isfile(filename):                                  #判断是否为文件，是则进行压缩
                    with open(filename,'rb') as f:
                        webFileText = f.read()
                    if not common.compareFileStr(webFileText,bakFileText) :
                        self.dealAndMessage(action,filename,'restore')
        elif action == 'Deleted' or action == 'Renamed from something':   #重命名:
            if flag != 'no':
                self.dealAndMessage(action,filename,'restore')
        elif action == 'Updated':   #修改
            if flag != 'no':
                bakFileText = filedeal.getZipContent(flag,bakPath)
                if os.path.isdir(filename):                                       #判断file是否为文件夹
                    if not common.compareFoldStr(filename,bakFileText) :
                        self.dealAndMessage(action,filename,'restore')
                elif os.path.isfile(filename):                                  #判断是否为文件，是则进行压缩
                    with open(filename,'rb') as f:
                        webFileText = f.read()
                    if not common.compareFileStr(webFileText,bakFileText) :
                        self.dealAndMessage(action,filename,'restore')


    def dealAndMessage(self,action,filename,deal):
        # if self.mode == 'safe':
        #     self.qHeartHeats.put([action,filename,0])
        #     self.qRepaire.put([deal,action,filename])
        # else :
        #     self.qHeartHeats.put([action,filename,0])
        #     self.backup.stopRun()
        #     self.check.stopRun()
        #     self.qRepaire.put(['close','close','close'])
        #     self.qHeartHeats.put(['Info','备份或自检时请勿操作文件 ！停止监控'+self.projectName+' ...',0])
        #     self.stopRun()
        self.qHeartHeats.put([action,filename,0])
        self.qRepaire.put([deal,action,filename])

   # 停止监控函数
    def stopRun(self):
        self.runFlag  = 0
        self.qHeartHeats.put(['Info','停止监控'+self.projectName+' ...',0])

