#!/usr/bin/python

import os
import sys
import re
import glob
import commands
from Utils import *
from UserInfo import *
from Config import *
from AllProject import *

class project(AllProject):

	def initConfFromXls(self, conf):
		print "init conf from xls"
		## get version from here if bigversion		
                tempdir = tempfile.mkdtemp('SuperSpam', 'temp', '/tmp')
                docmd('mkdir %s/image' % tempdir)
		docmd('mkdir %s/attach' % tempdir)
		tempdir = conf.getConf('tempdir','tmp path', tempdir)
		## if version
		argvList = []
		###argvList.extend(['-projbuildroot', '/local/build/genericapp/%s' % conf.getConf('appname', 'appname name')])
		argvList.extend(['-tempdir',tempdir])
		conf.addFromArg(argvList)
		print conf.dumpConfPretty()



