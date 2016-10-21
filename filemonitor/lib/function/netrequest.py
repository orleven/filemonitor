#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'
import requests
import time
import os
from lib.function import filedeal
from lib.function import confdeal
from lib.special import  special

def post(remoteHost,remotePort,localHost,nowTime):
    try:
        r = requests.post("http://%s:%d/wzgl/monitor/hb" %(remoteHost,remotePort), data={'ip':localHost,'time':nowTime},timeout=3)
        text=r.text.strip()
        if 'success'  not in text :
        #   special.echo( "失去服务器连接 ！")   #  如果无法搜到服务器返回的200 信息，表示服务器丢失
            return False
        return True
    except:
    #  special.echo( "失去服务器连接 ！")
        return False


def sendInfo(remoteHost,remotePort,localHost,nowTime,info,level):
    try:
        r = requests.post("http://%s:%d/wzgl/monitor/postMsg" %(remoteHost,remotePort), data={'ip':localHost,'info':nowTime+'  '+info,'level':level},timeout=3)
        text=r.text.strip()
        if 'success' not in text :
    #   special.echo( "失去服务器连接 ！")    #  如果无法搜到服务器返回的200 信息，表示服务器丢失
            return False
        return True
    except:
    #  special.echo( "失去服务器连接 ！")
        return False

def downLoad(remoteHost,remotePort,path,fileName,isFlag):
    flag,partnum = 3,1
    while 1:
        try:
            if flag:
                if isFlag:
                    filename = fileName
                    filedir = os.sep.join([path,'download'])
                    filepath = os.sep.join([filedir, fileName])
                else:
                    filename = ('part%02d_'%partnum)+ fileName
                    filedir = os.sep.join([path,'download'])
                    filepath = os.sep.join([filedir,('part%02d_'%partnum)+ fileName])
                if _download(remoteHost,remotePort,filepath,filename):
                    if isFlag :
                        return True
                    else:
                        if os.path.getsize(filepath) < confdeal.getConfFile()['fileSize']*1024*1024:
                            if filedeal.combFile(os.sep.join([path,'download']),fileName,os.sep.join([path,'download'])):
                                return True
                        flag = 3
                else :
                    flag -= 1
                        # if filedeal.decomZip(os.sep.join([filedir, fileName]),ouPath):
                        #     special.echo("下载解压完成 ！ \n根据下载压缩文件进行检查 ！")
                        #     return True
                        # else:
                        #     special.echo("下载压缩文件出现问题 ！ ")
                        #     flag = 0
            else:
                special.echo("服务器请求失败 ！ \n根据原压缩文件进行检查 ！")
                # if not filedeal.decomZip(os.sep.join([path,'upload',fileName]),ouPath):
                #     special.echo("原压缩文件出现问题 ！ ")
                #     return False
                return False
        except:
            return False


def _download(remoteHost,remotePort,filepath,filename):
    try:
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'Accept-Encoding': 'gzip, deflate',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3'
        }
        r = requests.post('http://'+remoteHost+':'+remotePort+'/wzgl/monitor/download',data={'name':filename},headers=headers)
        with open(filepath,'wb') as f:
            f.write(r.content)
        return True
    except:
        special.echo("失去服务器连接 ！ 等待5秒 ...")
        time.sleep(5)
        return False

#文件上传
def upload(remoteHost,remotePort,path,fileName,isFlag):
    filedir = os.sep.join([path,'upload'])
    if not isFlag :
        partnum = 1;
        bakCount = filedeal.splitFile(filedir,fileName,filedir,50)
        if bakCount :
            while 1:
                try :
                    if _upload(remoteHost,remotePort,os.sep.join([filedir,('part%02d_'%partnum)+ fileName])):
                        os.remove(os.sep.join([filedir,('part%02d_'%partnum)+ fileName]))
                        if partnum == bakCount:
                            break
                        partnum += 1
                except:
                    time.sleep(10)
            special.echo("上传备份文件成功 ！")
    else:
        while 1:
            try :
                if _upload(remoteHost,remotePort,os.sep.join([filedir,fileName])):
                    os.remove(os.sep.join([filedir,fileName]))
            except:
                time.sleep(10)
        special.echo("上传备份文件成功 ！")
            # special.echo("失去服务器连接 ！ 等待10秒 ...")


def _upload(remoteHost,remotePort,filePath):
    f=open(filePath,'rb')
    fileName=filePath.split(os.sep)[-1]
    try:
        r = requests.post('http://'+remoteHost+':'+remotePort+'/wzgl/monitor/upload',data={'name':fileName},files ={'file':f})
        text=r.text.strip()
        if 'success' in text :
        #   special.echo( "失去服务器连接 ！")    #  如果无法搜到服务器返回的200 信息，表示服务器丢失
            return True
        return False
    except:
        return False