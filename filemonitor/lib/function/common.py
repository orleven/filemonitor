#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'

import time
import datetime
import hashlib
from lib.special import special
# 替换dic里的部分字符
def dicStringReplace(dic,original,afterwards):
    for i in dic.keys():
        if isinstance(dic[i],list):
            for j in range(0,len(dic[i])) :
                if isinstance(dic[i][j],basestring):
                    dic[i][j] = dic[i][j].replace(original,afterwards)
        elif isinstance(dic[i],basestring):
            dic[i] = dic[i].replace(original,afterwards)


#返回当前时间
def getNowTime():
    return time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))

def dateDiffInSeconds(date1, date2):
    if date1 ==None:
        import sys
        return sys.maxint
    date1=datetime.datetime.strptime(date1, "%Y-%m-%d %H:%M:%S")
    date2=datetime.datetime.strptime(date2, "%Y-%m-%d %H:%M:%S")
    timedelta = date2 - date1
    return timedelta.days*24*3600 + timedelta.seconds

def getRandom():
    return getMd5(getNowTime())

def getMd5(str):
    return hashlib.md5(str).hexdigest()[0:16]

#  对比2个文件字符串 hash 是否相同
def compareFileStr(str1,str2):
    str1md5=hashlib.md5(str1).hexdigest()
    str2md5=hashlib.md5(str2).hexdigest()
    if str2md5 == str1md5:
        return True
    return False

#  对比2个文件夹 hash 是否相同
def compareFoldStr(str1,str2):
    str1md5=hashlib.md5(special.coding(str1.split('\\')[-1])).hexdigest()[0:16]
    str2md5=str2
    if str2md5 == str1md5:
        return True
    print str1md5,str2md5
    print str1.split('\\')[-1]
    return False
