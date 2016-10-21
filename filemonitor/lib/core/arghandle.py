#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'

import argparse
from lib.function import confdeal


class ArgHandle:
    # 初始化程序
    def __init__(self,scriptPath):
        self.scriptPath = scriptPath
        self.flag = False
        self.parser = argparse.ArgumentParser(description="File Monitor Client 0.2")
        self.argSet()
        self.handle()

    # 程序的所需参数
    def argSet(self):
        self.parser.add_argument('-LHOST', metavar="Local Host",action="store",help='Local Host IP,e.g. 10.10.10.10',default = None)
        self.parser.add_argument('-LPORT', metavar="Local Port",action="store",help='Local Port,e.g. 5000',type=int, default = None)
        self.parser.add_argument('-RHOST', metavar="Remote Host",action="store",help='Remote Host IP,e.g. 10.21.11.21',default = None)
        self.parser.add_argument('-RPORT', metavar="Remote Port",action="store",help='Remote Port,e.g. 80', type=int,default = None)

    # 参数处理
    def handle(self):
        confdeal.initConf(self.scriptPath)
        args = self.parser.parse_args()

        # 有输入参数的情况：
        if args.LHOST != None or args.LPORT !=None or args.RHOST !=None or args.RPORT !=None :
            if confdeal.setConfRemote(self.scriptPath,args.RHOST,args.RPORT,args.LHOST,args.LPORT):
                remoteDic = {
                    'localHost': args.RHOST,
                    'localPort': args.RPORT,
                    'remoteHost': args.LHOST,
                    'remotePort': args.LPORT,
                }
                self.flag = True

        # 没输入参数 读取配置文件
        else:
            remoteDic = confdeal.getConfRemote(self.scriptPath)
            if  remoteDic :
                self.flag = True

         # 没有输入参数，又没有配置文件

    def getFlag(self):
        return self.flag





