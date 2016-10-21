#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'

import os
import zipfile
import zlib
import shutil
# 解压zip
def decomZip(inZip,outFold):
    try:
        filename = inZip #要解压的文件
        filedir = outFold  #解压后放入的目录
        r = zipfile.is_zipfile(filename)
        if r:
            fz = zipfile.ZipFile(filename,'r')
            for file in fz.namelist():
                fz.extract(file,filedir)
        else:
            print('This file is not zip file')
            return False
        return True
    except:
        return False
# 压缩成zip
def comZip(inFold,outZip):
    try:
        import zlib
        compression = zipfile.ZIP_DEFLATED
    except:
        compression = zipfile.ZIP_STORED
    path = inFold  #要进行压缩的文档目录
    start = path.rfind(os.sep) + 1
    filename = outZip #压缩后的文件名
    try:
        z = zipfile.ZipFile(filename,mode = "w",compression = compression)
        for dirpath,dirs,files in os.walk(path):
            for file in files:
                if file == filename or file == "zip.py":
                    continue
                # print(file)
                z_path = os.path.join(dirpath,file)
                z.write(z_path,z_path[start:])
        z.close()
    except:
        if z:
            z.close()
    return True


def splitFile(fromdir,targetName,todir,chunksize = 50):
    try:
        chunksize = int(chunksize)*1024*1024#default chunksize
        partnum = 0
        inputfile = open(fromdir+os.sep+targetName,'rb')#open the fromfile
        while 1:
            chunk = inputfile.read(chunksize)
            if not chunk:             #check the chunk is empty
                break
            partnum += 1
            filename = os.sep.join([todir,('part%02d_'%partnum)+targetName])
            fileobj = open(filename,'wb')#make partfile
            fileobj.write(chunk)         #write data into partfile
            fileobj.close()
        return partnum
    except:
        return False

def combFile(fromdir,targetName,todir):
    outfile = open(os.sep.join([todir,targetName]),'wb')
    files = os.listdir(fromdir) #list all the part files in the directory
    files.sort()                #sort part files to read in order
    for file in files:
        if targetName in file and 'part' in file:
            filepath = os.sep.join([fromdir,file])
            infile = open(filepath,'rb')
            data = infile.read()
            outfile.write(data)
            infile.close()
            os.remove(filepath)
    outfile.close()
    return True

# 获取目标压缩文件内容
def getZipContent(type,targetPath):
    if type == 'file':
        while True:
            with open(targetPath, 'rb') as inFile :
                decompress = zlib.decompressobj()
                data = inFile.read(1024)
                text = ''
                while data:
                    text += decompress.decompress(data)
                    data = inFile.read(1024)
                text += decompress.flush()
                return text
    elif type == 'fold':
        return targetPath.split(os.sep)[-1]

def decompress(inFile,outFile):
    text = getZipContent('file',inFile)
    with open(outFile,'wb')as outFile:
        outFile.write(text)

def putZipContent(targetPath):
    level=9
    with open(targetPath, 'rb') as inFile:
        compress = zlib.compressobj(level)              #压缩文件
        data = inFile.read(1024)
        text = ''
        while data:
            text += compress.compress(data)
            data = inFile.read(1024)
        text += compress.flush()
        return  text

def compress(inFile, ouFile):
    text = putZipContent(inFile)
    with open(ouFile, 'wb')as ouFile:
        ouFile.write(text)

def delete(targetPath):
    try:
        if os.path.exists(targetPath):                                     # 判断源文件是否存在，存在则删除
            if os.path.isdir(targetPath):
                shutil.rmtree(targetPath)
            elif os.path.isfile(targetPath):
                os.remove(targetPath)
        return True
    except:
        print "delete error !"
        return False


def  createFold(targetPath):
    temp = targetPath[:targetPath.rfind(os.sep)]
    if not os.path.exists(temp):
        createFold(temp)
        os.mkdir(temp)