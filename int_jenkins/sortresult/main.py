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
	print sys.argv[1:]
	print "test for jianbo.deng for martell..."

	conf.addFromArg(sys.argv[1:])
	print "test for argv ..... martell jianbo.deng"
	print sys.argv[1:]
	user = conf.getConf('user', 'User name')

	info = UserInfo()
	info.initUserInfo(user)

	projname = conf.getConf('project', 'Project name')
	conf.loadConfigFromFile(os.path.dirname(__file__)+'/conf/'+projname+'.conf')

	print "show projname for test"
	print projname
	projMod = __import__('projects.'+projname, globals(), locals(), '*')
	proj = projMod.project()
	#sys.exit(1)
	##AllProjects.py
	try:
		proj.run()
	finally:
		proj.cleanup()

if __name__ == '__main__':
	main()
