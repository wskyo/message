#!/usr/bin/python

import os
import sys
import re
from commands import *
import glob
sys.path.append('/local/int_jenkins/lib')
from Utils import *
from Config import *

if sys.argv[1]=='-appname':
	project = sys.argv[2]

TelewebApk = getoutput("ssh sl_hz_hran@10.92.32.26 ls /mfs/teleweb/genericapp/%s | grep '0' | sort | tail -1" % project)

match = re.match('v(.*)',TelewebApk)
if match:
	TelewebApk = match.group(1)
	print TelewebApk.strip()
