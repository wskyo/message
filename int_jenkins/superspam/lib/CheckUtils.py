#!/usr/bin/python

############################################################################
## MailUtils be user to create mail html and send mail to recipients.
## this class has mail head, body, foot, attach method for comment mail message.
## add by jianbo.deng for superspam create 2013-08-27
############################################################################

from pyExcelerator import *
import os
import sys
import re

class CheckUtils:

	### mini version test check list
	def mkMiniTestCheckList(self, conf):
		projName = conf.getConf('project', 'Project name in check list file name')
		itemDescFont = self.getCheckListColorFont(250, True, True, color=41)
		perso = conf.getConf('perso', 'Perso file name {[\w\.]+}')
		version = conf.getConf('version', 'current version')
		fullName = conf.getConf('fullName', 'full name')

		checkListConf = 'CheckList_%s_%s.conf' % (version, perso)
		if os.path.isfile(checkListConf):
			conf.loadConfigFromFile(checkListConf)
		workbook = Workbook()
		worksheet = workbook.add_sheet('INT_Release_Check_List')
		worksheet.write_merge(0, 1, 0, 7, 'SDD1 INT SW Version Delivery Check List', self.getCheckListFont(300, True, True))
		worksheet.write_merge(2, 3, 0, 7, '   Project Name:  %s                 Main Version: %s                  Perso: %s                  Releaser: %s' % (projName, version, perso, fullName), self.getCheckListFont(250, True))
		worksheet.write_merge(4, 5, 0, 1, 'Item', itemDescFont)
		worksheet.write_merge(4, 5, 2, 3, 'Description', itemDescFont)
		worksheet.write_merge(4, 5, 4, 5, 'Result', itemDescFont)
		worksheet.write_merge(4, 5, 6, 7, 'Comment', itemDescFont)
	
		self.lineNum = 5 
		self.doMiniTest(worksheet, conf, checkListConf)
	
		worksheet.col(0).width = 1250
		worksheet.col(1).width = 1250
		worksheet.col(2).width = 10000
		worksheet.col(3).width = 10000
		worksheet.col(4).width = 1500
		worksheet.col(5).width = 1500
		worksheet.col(6).width = 9000
		worksheet.col(7).width = 9000
	
		workbook.save('%s/attach/%s_SW_%s_Delivery_CheckList.xls' % (self.tempdir, projName, version))


	def doMiniTest(self, worksheet, conf, checkListConf):		
		self.doMiniTestAddFromProject(worksheet, conf, checkListConf)

	## override this method is you have other check
	def doMiniTestAddFromProject(self, worksheet, conf, checkListConf):
		return ''	

	def miniTestCheckItem(self, worksheet, conf, checkListConf, key, desc, desc2=None, merge=0):
		self.lineNum += 1
		worksheet.write_merge(self.lineNum, self.lineNum + merge, 0, 1, self.lineNum-5, self.getCheckListFont(250))
		if not desc2:
			desc2 = desc
		worksheet.write_merge(self.lineNum, self.lineNum + merge, 2, 3, desc2, self.getCheckListFont(250))
		res = conf.getConf(key, desc+' <ok|ko|na>', 'ok', ask=1, save=checkListConf)
		if res.upper() == 'OK':
			worksheet.write_merge(self.lineNum, self.lineNum + merge, 4, 5, res.upper(), self.getCheckListFont(250, bold=True, center=True))
			worksheet.write_merge(self.lineNum, self.lineNum + merge, 6, 7, '', self.getCheckListFont(250))
		elif res.upper() == 'NA':
			worksheet.write_merge(self.lineNum, self.lineNum + merge, 4, 5, res.upper(), self.getCheckListFont(250, bold=True, center=True, index=4))
			worksheet.write_merge(self.lineNum, self.lineNum + merge, 6, 7, '', self.getCheckListFont(250))
		else:
			worksheet.write_merge(self.lineNum, self.lineNum + merge, 4, 5, res.upper(), self.getCheckListFont(250, bold=True, center=True, index=10))
			comment = conf.getConf(key+'_ko_comment', 'Fail comment', save=checkListConf)
			worksheet.write_merge(self.lineNum, self.lineNum + merge, 6, 7, comment, self.getCheckListFont(250))
		self.lineNum += merge

	### mini version sw test check list
	def mkMiniSWCheckList(self, conf):
		projName = conf.getConf('project', 'Project name in check list file name')
		itemDescFont = self.getCheckListFont(250, True, True)
		version = conf.getConf('version', 'current version')
		checkListConf = 'miniCheckList_%s.conf' % version
		if os.path.isfile(checkListConf):
			conf.loadConfigFromFile(checkListConf)	
		workbook = Workbook()
		worksheet = workbook.add_sheet('MMI Test Result')
		worksheet.write_merge(0, 1, 0, 7, 'SW_MMI_test_Delivery_Checklist', self.getCheckListColorFont(300, True, True,color=41))
		titleFont = self.getCheckListColorFont(250, True, True,color=41)
		worksheet.write(2, 0, 'SW version', itemDescFont)
		worksheet.write(2, 1, version, itemDescFont)
		worksheet.write_merge(3, 3, 0, 7, 'AutoTest', titleFont)
		self.doMiniAutoTest(worksheet, conf, checkListConf)
		
		worksheet.write_merge(29, 29, 0, 7, 'ManuTest', titleFont)
		self.doMiniManuTest(worksheet, conf, checkListConf)
		
		worksheet.col(0).width = 9800
		worksheet.col(1).width = 3500
		worksheet.col(2).width = 3500
		worksheet.col(3).width = 3500
		worksheet.col(4).width = 3500
		worksheet.col(5).width = 3500
		worksheet.col(6).width = 3500
		worksheet.col(7).width = 3500
		workbook.save('%s/attach/%s_SW_MMI_test_%s_Delivery_CheckList.xls' % (self.tempdir, projName, version))

	def doMiniAutoTest(self, worksheet, conf, checkListConf):
		self.lineNum = 3
		MiniTestCase=['TRACABILITY', 'MISC', 'LCD MIRE', 'LCD BLACK', 'LCD GREYCHART', 'LCD WHITE', 'KEYPAD', 'BACKLIGHT Level', 'CAMERA LED', 'VIBRATOR', 'CAMERA IMG', 'CAMERA IMG FRONT', 'MELODY(Speaker/MIC loop/Sub MIC)', 'HEADSET', 'USB', 'GENSOR', 'COMPASS', 'ALS/PS', 'SIM', 'MEMORYCARD', 'BATTERY TEMP', 'BT', 'WIFI', 'GPS', 'CALL']
		for i in range(len(MiniTestCase)):
			self.miniSWCheckItem(worksheet, conf, checkListConf, 'AutoTest'+str(i+1), MiniTestCase[i])
	
	def doMiniManuTest(self, worksheet, conf, checkListConf):
		MiniTestCase=['TRACABILITY', 'MISC', 'LCD MIRE', 'LCD BLACK', 'LCD GREYCHART', 'LCD WHITE', 'KEYPAD', 'BACKLIGHT Level', 'CAMERA LED', 'VIBRATOR', 'CAMERA IMG', 'CAMERA IMG FRONT', 'MELODY(Speaker/MIC loop/Sub MIC)', 'HEADSET', 'USB', 'GENSOR', 'COMPASS', 'ALS/PS', 'SIM', 'MEMORYCARD', 'BATTERY TEMP', 'BT', 'WIFI', 'GPS', 'CALL']
		self.lineNum = len(MiniTestCase)+4
		for i in range(len(MiniTestCase)):
			self.miniSWCheckItem(worksheet, conf, checkListConf, 'ManuTest'+str(i+1), MiniTestCase[i])

	def miniSWCheckItem(self, worksheet, conf, checkListConf, key, desc, desc2=None, merge=0):
		self.lineNum += 1
		if not desc2:
			desc2 = desc
		worksheet.write(self.lineNum, 0, desc2, self.getCheckListFont(250,False,True))
		print self.lineNum
		res = conf.getConf(key, desc+' <ok|ko|na>', 'ok', ask=1, save=checkListConf)
		if res.upper() == 'OK':
			worksheet.write(self.lineNum, 1, res.upper(), self.getCheckListFont(250, bold=True, center=True))
		elif res.upper() == 'NA':
			worksheet.write(self.lineNum, 1, res.upper(), self.getCheckListFont(250, bold=True, center=True, index=4))
		else:
			worksheet.write(self.lineNum, 1, res.upper(), self.getCheckListFont(250, bold=True, center=True, index=10))
