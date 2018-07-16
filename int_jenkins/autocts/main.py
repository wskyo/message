#!/usr/bin/python


import os
import sys
import re
import pexpect
import datetime
from Config import *
from Utils import *
from UserInfo import *

''' this class for auto googletest mail, it like main method.
    create by xueqin.zhang 2016-03-21 '''

def main():
	conf = Config();
	### add args
	conf.addFromArg(sys.argv[1:])
	print "test for auto test mail ....."
	print sys.argv[1:]
	user = conf.getConf('user', 'User name')
	### set user info
	info = UserInfo()
	info.initUserInfo(user)
	### run project 
	projname = conf.getConf('project', 'Project name')

	projMod = __import__('projects.'+projname, globals(), locals(), '*')
	proj = projMod.project()

	try:
		print 'START!'
		proj.run()
	finally:
		proj.cleanup()
		print 'finish!'

if __name__ == '__main__':
	main()
