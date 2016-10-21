#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'

import os
from lib.core import datahandle
from lib.special import special 
def sessionToFile(target,path):
    try:
        import cPickle as pickle
    except:
        import pickle
    with open(path,'wb') as f:
        text = pickle.dumps(target)
        dh = datahandle.DataHandle()
        textEncode = dh.ecrypt(text)
        f.write(textEncode)
    return True

def sessionFromFile(path):
    try:
        import cPickle as pickle
    except:
        import pickle
    with open(path,'rb') as f:
        textEncode = f.read()
        dh = datahandle.DataHandle()
        textDecode = dh.decrypt(textEncode)
        target = pickle.loads(textDecode)
    return target

def setSession(sessionPath,sessionDic):
    sessionToFile(sessionDic,os.sep.join([sessionPath,sessionDic['sessionName']]))


def getSession(targetPath):
    pList = os.listdir(targetPath)
    pList.sort()
    monitorList = []
    for i in pList:                                #遍历目录
        filePath = os.sep.join([targetPath,i])
        try:
            sessionDic = sessionFromFile(filePath)
            command = sessionDic['command']
            mode = sessionDic['mode']
            projectPath = sessionDic['targetPath']
            whiteList = sessionDic['whiteList']
            blackList = sessionDic['blackList']
            sessionName = sessionDic['sessionName']
            projectName = sessionDic['projectName']
            flagName = sessionDic['flagName']
            sessionDic = agrDeal(command,projectPath,mode,0,whiteList,blackList)
            sessionDic['sessionName'] = sessionName
            sessionDic['projectName'] = projectName
            sessionDic['flagName'] = flagName
            if sessionDic:
                flag = 1
                for j in xrange(0,len(monitorList)):
                    if monitorList[j]['targetPath'] == projectPath:
                        flag = 0
                if flag:
                    monitorList.append(sessionDic)
        except:
            pass
    return monitorList

def agrDeal(command,projectPath,mode = None,doBak = 0 ,whiteList = None,blackList = None,):
    try:
        if command in ['start','scan','stop','getPath','getWhitePath']:
            slash , bslash = special.getSlash()
            projectPath = projectPath.replace(bslash,slash)
            if os.path.exists(projectPath):
                if mode != None and mode not in ['safe','human']:
                    return False
                if doBak not in [1,0]:
                    return False
                if whiteList != None:
                    for i in whiteList:
                        if not os.path.exists(i):
                            whiteList.remove(i)
                if blackList != None:
                    while '' in blackList:
                        blackList.remove('')
            else:
                return False
        else:
            return False
        return {'command':command,'targetPath':projectPath,'mode':mode,'doBak':doBak,'whiteList':whiteList,'blackList':blackList,}
    except:
        return False


