#!/usr/bin/python

import os
import sys
import re
import pexpect
import datetime
from Utils import *
from Config import *
from UserInfo import *

###user for send email
def main():
	conf = Config();
	conf.addFromArg(sys.argv[1:])
	print "test for argv ....."
	print sys.argv[1:]
	user = conf.getConf('user', 'User name')

	info = UserInfo()
	info.initUserInfo(user)

	projname = conf.getConf('project', 'Project name')
	#conf.loadConfigFromFile(os.path.dirname(__file__)+'/conf/'+projname+'.conf')

	projMod = __import__('projects.'+projname, globals(), locals(), '*')
	proj = projMod.project()

	try:
		proj.run()
	finally:
		proj.cleanup()

if __name__ == '__main__':
	main()
