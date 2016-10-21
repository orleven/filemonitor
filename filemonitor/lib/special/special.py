#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'

import platform
import sys

if  'Windows' in platform.system():
    from win32api import *
    from win32con import *
    def echo(str):
        print str.encode('gbk')

    def coding(str):
        return str.encode('gbk')

    def decoding(str):
        return str.decode('gbk')

    def getSlash():
        return '\\','/'

    def whatIsPlatform():
        return 'Windows'

    # 添加注册表,开机自启动
    def SetOpen(scriptPath):
        try:
            # 创建批处理命令，用于开机启动
            output = open(scriptPath+'\\main.bat', 'w')
            text='@echo off\ncd "'+scriptPath+'"\npython.exe "Main.py"'
            output.write(text)
            output.close()

            # 获取python路径
            pythonPath=sys.executable.replace('pythonw.exe','python.exe')

            # 添加开机启动的注册表
            subkey='SOFTWARE\Microsoft\\CurrentVersion\Run'
            key=RegOpenKey(HKEY_LOCAL_MACHINE,subkey,0,KEY_ALL_ACCESS)
            temp= '"'+scriptPath+'\\main.bat"'
            RegSetValueEx(key,'monitor',0,REG_SZ,temp)

            # 给python管理员权限
            subkey='Software\Microsoft\ NT\CurrentVersion\AppCompatFlags\Layers'
            key=RegOpenKey(HKEY_CURRENT_USER,subkey,0,KEY_ALL_ACCESS)
            temp= 'RUNASADMIN'
            RegSetValueEx(key,pythonPath,0,REG_SZ,temp)

        except:
            print "请用管理员的身份运行 ！".encode('gbk')


else :
    def echo(str):
        print str

    def coding(str):
        return str

    def decoding(str):
        return str

    def getSlash():
        return '/','\\'

    def whatIsPlatform():
        return 'Linux'

def pythonVersion():
    if sys.version_info >  (3, 0):
        return  True
    return False