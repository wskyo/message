#!/usr/bin/python

############################################################################
## Interface be user to create common method and sample implemention for it.
## if you will user this class method, pls implement it
## add by xueqin.zhang for autocts 2016-03-25
############################################################################

import sys
import os
import re
from Utils import *
from Config import *
from UserInfo import *

class InterfaceUtils:

	def initConfFromXls(self, conf):
		return True

	def initSomeConf(self, conf):
		version = self.getVersion(conf)
		self.mailSubject(conf)
		pmDict = readFile('#','/local/int_jenkins/autocts/conf/common.conf')
		if pmDict.keys().__contains__('fullname'):
			conf.getConf('fullname', 'full name', pmDict['fullname'])
		if pmDict.keys().__contains__('defultmail'):
			conf.getConf('defultmail', 'defult mail', pmDict['defultmail'])
		if pmDict.keys().__contains__('tell'):
			conf.getConf('tell', 'Tell', pmDict['tell'])
		if pmDict.keys().__contains__('smtpserver'):
			conf.getConf('smtpserver', 'smtp server', pmDict['smtpserver'])

		print pmDict
		
	def getVersion(self, conf):
		versionStr = conf.getConf('version', 'Version number {([0-9A-Z]{3,4}|[0-9A-Z]{3,4}-[0-9A-Z]{1}-[A-Z]{2})$}')
		return versionStr

	def getTestType(self, conf):
		testtype = conf.getConf('testtype', 'Test Type').upper()
		return testtype


	def getResultRootPath(self, conf):
		testtype = conf.getConf('testtype', 'Test Type').upper()
		if testtype == 'CTS':
			resultRootPath = '/local/%s/tools/android-cts/repository/' % self.getPlatform()
		elif testtype == 'GTS':
			resultRootPath = '/local/androidM/tools/android-xts/repository/'	
		else:
			print 'test'
		return resultRootPath


	def getMailList(self,conf):
		return 'mail list'

	## get Mail Subject
	def mailSubject(self, conf):
		version = conf.getConf('version', 'Version number {^\w\w\w-\w$}')
		testtype = conf.getConf('testtype', 'Test Type').upper()
		googleversion = conf.getConf('googleversion', 'Test Type').upper()
		persoversion = conf.getConf('persoversion', 'Test Type').upper()
		projectName = conf.getConf('project', 'Project name in check list file name').upper()
		#mailTitle = (conf.getConf('googletesttitle', 'Google Test Title').strip())%(testtype, googleversion, version, persoversion, testtype)
		mailTitle = '[%s Test Result][%s][Emergency] %s v%s+%s %s' %(testtype, googleversion, projectName, version, persoversion, testtype)
		return conf.getConf('mailsubject', 'Mail subject', mailTitle)



