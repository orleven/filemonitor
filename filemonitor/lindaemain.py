#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'
'''
    增加守护进程（linux）
'''
from lib.special import special
if special.whatIsPlatform() != 'Linux':
    print 'This is not a Linux operating system ! '
    exit()

import os
import datetime
import time
import sys
import atexit
import string  
import subprocess
from signal import SIGTERM  
from lib.function import confdeal

class Daemon:
    #需要获取调试信息，改为stdin='/dev/stdin', stdout='/dev/stdout', stderr='/dev/stderr'，以root身份运行。  
    def __init__(self, scriptPath,pidfile, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):  
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.scriptPath = scriptPath
       
    def _daemonize(self):  
        try:  
            pid = os.fork()    #第一次fork，生成子进程，脱离父进程  
            if pid > 0:  
                sys.exit(0)      #退出主进程  
        except OSError, e:  
            sys.stderr.write('fork #1 failed: %d (%s)\n' % (e.errno, e.strerror))  
            sys.exit(1)  

        os.chdir("/")      #修改工作目录  
        os.setsid()        #设置新的会话连接  
        os.umask(0)        #重新设置文件创建权限  

        try:  
            pid = os.fork() #第二次fork，禁止进程打开终端  
            if pid > 0:  
                sys.exit(0)  
        except OSError, e:  
            sys.stderr.write('fork #2 failed: %d (%s)\n' % (e.errno, e.strerror))  
            sys.exit(1)  

        #重定向文件描述符  
        sys.stdout.flush()  
        sys.stderr.flush()  
        si = file(self.stdin, 'r')  
        so = file(self.stdout, 'a+')  
        se = file(self.stderr, 'a+', 0)  
        os.dup2(si.fileno(), sys.stdin.fileno())  
        os.dup2(so.fileno(), sys.stdout.fileno())  
        os.dup2(se.fileno(), sys.stderr.fileno())  

       #注册退出函数，根据文件pid判断是否存在进程  
        atexit.register(self.delpid)  
        pid = str(os.getpid())  
        file(self.pidfile,'w+').write('%s\n' % pid)  

    def delpid(self):  
        os.remove(self.pidfile)  

    def start(self):  
            #检查pid文件是否存在以探测是否存在进程  
        try:  
            pf = file(self.pidfile,'r')  
            pid = int(pf.read().strip())  
            pf.close()  
        except IOError:  
            pid = None  

        if pid:  
            message = 'pidfile %s already exist. Daemon already running!\n'  
            sys.stderr.write(message % self.pidfile)  
            sys.exit(1)  

        #启动监控  
        self._daemonize()  
        self._run()  

    def stop(self):  
        #从pid文件中获取pid  
        try:  
            pf = file(self.pidfile,'r')  
            pid = int(pf.read().strip())  
            pf.close()  
        except IOError:  
            pid = None  

        if not pid:   #重启不报错  
            message = 'pidfile %s does not exist. Daemon not running!\n'  
            sys.stderr.write(message % self.pidfile)  
            return  

        #杀进程  
        remoteDic = confdeal.getConfRemote(self.scriptPath)                
        if remoteDic:
            ret = os.popen('netstat -antup | grep \":'+str(remoteDic['localPort'])+' \"')
            strList =  list(set(ret.read().split('\n')))
            for pidStr in strList:
                if pidStr != '':
                    pidStr = pidStr.split('/')[0]
                    pidStr = pidStr[pidStr.rfind(' ')+1:]
                    os.system("kill "+pidStr)
                
        try:     
            while 1:            
                os.kill(pid, SIGTERM)  
                time.sleep(0.1)  
                #os.system('hadoop-daemon.sh stop datanode')  
                #os.system('hadoop-daemon.sh stop tasktracker')  
                #os.remove(self.pidfile)  
                
        except OSError, err:  
            err = str(err)  
            if err.find('No such process') > 0:  
                if os.path.exists(self.pidfile):  
                    os.remove(self.pidfile)  
            else:  
                print str(err)  
                sys.exit(1)  

    def restart(self):  
        self.stop()  
        self.start()  

    def _run(self):       
        cmd = 'cd ' + self.scriptPath +' && python promain.py'
        child = subprocess.Popen(cmd, shell=True)
        while 1:
            if child.poll()==1:
                child = subprocess.Popen(cmd, shell=True)
            time.sleep(10)

if __name__ == '__main__':  
    scriptPath = os.path.dirname(os.path.realpath(__file__))
    daemon = Daemon(scriptPath,'/tmp/watch_process.pid', stdout = '/tmp/watch_stdout.log')  
    if len(sys.argv) == 2:  
        if 'start' == sys.argv[1]:  
            daemon.start()  
        elif 'stop' == sys.argv[1]:  
            daemon.stop()  
        elif 'restart' == sys.argv[1]:  
            daemon.restart()  
        else:  
            print 'unknown command'  
            sys.exit(2)  
        sys.exit(0)  
    else:  
        print 'usage: %s start|stop|restart' % sys.argv[0]  
        sys.exit(2)  



