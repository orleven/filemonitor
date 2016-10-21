#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'
import ConfigParser
import os
import re

def initConf(scriptPath):
    if not os.path.exists(os.sep.join([scriptPath,'default.conf'])):
        with open(os.sep.join([scriptPath,'default.conf']), 'w') as f:
            pass

# 读取remote配置
def getConfRemote(scriptPath):
    iniFlag = False
    config = ConfigParser.ConfigParser()
    try:
        config.read(os.sep.join([scriptPath,'default.conf']))
        serverIP = config.get("Remote", "RemoteHost")
        serverPort = int(config.get("Remote", "RemotePort"))
        localIP = config.get("Remote", "LocalHost")
        localPort = int(config.get("Remote", "LocalPort"))
        p = re.compile("^((?:(2[0-4]\d)|(25[0-5])|([01]?\d\d?))\.){3}(?:(2[0-4]\d)|(255[0-5])|([01]?\d\d?))$")
        if p.match(serverIP) and p.match(localIP) and serverPort>=80 and serverPort<65535 and localPort>=1000 and localPort<65535:
            iniFlag=True
    except:
        return False
    if iniFlag:
        dic={"remoteHost":serverIP,"remotePort":serverPort,"localHost":localIP,"localPort":localPort}
        return dic
    else :
        return False

# 设置remote配置
def setConfRemote(scriptPath,serverIP='10.10.10.10',serverPort='8080',localIP='127.0.0.1',localPort='5001'):
    config = ConfigParser.ConfigParser()
    try:
        config.read(os.sep.join([scriptPath,'default.conf']))
        p = re.compile("^((?:(2[0-4]\d)|(25[0-5])|([01]?\d\d?))\.){3}(?:(2[0-4]\d)|(255[0-5])|([01]?\d\d?))$")
        if p.match(serverIP) and p.match(localIP) and int(serverPort)>=80 and int(serverPort)<65535 and int(localPort)>=1000 and int(localPort)<65535:
            config.remove_section("Remote")
            config.add_section("Remote")
            config.set("Remote", "RemoteHost", serverIP)
            config.set("Remote", "RemotePort", serverPort)
            config.set("Remote", "LocalHost", localIP)
            config.set("Remote", "LocalPort",localPort)
            config.write(open(os.sep.join([scriptPath,'default.conf']),"w"))
            return True
    except:
        config.remove_section("Remote")
    return False


# 设置heartbeats配置
def setConfHeartbeats(scriptPath,delayTime=60):
    config = ConfigParser.ConfigParser()
    try:
        config.read(os.sep.join([scriptPath,'default.conf']))
        if  int(delayTime)>=1 and int(delayTime)<=3600:
            config.remove_section("Heartbeats")
            config.add_section("Heartbeats")
            config.set("Heartbeats", "DelayTime", delayTime)
            config.write(open(os.sep.join([scriptPath,'default.conf']),"w"))
            return True
    except:
        config.remove_section("Heartbeats")
    return False

# 读取heartbeats配置
def getConfHeartbeats(scriptPath):
    iniFlag=False
    config = ConfigParser.ConfigParser()
    try:
        config.read(os.sep.join([scriptPath,'default.conf']))
        delayTime = int(config.get("Heartbeats", "delayTime"))
        if  int(delayTime)>=1 and int(delayTime)<=3600:
            iniFlag=True
    except:
        return False
    if iniFlag:
        dic={"delayTime":delayTime}
        return dic
    else :
        return False

def setConfPath(scriptPath):
    config = ConfigParser.ConfigParser()
    try:
        config.read(os.sep.join([scriptPath,'default.conf']))
        config.remove_section("Path")
        config.add_section("Path")
        config.set("Path", "SessionPath", os.sep.join([scriptPath,'session']))
        config.set("Path", "LogPath", os.sep.join([scriptPath,'log']))
        config.set("Path", "CashPath", os.sep.join([scriptPath,'cash']))
        config.set("Path", "BakPath", os.sep.join([scriptPath,'bak']))
        config.set("Path", "RarPath", os.sep.join([os.path.expanduser('~'),'.filemonitor']))
        config.write(open(os.sep.join([scriptPath,'default.conf']),"w"))
        return True
    except:
        config.remove_section("Path")
    return False

def getConfPath(scriptPath):
    iniFlag=False
    config = ConfigParser.ConfigParser()
    try:
        config.read(os.sep.join([scriptPath,'default.conf']))
        sessionPath = config.get("Path", "SessionPath")
        logPath = config.get("Path", "LogPath")
        cashPath = config.get("Path", "CashPath")
        bakPath = config.get("Path", "BakPath")
        rarPath = config.get("Path", "RarPath")
        iniFlag=True
    except:
        return False
    if iniFlag:
        dic={"sessionPath":sessionPath,"logPath":logPath,"cashPath":cashPath,"bakPath":bakPath,"rarPath":rarPath}
        return dic
    else :
        return False

def getConfFile(scriptPath):
    iniFlag=False
    config = ConfigParser.ConfigParser()
    try:
        config.read(os.sep.join([scriptPath,'default.conf']))
        fileSize = int(config.get("File", "FileSize"))
        iniFlag=True
    except:
        return False
    if iniFlag:
        dic={"fileSize":fileSize}
        return dic
    else :
        return False


def setConfFile(scriptPath,fileSize = 50):
    config = ConfigParser.ConfigParser()
    try:
        config.read(os.sep.join([scriptPath,'default.conf']))
        config.remove_section("File")
        config.add_section("File")
        config.set("File", "FileSize", int(fileSize))
        config.write(open(os.sep.join([scriptPath,'default.conf']),"w"))
        return True
    except:
        config.remove_section("File")
    return False