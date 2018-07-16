#!/usr/bin/python

import os
import sys
import re
from glob import *
from Utils import *
from UserInfo import *
from Config import *
from AllProjectNew import *
import xlrd
from pyExcelerator import *
from ftplib import *
from commands import *




class project(AllProjectNew):
	def __init__(self):
		self.conf=Config()
	

	def initConfFromXls(self, conf):
		print "init conf from xls"
		## get version from here if bigversion
		versionStr = conf.getConf('version', 'Version number {([0-9A-Z]{3,4}|[0-9A-Z]{3,4}-[0-9A-Z]{1}-[A-Z]{2})$}')
		## if version
		if(versionStr[-2] >= 'U' and not versionStr.__contains__('-')):
			self.BAND = conf.getConf('BAND', 'which BAND version to deliver? <CN|EU1|EU2|US1|US2|2M|AWS|2G|LATAM3G|LATAM2G>')
		self.ProjectConfig = commands.getoutput('/local/int_jenkins/bin/MT6572_X_GetVerInfo '+ versionStr[0:3]+'X -All').split('\n')
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
		conf.addFromArg(argvList)
		print conf.dumpConfPretty()

	#get mail list
	def getMailList(self,conf):
		version = self.getVersion(conf)
		## big version will send to office list
		if conf.getConf('isBigVersion','is big version <yes|no>') == 'yes':
			toList =  conf.getConf('officelist','if not mail list,pls input')
		## mini version will send to mini list
		elif conf.getConf('isMiniVersion', 'is mini version <yes|no>') == 'yes':
			toList = conf.getConf('minilist','if not mail list,pls input')
		## Daily version will send to Dialy list
		elif conf.getConf('isDailyVersion', 'is Daily version<yes|no>') == 'yes':
			toList = conf.getConf('Dailylist','if not mail list,pls input')
		else:
			toList = ['<shie.zhao@tcl.com>']
		return toList
	
	## name rule 
	def getNameRule(self):
		return 'Soul4-NAMING_RULE_v0.3.xls'
	
	## if you add other test case please input this method, flow example reboot
	def doMiniTestAddFromProject(self, worksheet, conf, checkListConf):
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'versioninfo', 'Use *#3228# to check version number and version info.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'outcall1', 'Make an outgoing call. Hangup by self phone. Check call log.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'outcall2', 'Make an outgoing call. Hangup by opposite side. Check call log.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'incall1', 'Make an incoming call. Hangup by self phone. Check call log and incoming ringtone.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'incall2', 'Make an incoming call. Hangup by opposite side. Check call log and incoming ringtone.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'ringtone', 'Change ringtone.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'sms', 'Send a sms to 10086 or 10010. Check the reply on notification bar.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'alarm', 'Set an alarm. Check it can work normally.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'contact', 'Create a contact, then delete it.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'takephoto', 'Take a photo by camera.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'usb', 'Connect USB. 1) Check USB charge. 2) Select "Mount" to check USB massive storage.', 'Connect USB.\n 1) Check USB charge.\n 2) Select "Mount" to check USB massive storage.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'inputmethod', 'Switch input method in any input box.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'flightmode', 'Switch normal mode/filght mode.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'musicplayer', 'Go to music player to check lauder speaker and whether phone can play music normally.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'aboutphone', 'Go to setting, check "about phone".')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'switchbt', 'Turn on/off BT.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'switchwifi', 'Turn on/off Wifi.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'gsensor', 'Go to message list, rotate the phone to check the display mode(portraint and landscape) with g-sensor.')
		self.miniTestCheckItem(worksheet, conf, checkListConf, 'reboot', 'Reboot the phone.')
		return
	
        ##update for modem version
	def getModemVersion(self, version):
		##beetlelite CU
		if(version[1:2] == '7' or version[1:2] == 'X'):
			return 'MT6572_S00_MOLY_WR8_W1315_MD_WG_MP_V1'
		else:###other beetlelite project
			return 'MT6572_S00_MOLY_WR8_W1315_MD_WG_MP_V1'

