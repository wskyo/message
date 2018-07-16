#!/usr/bin/python

############################################################################
## Change Utils for get changelist message.AppverList
## add by jianbo.deng for superspam create 2013-08-27
###########################################################################

import sys
import os
import re
import commands
import xml.dom.minidom
import tempfile
from Utils import *
from Config import *
from UserInfo import *
from ChangeUtils import *
import glob
from commands import *

#-manifestprefix -version 

#  python GetChangeList.py -project twin -version 2CU8 -baseversion 2CU7 -BAND EU1 -fullname twin


def initConfFromXls(conf):
		print "init conf from xls"
		## get version from here if bigversion
		######versionStr = conf.getConf('version', 'Version number {([0-9A-Z]{3,4}|[0-9A-Z]{3,4}-[0-9A-Z]{1}-[A-Z]{2})$}')
                tempdir = tempfile.mkdtemp('SuperSpam', 'temp', '/tmp')
                docmd('mkdir %s/image' % tempdir)
		docmd('mkdir %s/attach' % tempdir)
		tempdir = conf.getConf('tempdir','tmp path', tempdir)#open by lyf
		## if version	
		argvList = []
		#argvList.extend(['-projbuildroot', '/local/build/%s-release/' % conf.getConf('appname', 'APK name')])
		#argvList.extend(['-releasenoteprojname', '%s-ReleaseNote' % self.appname])

		argvList.extend(['-AppList',ProjectConfig[20].strip()])
		argvList.extend(['-tempdir',tempdir])
		conf.addFromArg(argvList)
		print conf.dumpConfPretty()



conf = Config();
cutils= ChangeUtils();
## get all args from commands
conf.addFromArg(sys.argv[1:])
initConfFromXls(conf);
cutils.getChangeList(conf)
AppList = conf.getConf('AppList', 'AppList mail')
docmd('rm -rf %s' % conf.getConf('tempdir', 'tempdir'))

