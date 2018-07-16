#!/usr/bin/python

############################################################################
## Change Utils for get changelist message.
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
		versionStr = conf.getConf('version', 'Version number {([0-9A-Z]{3,4}|[0-9A-Z]{3,4}-[0-9A-Z]{1}-[A-Z]{2})$}')
                tempdir = tempfile.mkdtemp('SuperSpam', 'temp', '/tmp')
                docmd('mkdir %s/image' % tempdir)
		docmd('mkdir %s/attach' % tempdir)
		tempdir = conf.getConf('tempdir','tmp path', tempdir)#open by lyf
		## if version
		if(versionStr[2] >= 'U' #and not versionStr.__contains__('-')):
			BAND = conf.getConf('BAND', 'which BAND version to deliver? <CN|EU|EU1|EU2|US0|US1|US2|2M|AWS|2G|LATAM3G|LATAM2G>')
		ProjectConfig = commands.getoutput('/local/int_jenkins/bin/MT6572_X_GetVerInfo '+ versionStr[0:3]+'X -All').split('\n')
		argvList = []
		argvList.extend(['-projbuildroot', '/local/build/%s-release/' % conf.getConf('project', 'project name')])
		argvList.extend(['-officelist', ProjectConfig[4].strip()])
		argvList.extend(['-Dailylist', ProjectConfig[5].strip().lower()])
		argvList.extend(['-minilist', ProjectConfig[17].strip().lower()])
		argvList.extend(['-manifestprefix', 'int/%s/'%ProjectConfig[1].strip().lower()])
		argvList.extend(['-prlistprojname', ProjectConfig[1].strip()])
		argvList.extend(['-releasenoteprojname', ProjectConfig[1].strip()])
		argvList.extend(['-custstorepath', ProjectConfig[7].strip()])
		argvList.extend(['-checklist.projname', ProjectConfig[1].strip()])
		argvList.extend(['-bugzillaproductid', ProjectConfig[6].strip()[3:]])
		argvList.extend(['-projbugbranch',ProjectConfig[10].strip()])
		argvList.extend(['-delivtitle',ProjectConfig[3].strip()])
		argvList.extend(['-versionX',ProjectConfig[0].strip()]) 
		argvList.extend(['-DirverList',ProjectConfig[20].strip()])
		argvList.extend(['-tempdir',tempdir])
		conf.addFromArg(argvList)
		print conf.dumpConfPretty()



conf = Config();
cutils= ChangeUtils();
## get all args from commands
conf.addFromArg(sys.argv[1:])
initConfFromXls(conf);
cutils.getChangeList(conf)
DirverList = conf.getConf('DirverList', 'DirverList mail')
#docmd('rm -rf %s' % conf.getConf('tempdir', 'tempdir'))

