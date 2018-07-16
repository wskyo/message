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
#from pyExcelerator import *
from ftplib import *
from commands import *

class project(AllProjectNewAlm):
	def __init__(self):
		self.conf=Config()

	def initConfFromXls(self, conf):
		print "init conf from xls"
		versionStr = conf.getConf('version', 'Version number {([0-9A-Z]{3,4}|[0-9A-Z]{3,4}-[0-9A-Z]{1}-[A-Z]{2})$}')
		self.ProjectConfig = commands.getoutput('/local/int_jenkins/bin/MT6580_X_GetVerInfo '+ versionStr[0:3]+'X -All').split('\n')
		argvList = []
		argvList.extend(['-projbuildroot', '/local/build/%s-release/' % self.conf.getConf('project', 'project name')])
		argvList.extend(['-officelist', self.ProjectConfig[4].strip()])
		argvList.extend(['-Dailylist', self.ProjectConfig[5].strip().lower()])
		argvList.extend(['-minilist', self.ProjectConfig[17].strip().lower()])
		argvList.extend(['-manifestprefix', 'int/%s/'%self.ProjectConfig[1].strip().lower()])
		argvList.extend(['-prlistprojname', self.ProjectConfig[1].strip()])
		argvList.extend(['-releasenoteprojname', self.ProjectConfig[1].strip()])
		argvList.extend(['-custstorepath', self.ProjectConfig[7].strip()])
		argvList.extend(['-checklist.projname', self.ProjectConfig[1].strip()])
		argvList.extend(['-bugzillaproductid', self.ProjectConfig[6].strip()[3:]])		
		argvList.extend(['-projbugbranch',self.ProjectConfig[10].strip()])
		argvList.extend(['-delivtitle',self.ProjectConfig[3].strip()])
		argvList.extend(['-versionX',self.ProjectConfig[0].strip()])
		argvList.extend(['-codebranch',self.ProjectConfig[2].strip()])
		argvList.extend(['-Spmlist',self.ProjectConfig[21].strip()])
		argvList.extend(['-owner','chunlei.hu_xiaoling.luo'])
		argvList.extend(['-mtkproject',self.ProjectConfig[9].strip()])
		argvList.extend(['-mtkBaseLine','alps-mp-m0.mp1-V2.34_jhz6580.we.tf.m'])
		conf.addFromArg(argvList)
		print conf.dumpConfPretty()


	def getPlatform(self):
		return 'androidM'

	def getProjectPlatform(self):
		return 'MT6580M'

	def getCtsProjectName(self,conf):
		return 'Pixi4-4 3G TF'

	def getMailList(self,conf):
		toList =  conf.getConf('intlist','if not mail list,pls input')
		#toList = 'xueqin.zhang@tcl.com'
		return toList

	def getSpmList(self):
		#Spmlist = 'xueqin.zhang@tcl.com'
		Spmlist = 'hui.shen@tcl.com'
		return Spmlist




	


