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

TelewebApk = getoutput("ssh user@10.92.35.20 ls /var/www/data/CreativeApk/%s | grep '0' | sort | tail -1" % project)
match = re.match('.*\.(\d+)\.(\d+)$',TelewebApk)
lastversion = match.group(1)
if re.match('^000(\d)',lastversion):
	match = re.match('^000(\d)',lastversion)
	num = (int(match.group(1))+1)
	if num==10:
		curversion = "0010"
	else:
		curversion = ("000"+ "%s") % num

elif re.match('^00(\d\d)',lastversion):
	match = re.match('^00(\d\d)',lastversion)
	num = (int(match.group(1))+1)
	if num==100:
		curversion = "0100"
	else:
		curversion = ("00"+ "%s") % num

elif re.match('^0(\d\d\d)',lastversion):
	match = re.match('^0(\d\d\d)',lastversion)
	num = (int(match.group(1))+1)
	if num==1000:
		curversion = "1000"
	else:
		curversion = "0%s" % num

elif re.match('^(\d+)',lastversion):
	match = re.match('^(\d+)',lastversion)
	num = (int(match.group(1))+1)
	curversion = "%s" % num
NextTelewebApk = TelewebApk.replace(lastversion,curversion)

match = re.match('v(.*)',NextTelewebApk)
if match:
	NextTelewebApk = match.group(1)
	print NextTelewebApk.strip()
