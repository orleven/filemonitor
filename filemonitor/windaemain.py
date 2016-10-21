#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'
'''
    增加守护进程（windows服务）
'''
from lib.special import special
if special.whatIsPlatform() != 'Windows':
    print 'This is not a Windows operating system ! '
    exit()

import pythoncom
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import os
import sys
import subprocess
import time
from lib.function import confdeal

class Daemon (win32serviceutil.ServiceFramework):
    _svc_name_ = "File Monitor Service"
    _svc_display_name_ = "File Monitor Service"
    _svc_description_ = "File Monitor Service ."

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.monitorProcess()

    def monitorProcess(self):
        with open('C:\\filemonitor', 'r') as f:
            scriptPath=f.read()
        if os.path.exists(scriptPath):
            cmd = 'cd '+scriptPath+' && python promain.py'
            child = subprocess.Popen(cmd, shell=True)
            while 1:
                if child.poll()==1:
                    child = subprocess.Popen(cmd, shell=True)
                time.sleep(10)
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

    def SvcStop(self):
        with open('C:\\filemonitor', 'r') as f:
            scriptPath=f.read()
        if os.path.exists(scriptPath):
            remoteDic = confdeal.getConfRemote(scriptPath)
            if remoteDic:
                ret = os.popen('netstat -ano | findstr \":'+str(remoteDic['localPort'])+' \"')
                strList =  list(set(ret.read().split('\n')))
                for pidStr in strList:
                    if pidStr != '':
                        pidStr = pidStr[pidStr.rfind(' ')+1:]
                        os.system("taskkill /F /T /PID "+pidStr)
        else : 
            exit()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

if __name__ == '__main__':
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    with open('C:\\filemonitor', 'w') as f:
        f.write(scriptPath)
    confdeal.initConf(scriptPath)
    win32serviceutil.HandleCommandLine(Daemon)












