#!/usr/bin/python

import os
import sys
import re
import pexpect
import datetime

from Utils import *
from Config import *
from UserInfo import *

#/local/int_jenkins/bin/notice -user hudson.admin# -jobname pixi4-35_3g-black -buildurl 10.92.37.25 -buildnumber 30 -buildstate success -addr yinfang.lai@tcl.com -baseversion BL1D -blacksuffix perso
def main():
	conf = Config();
	### add args
	conf.addFromArg(sys.argv[1:])
	user = conf.getConf('user', 'User name')
	### set user info
	info = UserInfo()
	info.initUserInfo(user)
	### run project 
	#projname = conf.getConf('project', 'Project name')
	#conf.loadConfigFromFile(os.path.dirname(__file__)+'/conf/'+projname+'.conf')
        projname = "jrdcommon"
	projMod = __import__('projects.'+projname, globals(), locals(), '*')
	proj = projMod.project()

	try:
		proj.run()
	finally:
		proj.cleanup()

if __name__ == '__main__':
	main()
