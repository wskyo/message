#!/usr/bin/python

############################################################################
## Interface be user to create common method and sample implemention for it.
## if you will user this class method, pls implement it
## add by jianbo.deng for superspam 2013-08-27
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
		pmDict = readFile('#','/local/int_jenkins/checklunch/conf/common.conf')
		##info = UserInfo()
		if pmDict.keys().__contains__('fullname'):
			conf.getConf('fullname', 'full name', pmDict['fullname'])
		if pmDict.keys().__contains__('defultmail'):
			conf.getConf('defultmail', 'defult mail', pmDict['defultmail'])
		if pmDict.keys().__contains__('tell'):
			conf.getConf('tell', 'Tell', pmDict['tell'])
		if pmDict.keys().__contains__('smtpserver'):
			conf.getConf('smtpserver', 'smtp server', pmDict['smtpserver'])
		if pmDict.keys().__contains__('intlist'):
			conf.getConf('intlist', 'int list', pmDict['intlist'])

		print pmDict
		
	def getVersion(self, conf):
		versionStr = conf.getConf('version', 'Version number {([0-9A-Z]{3,4}|[0-9A-Z]{3,4}-[0-9A-Z]{1}-[A-Z]{2})$}')
		#modify by renzhi 2015-3-6
		#return versionStr[:-2] if versionStr[-1] == '0' else versionStr
		return versionStr

	def getBase(self, conf):
		baseStr = conf.getConf('baseversion', 'Base version number {([0-9A-Z]{3,4}|[0-9A-Z]{3,4}-[0-9A-Z]{1}-[A-Z]{2})$}')
		return baseStr[:-2] if baseStr[-1] == '0' else baseStr

	def getBranch(self, conf):
		return conf.getConf('projbugbranch', 'project bugzille branch', 'TBD')
	
	def getManifestPrefix(self, conf):
		return conf.getConf('manifestprefix', 'Prefix dir for manifest files (int/xxx)')

	def getCurManifestFile(self, conf):
		return 'v%s.xml' % conf.getConf('version', 'current version')

	def getBaseManifestFile(self, conf):
		return 'v%s.xml' % conf.getConf('baseversion', 'base version')

	## big version for example 2A9C, but if version index '-' is small version
	## if you have other rule pls override this method
	def isBigVersion(self, version):
                if version[2] < 'N' and not version.__contains__('-'):
			return 'yes'
		else:
			return 'no'
               	
	## defualt mini version is after U 
	## example 2AVC
	def isMiniVersion(self, version):
                if version[2] >= 'N' and not version.__contains__('-'):
			return 'yes'
                else:
			return 'no'
		
	def isDailyVersion(self, version):
		if version.__contains__('-'):
			return 'yes'
		else:
			return 'no'

	def preLoad(self, conf):
		nameRule = self.getNameRule()
		docmd('cp /local/int_jenkins/INT_DOC/Name_Rule/%s %s/attach' % (nameRule, self.tempdir))
		return True
        #add by zhaoshie 
	def loadcompilelog(self, conf):
		version = conf.getConf('version', 'project current version')
		projectName = conf.getConf('project', 'Project name in check list file name')
                if projectName == 'pixi3-4':
		      docmd( 'zip %s/attach/android_log.zip /local/build/%s-release/v%s/out/target/product/pixi3_4_android.log ' % (self.tempdir,projectName,version))
                elif projectName == 'pixi3-45':
		      docmd( 'zip %s/attach/android_log.zip /local/build/%s-release/v%s/out/target/product/pixi3_45_android.log ' % (self.tempdir,projectName,version))
                elif projectName == 'yarisl':
                      docmd( 'zip %s/attach/android_log.zip /local/build/%s-release/v%s/out/target/product/%s_android.log ' % (self.tempdir,projectName,version,projectName))                      
                else:
		      docmd( 'zip %s/attach/android_log.zip /local/build/%s-release/v%s/android.log ' % (self.tempdir,projectName,version))
		return True

	def getNameRule(self):
		return 'DEFULT_NAMING_RULE_*.xls'

	def getOfficList(self, conf):
		return conf.getConf('officelist', 'Send to').strip()

	def getMiniList(self, conf):
		return conf.getConf('minilist', 'mini send to').strip()

	def getDailyList(self, conf):
		return conf.getConf('Dailylist', 'Daily send to').strip()

	def getBugzillaProduct(self, conf):
		return re.findall('[^,]+', conf.getConf('bugzillaproductid', 'Product id in bugzilla'))

	def postLoad(self, conf):
		return true

	def getTelewebVersion(self, conf):
		return conf.getConf('telewebversion', 'download teleweb version', 'MTK_SP 3.7.0')

	def getBuildModemVersion(self, conf):
		return conf.getConf('modemversion', 'modem version', self.getModemVersion(self.getVersion(conf)))

	def getModemVersion(self, version):
		return 'no modem version'

	def getMailList(self,conf):
		return 'mail list'

	## get Mail Subject
	def mailSubject(self, conf):
		version = conf.getConf('version', 'Version number {^\w\w\w-\w$}')
                projectName = conf.getConf('project', 'Project name in check list file name')
		if self.isMiniVersion(version) == 'yes' and projectName == 'yarisl' :
	                ## zhaoshie add for SZ mini version
 			if version.__contains__('_'):    	
				mailTitle = (conf.getConf('delivtitle', 'Deliv Title').strip())%version   
  			else:
				BAND = conf.getConf('BAND', 'which BAND version to deliver? <CN|EU|US|2G|LATAM3G|LATAM2G>')
				mailTitle = (conf.getConf('delivtitle', 'Deliv Title').strip())%(version, BAND)
		else:
			mailTitle = (conf.getConf('delivtitle', 'Deliv Title').strip())%version
		##mailTitle += ' Delivery'
		##print "mail subject mailTitle %s" %mailTitle
		return conf.getConf('mailsubject', 'Mail subject', mailTitle)

	def uploadImgFTP(self,conf):
		return True
