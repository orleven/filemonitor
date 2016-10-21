#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'

import threading
import  os
from lib.function import confdeal
from lib.special import special
from lib.function import common
from lib.function import netrequest

class Heartbeats(threading.Thread):
    def __init__(self,t_name,scriptPath,qHeartbeats):
        threading.Thread.__init__(self,name=t_name)
        self.qHeartbeats = qHeartbeats
        self.pathDic = confdeal.getConfPath(scriptPath)
        self.heartbeatsLogPath = self.pathDic['logPath'] + os.sep + 'heartbeats.log'
        self.monitorLogPath = self.pathDic['logPath'] + os.sep + 'monitor.log'
        self.cashLogPath = self.pathDic['logPath'] + os.sep + 'cash.log'
        self.cashList = []               # 日志缓存

        self.clog = open(self.cashLogPath,'a+')
        self.remoteDic = confdeal.getConfRemote(scriptPath)
        self.timeDelay = confdeal.getConfHeartbeats(scriptPath)['delayTime']

        self.runFlag = 1             # 线程运行标志
        self.portFlag = 1            # 连通标志
        self.differentFlag = 1
        self.lastTime = None
        self.nowTime = None

    def run(self):
        with open(self.heartbeatsLogPath,'a+') as hlog, open(self.monitorLogPath,'a+') as mlog:
            self.nowTime = common.getNowTime()
            hlog.write("[%s][信息][连接服务器 (%s:%d) ...]\n" %(self.nowTime,self.remoteDic['remoteHost'],self.remoteDic['remotePort']))
            hlog.flush()
            special.echo("连接服务器 (%s:%d) ..."  %(self.remoteDic['remoteHost'],self.remoteDic['remotePort']))

            while self.runFlag:
                self.nowTime = common.getNowTime()
                # 每分钟心跳一次
                if  common.dateDiffInSeconds(self.lastTime,self.nowTime) >= self.timeDelay :
                    self.lastTime =  self.nowTime
                    if netrequest.post(self.remoteDic['remoteHost'],self.remoteDic['remotePort'],self.remoteDic['localHost'],self.nowTime):
                        self.portFlag = 1
                    else :
                        self.portFlag = 0
                # 有消息推送过来
                if not self.qHeartbeats.empty():
                    textList = self.qHeartbeats.get()
                    happend,level,info = self.messageHandle(textList[0],textList[1],textList[2],mlog)
                    if self.portFlag:
                        if not netrequest.sendInfo(self.remoteDic['remoteHost'],self.remoteDic['remotePort'],self.remoteDic['localHost'],happend,level,info):
                            self.portFlag = 0
                            self.cashList.append("%s\t%s\t%s\n" %(happend,level,info))
                        else :
                            self.portFlag = 1
                    else :
                        self.cashList.append("%s\t%s\t%s\n" %(happend,level,info))
                if self.differentFlag ^ self.portFlag :
                    self.differentFlag = not self.differentFlag
                    if self.portFlag :
                        special.echo("连接服务器 (%s:%d) 成功 ！"  %(self.remoteDic['remoteHost'],self.remoteDic['remotePort']))
                        hlog.write("[%s][信息][连接服务器 (%s:%d) 成功 ！]\n" %(self.nowTime,self.remoteDic['remoteHost'],self.remoteDic['remotePort']))
                        hlog.flush()
                        self.clog.close()
                    else :
                        special.echo("连接服务器 (%s:%d) 失败 ！"   %(self.remoteDic['remoteHost'],self.remoteDic['remotePort']))
                        hlog.write("[%s][信息][连接服务器 (%s:%d) 失败 ！]\n" %(self.nowTime,self.remoteDic['remoteHost'],self.remoteDic['remotePort']))
                        hlog.flush()
                        self.clog = open(self.cashLogPath,'a+')

                 # 如果有缓存的log 则进行处理

                if self.portFlag :
                    if  os.path.exists(self.cashLogPath):
                        self.clog = open(self.cashLogPath,'w')
                        while 1:
                            line = self.clog.readline()
                            if not line:
                                break
                            temp = line.split('\t')
                            if not netrequest.sendInfo(temp[0],temp[1],temp[2]):
                                self.portFlag = 0
                                self.cashList.append("%s\t%s\t%s\n" %(temp[0],temp[1],temp[2]))
                            else :
                                self.portFlag = 1
                        os.remove(self.cashLogPath)
                else :
                    if self.cashList:
                        self.cashList.reverse()
                        while self.cashList:
                            self.clog.write(self.cashList.pop())
                            self.clog.flush()

    # 停止心跳
    def stopRun(self):
        self.runFlag =0

    # 消息处理函数
    def messageHandle(self,action,info,done,mlog):
        if action == 'Created'  or  action == 'Renamed to something':   #重命名:
            level = '提醒'
            action = '新建'
        elif action == 'Deleted' or  action == 'Renamed from something':   #重命名:
            level = '危险'
            action = '删除'
        elif action == 'Updated':   #修改
            level = '警告'
            action = '修改'
        else:
            level='信息'
            action = '信息'
        slash , bslash = special.getSlash()
        info = info.replace(bslash,slash)
        nowTime = common.getNowTime()
        if done:
            special.echo("[%s][%s][%s][已处理 ...]" %(nowTime,action,info))
            info += '[已处理]'
        else :
            special.echo("[%s][%s][%s]"  %(nowTime,action,info))
        mlog.write("[%s][%s][%s]\n" %(nowTime,action,info))
        mlog.flush()
        return  nowTime,level,action + " : "+info
