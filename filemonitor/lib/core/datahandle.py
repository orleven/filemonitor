#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'leven'
import binascii
from Crypto.Cipher import DES
from base64 import b64encode, b64decode
class DataHandle:
    key = chr(64)+chr(48)+chr(82)+chr(108)+chr(51)+chr(118)+chr(101)+chr(78)
    iv = chr(11)+chr(22)+chr(33)+chr(44)+chr(55)+chr(66)+chr(77)+chr(88)
    def __init__(self,key='',iv=''):
        if len(key)> 0:
            self.key = key
        if len(iv)>0 :
            self.iv = iv

    def ecrypt(self,ecryptText):
        try:
            cipherX = DES.new(self.key, DES.MODE_CBC, self.iv)
            pad = 8 - len(ecryptText) % 8
            padStr = ""
            for i in range(pad):
                padStr = padStr + chr(pad)
            ecryptText = ecryptText + padStr
            x = cipherX.encrypt(ecryptText)
            return b64encode(binascii.a2b_hex(x.encode('hex_codec').upper()))
        except:
            return ""


    def decrypt(self,decryptText):
        try:
            decryptText = binascii.b2a_hex(b64decode(decryptText))
            cipherX = DES.new(self.key, DES.MODE_CBC, self.iv)
            str = decryptText.decode('hex_codec')
            y = cipherX.decrypt(str)
            return y[0:ord(y[len(y)-1])*-1]
        except:
            return ""