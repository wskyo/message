#!/usr/bin/python

import os
import sys
import re
from commands import *
import glob
sys.path.append('/local/int_jenkins/lib')
from Utils import *
from Config import *

versionSequence = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

conf = Config()
conf.addFromArg(sys.argv[1:])

curVer = conf.getConf('cur', 'Current version {^[0-9A-Z]{3}-[1-9A-Z]$}')
project = conf.getConf('projectName', 'project name')
BAND = conf.getConf('BAND', 'BAND, like as EU,EU1,EU2,US0,US1,US2,US3,EU_DTV,US_DTV')

if project =='yarisl':
	project='YarisL'

#print curVer

if curVer[3] == '0':
	print 'Error: small version can not be 0'
	sys.exit(1)
subVer = versionSequence[versionSequence.index(curVer[3])-1]
#print subVer
if subVer == '0':
	print curVer[0:4]
else:
	TelewebMini = getoutput("ssh sl_hz_hran@10.92.32.26 ls /mfs/teleweb/%s/mini | grep %s | sort | tail -1" %(project, curVer[:3]))
if TelewebMini =='':
	TelewebMini=curVer
print TelewebMini[1:len(TelewebMini)]
