#!/usr/bin/python

import os
import sys
import re
from glob import *
from Utils import *
from UserInfo import *
from Config import *
from AllProjectNewAlm import *
import xlrd
from pyExcelerator import *
from ftplib import *
from commands import *

class project(AllProjectNewAlm):
	def __init__(self):
		self.conf=Config()

	def initConfFromXls(self, conf):
		print "init conf from xls"
		## get version from here if bigversion
		versionStr = conf.getConf('version', 'Version number {([0-9A-Z]{3,4}|[0-9A-Z]{3,4}-[0-9A-Z]{1}-[A-Z]{2})$}')

		self.ProjectConfig = commands.getoutput('/local/int_jenkins/bin/MT6572_X_GetVerInfo '+ versionStr[0:3]+'X -All').split('\n')
		argvList = []
		argvList.extend(['-projectupper', self.ProjectConfig[1].strip().upper()])
		argvList.extend(['-officelist', self.ProjectConfig[4].strip()])
		argvList.extend(['-Spmlist',self.ProjectConfig[21].strip()])
		#argvList.extend(['-googletesttitle',self.ProjectConfig[22].strip()])
		argvList.extend(['-owner','yan.xiong_zhongshuang'])
		conf.addFromArg(argvList)
		print conf.dumpConfPretty()

	def getPlatform(self):
		return 'androidL'

	def getMailList(self,conf):
		version = self.getVersion(conf)
		toList =  conf.getConf('officelist','if not mail list,pls input')
		#toList = ['<xueqin.zhang@tcl.com>']
		return toList




	


