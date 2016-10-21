#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'

import socket
import json
import os
import time
import sys
from Queue import Queue
from lib.function import common
from lib.function import confdeal
from lib.function import sessiondeal
from lib.function import treedeal
from lib.special import special
from lib.module.heartbeats import Heartbeats
from lib.module.backup import Backup
from lib.module.repaire import Repaire
from lib.module.check import Check
if special.whatIsPlatform() == 'Windows':
    from lib.module.winmonitor import Monitor
else :
    from lib.module.linmonitor import Monitor

class Controller(object):
    def __init__(self,scriptPath):
        self.scriptPath = scriptPath
        heartbeatDic =  confdeal.getConfHeartbeats(self.scriptPath)
        if not heartbeatDic:
            confdeal.setConfHeartbeats(scriptPath,60)
        confdeal.setConfPath(scriptPath)
        self.pathDic = confdeal.getConfPath(self.scriptPath)
        self.initPath(self.pathDic)
        if not confdeal.getConfFile(self.scriptPath) :
            confdeal.setConfFile(self.scriptPath,50)
        self.qHeartbeats = Queue()
        self.heartBeat = Heartbeats('hb',self.scriptPath,self.qHeartbeats)
        self.sessionList=[]
        self.threadList=[]

    def working(self):
        self.heartBeat.start()
        remoteDic = confdeal.getConfRemote(self.scriptPath)
        time.sleep(4)
        try:
            s = socket.socket();
            s.bind(("0.0.0.0",remoteDic['localPort']))
            s.listen(1);   #指定最多允许多少个客户连接到服务器。
        except:
            self.heartBeat.stopRun()
            print 'Socker init error ! \nPlease check port\nExit!'
            sys.exit()
        if not self.bakOrCheck():
            print 'No config ! \nWaiting for server\'s command !'
        # self.test()         # 测试
        while 1:  # 接受指令
            try:
                conn, addr = s.accept()
                conn.settimeout(5);
                if addr != remoteDic['remoteHost']:         # 判断IP是否合法
                    print "IP($s)illegal connection ！\nAuto reject ..." %(addr)
                    conn.close()
                    continue
                messageJson = conn.recv(4096);          # 接收服务器消息
                message =json.loads(messageJson)
                command=message['command']
                if command == 'start':          # 开始监控和备份
                    slash , bslash = special.getSlash()
                    common.dicStringReplace(message,bslash,slash)
                    if os.path.exists(message['targetPath']) :
                        message['projectName'] = message['targetPath'][message['targetPath'].rfind(os.sep)+ 1:]
                        message['sessionName'] = common.getMd5(message['projectName'] +remoteDic['localHost']+str(remoteDic['localPort']))
                        message['flagName'] = common.getRandom()
                        self.startMonitor(message,1)
                    else:
                        print "The monitor path is not exists ！"
                elif command  =='stop':         # 停止监控和备份
                    message['projectName'] = message['targetPath'][message['targetPath'].rfind(os.sep)+ 1:]
                    message['sessionName'] = common.getMd5(message['projectName'] +remoteDic['localHost']+str(remoteDic['localPort']))
                    self.stopMonitor(message)
                elif command  =='getPath' or command =='getWhitePath':          # 遍历返回所有目录信息
                    infoJson = self.getPath(message)
                    conn.sendall(infoJson)
                conn.close()            # 关闭连接
            except :
                print 'Illegal command  ！'
                time.sleep(5)

    def initPath(self,pathDic):
        for i in pathDic.keys():
            if not os.path.exists(pathDic[i]):
                os.mkdir(pathDic[i])
        downloadPath = pathDic['rarPath']+ os.sep + 'download'
        uploadPath = pathDic['rarPath']+ os.sep + 'upload'
        if not os.path.exists(downloadPath):
            os.mkdir(downloadPath)
        if not os.path.exists(uploadPath):
            os.mkdir(uploadPath)

    def bakOrCheck(self):
        self.sessionList = sessiondeal.getSession(self.pathDic['sessionPath'])
        flag = 0
        for monitorDic in self.sessionList:
            self.startMonitor(monitorDic,0)
            flag = 1
        if flag:
            return True
        else:
            return False


    def startMonitor(self,message,doBak):
        for i in range(0,len(self.sessionList)):
            if self.sessionList[i]['sessionName'] == message['sessionName']:
                self.stopMonitor(self.sessionList[i])
                del self.sessionList[i]
                break
        qMonitor = Queue()
        qRepaire = Queue()
        backup = Backup('b_'+message['sessionName'] ,self.scriptPath,self.qHeartbeats,qMonitor,message)
        repaire = Repaire('r_'+message['sessionName'],self.scriptPath,self.qHeartbeats,qMonitor,qRepaire,message)
        check = Check('c_'+message['sessionName'],self.scriptPath,self.qHeartbeats,qMonitor,qRepaire,backup,message)
        monitor = Monitor('m_'+message['sessionName'],self.scriptPath,self.qHeartbeats,qMonitor,qRepaire,backup,check,message)          #监控线程
        monitor.start()
        if message['mode']=='safe':
            if doBak:
                backup.start()
            else:
                check.start()
            repaire.start()
        threadDic = {'name':message['sessionName'],'monitor':monitor,'backup':backup,'check':check,'repaire':repaire}
        self.threadList.append(threadDic)
        sessiondeal.setSession(self.pathDic['sessionPath'],message)


    def  stopMonitor(self,message):
        for i in range(0,len(self.threadList)):
            if self.threadList[i]['name'] == message['sessionName']:
                self.threadList[i]['monitor'].stopRun()
                self.threadList[i]['backup'].stopRun()
                self.threadList[i]['check'].stopRun()
                self.threadList[i]['repaire'].stopRun()
                del self.threadList[i]
                break

    # 未测试
    def getPath(self,message):
        folderPathList = message['targetPath']
        folderPathList = folderPathList.split(',')
        # 循环遍历每个目录下的信息
        for x in range(0,len(folderPathList)):
            if folderPathList[x]!='':
                folderPath = folderPathList[x]
                info=treedeal.getWebSourceFolePath(message['command'],folderPath)
                #返回信息
                # infoDict = {'path':info}
                infoJson=json.dumps(info)
                return infoJson


    # test
    def test(self):
        remoteDic = confdeal.getConfRemote(self.scriptPath)
        message = {
            'command': 'start',
            'targetPath':'/home/gmfork/Desktop/test',
            'mode':'safe',
            'doBak':1,
            'whiteList':['/home/gmfork/Desktop/test/python/other'],
            'blackList':['php','asp'],
            'timeDelay':'1',
        }
        command=message['command']

        # 开始监控和备份
        if command == 'start':
            slash , bslash = special.getSlash()
            common.dicStringReplace(message,bslash,slash)
            if os.path.exists(message['targetPath']):
                message['projectName'] = message['targetPath'][message['targetPath'].rfind(os.sep)+ 1:]
                message['sessionName'] = common.getMd5(message['projectName'] +remoteDic['localHost']+str(remoteDic['localPort']))
                message['flagName'] = common.getRandom()
                self.startMonitor(message,1)
            else:
                print "The monitor path is not exists ！"

        # 停止监控和备份
        elif command  =='stop':
            message['projectName'] = message['targetPath'][message['targetPath'].rfind(os.sep)+ 1:]
            message['sessionName'] = common.getMd5(message['projectName'] +remoteDic['localHost']+str(remoteDic['localPort']))
            self.stopMonitor(message)

        # 遍历返回所有目录信息
        elif command  =='getPath' or command =='getWhitePath':
            self.getPath(message)



