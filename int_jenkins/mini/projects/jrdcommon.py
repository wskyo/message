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
		versionStr = conf.getConf('version', 'Version number {([0-9A-Z]{3,4}|[0-9A-Z]{3,4}-[0-9A-Z]{1}-[A-Z]{2})$}')
                tempdir = tempfile.mkdtemp('SuperSpam', 'temp', '/tmp')
                docmd('mkdir %s/image' % tempdir)
		docmd('mkdir %s/attach' % tempdir)
		tempdir = conf.getConf('tempdir','tmp path', tempdir)
		## if version
		if(versionStr[-2] >= 'U' and not versionStr.__contains__('-')):
			BAND = conf.getConf('BAND', 'which BAND version to deliver? <CN|EU1|EU2|US1|US2|2M|AWS|2G|LATAM3G|LATAM2G>')
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
		argvList.extend(['-Spmlist',ProjectConfig[21].strip()])
		argvList.extend(['-tempdir',tempdir])
		conf.addFromArg(argvList)
		print conf.dumpConfPretty()

	def moveDBtoTemp(self, conf):
		version = conf.getConf('version', 'current version')
		project = conf.getConf('project', 'project name')
                versionstr  = version
		if(version[2] >= 'U' and version.__contains__('_')):
			versionstr=version[0:4]
                BAND = conf.getConf('BAND', 'which BAND version to deliver? <CN|EU1|EU2|US1|US2|2M|AWS|2G|LATAM2G>')
		if( BAND[0:2] == 'EU'):
			BAND='EU'
		else:
			BAND='US'
		jobName = conf.getConf('jobname', 'job release name',project+'-release')
		releasedir='/local/release/%s/v%s' %(jobName,version)
		tempdir = conf.getConf('tempdir','tmp path')
		print  releasedir
		docmd('cp %s/O%s*.db %s/attach' %(releasedir,versionstr,tempdir))  
		docmd('cp %s/A%s*.db %s/attach' %(releasedir,versionstr,tempdir)) 	


