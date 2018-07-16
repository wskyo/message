#!/usr/bin/python

import os
import sys
import re
import pexpect
import datetime

from Utils import *
from Config import *
from UserInfo import *

def main():
	conf = Config();
	### add args
	conf.addFromArg(sys.argv[1:])
	user = conf.getConf('user', 'User name')
	### set user info
	info = UserInfo()
	info.initUserInfo(user)
	### run project 
	projname = conf.getConf('project', 'Project name')
	conf.loadConfigFromFile(os.path.dirname(__file__)+'/conf/'+'jrdcommon.conf')
	projMod = __import__('projects.'+projname, globals(), locals(), '*')
	proj = projMod.project()

	try:
		proj.run()
	finally:
		proj.cleanup()

if __name__ == '__main__':
	main()
