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

TelewebAppli = getoutput("ssh sl_hz_hran@10.92.32.26 ls /mfs/teleweb/%s/appli | grep %s | sort | tail -1" %(project, curVer[:3]))
print TelewebAppli[1:len(TelewebAppli)]
