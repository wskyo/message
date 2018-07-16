#!/usr/bin/python

############################################################################
## Sheet Utils for create xls table.
## add by jianbo.deng for superspam create 2013-08-27
############################################################################

import re
import datetime
import commands

from ReleaseStyle import *
from pyExcelerator import *
from DBUtils import *
from DBUtilsALM import *
from Utils import *
from Config import *
from UserInfo import *
import copy

## xls table max column defualt is 12	

class SheetUtils:
	prVeriSWFromCodeInfoDict = {}
	prResolveFromCodeInfoDict = {}
	brotherBugsDict = {}
	clonedDefectOFPLF = {}
	notclonedDefectOFPLF = {}
	editCloneDefect = {}	
	projectBugIDs = []
	notClonedBugs = []
	maxColumn = 13
	curRow = 4


	def createReleaseNote(self, conf, SingleApkBugs):
		prVeriSWOldResolveInfoDict = {}
		prResolveFromBugzillaInfoDict = {}
		onGoingDefectTaskDict = {}
		self.projectBugIDs = []		
		workbook = Workbook()
		worksheet = workbook.add_sheet(self.appname)
		if 'Bugzilla' in self.AlmCheckDict[self.appname].values():
			mysqlConn = MySQLdb.connect('172.24.61.199', port=3306, user='scm_tools', passwd='SCM_TOOLS123!', db='bugs', charset='gbk')
		if conf != None:
			### step 1, create xls title
			self.createXlsTitle(conf, worksheet)
			### step 2 get current version release label create time and lase versin release label creaete time
			
			[tagcurversion,taglastversion] = self.tagDict[self.appname]
			pushdir(self.appname)
			lastVerTimeStr,curVerTimeStr = self.getCurrAndLaseTime(conf,tagcurversion,taglastversion)
			popdir()

			if self.appname in self.AlmCheckDict.keys():
				print self.AlmCheckDict[self.appname]
				if 'Bugzilla' in self.AlmCheckDict[self.appname].values():				
					oneProductIdNum	= self.AlmCheckDict[self.appname]['apkproject']			
					self.getSWAndRelPRList(conf, mysqlConn, curVerTimeStr, lastVerTimeStr)
					self.getVeriSWOldResolveInfoDict(self.mysqlConn, oneProductIdNum, prVeriSWOldResolveInfoDict, prResolveFromBugzillaInfoDict, curVerTimeStr, lastVerTimeStr)
				elif 'ALM' in self.AlmCheckDict[self.appname].values():
					oneProductIdNumALM = self.AlmCheckDict[self.appname]['apkproject']
					self.getSWAndRelPRListFromAlm(conf, curVerTimeStr, lastVerTimeStr,self.AlmCheckDict)
					self.getVeriSWOldResolveInfoDictALM(oneProductIdNumALM, prVeriSWOldResolveInfoDict, prResolveFromBugzillaInfoDict, curVerTimeStr, lastVerTimeStr,self.AlmCheckDict)
					self.getOnGoingDefectTask_of_Gapp(self.appname, onGoingDefectTaskDict)
				else:
					print "you have to make sure %s is alm or bugzilla in conf" % self.appname
					exit(1)

			### step 3 create PR SW and RESOLVED PR list
			if self.appname == 'JrdFileManager':
				self.bugzillaAppName = 'FileManager'
				self.bugzillaAppNameTwo =  'File Manager'			
			elif self.appname == 'JrdLauncher':
				self.bugzillaAppName = 'JrdLauncher'
				self.bugzillaAppNameTwo = 'Jrd Launcher'
			elif self.appname == 'OTBackup':
				self.bugzillaAppName = 'CloudBackup' 
				self.bugzillaAppNameTwo = 'Cloud Backup'
			elif self.appname == 'JrdWifiTransfer':
				self.bugzillaAppName = 'WiFiTransfer'
				self.bugzillaAppNameTwo = 'WiFi Transfer'
			elif self.appname == 'JrdSoundRecord':
				self.bugzillaAppName = 'SoundRecorder' 
				self.bugzillaAppNameTwo = 'Sound Recorder'
			else:
				self.bugzillaAppName = self.appname
				self.bugzillaAppNameTwo = self.appname					

			if 'Bugzilla' in self.AlmCheckDict[self.appname].values():				
				self.deliverPRlist(conf, mysqlConn, prVeriSWOldResolveInfoDict,prResolveFromBugzillaInfoDict)
			elif 'ALM' in self.AlmCheckDict[self.appname].values():
				self.deliverPRlistALM(conf, None, prVeriSWOldResolveInfoDict,prResolveFromBugzillaInfoDict)		
			### step 4 create release note

			self.createReleaseNotePRCode(worksheet,SingleApkBugs,onGoingDefectTaskDict)
			self.createBrotherBugReleaseNote(conf,workbook,curVerTimeStr, lastVerTimeStr)
		##return worksheet
		else:
			print "conf is None will exit(0)!"
			sys.exit(0)
		workbook.save('%s/attach/APK_ReleaseNote_%s_%s.xls' % (self.tempdir,self.appname, self.version))
                #docmd('cp %s/attach/APK_ReleaseNote_%s_%s.xls /tmp/' % (self.tempdir, self.appname, self.version))
		if self.AlmCheckDict[self.appname]['creative_apk'].strip() == 'yes':
			docmd('scp -r %s/attach/APK_ReleaseNote_%s_%s.xls user@10.92.35.20:/var/www/data/CreativeApk/%s/v%s/APK_ReleaseNote_%s_%s.xls' % (self.tempdir,self.appname,self.version,self.appname,self.version,self.appname,self.version))
		else:
			docmd('scp -r %s/attach/APK_ReleaseNote_%s_%s.xls user@10.92.35.20:/var/www/data/genericapp/%s/v%s/APK_ReleaseNote_%s_%s.xls' % (self.tempdir,self.appname,self.version,self.appname,self.version,self.appname,self.version))
		if self.appPlfDict:
			if self.AlmCheckDict[self.appname]['creative_apk'].strip() != 'yes':
				self.copyPlfToTestDir(self.appname, self.version)


	def createBrotherBugReleaseNote(self,conf,workbook,curVerTimeStr, lastVerTimeStr):		
		self.maxColumn = 13
		curRow = 0
		brotherBug = "Clone_bugs"
		worksheet = workbook.add_sheet(brotherBug)
		styleBodyInfoStyle = self.getBodyInfoStyle()
		styleBodyInfoStyleMan = self.getBodyInfoStyle(20)
		styleBodyTitleStyle = self.getBodyTitleStyle()
		styleReleaseNoteTitleStyle5 = self.getReleaseNoteTitleStyle(5)	
		worksheet.write_merge(curRow, curRow, 0, self.maxColumn, 'Clone Defect/Task OF Projects', styleReleaseNoteTitleStyle5)
		curRow += 1
		worksheet.write(curRow, 0, 'NO', styleBodyTitleStyle)
		worksheet.write(curRow, 1, 'Generic-BUG-ID', styleBodyTitleStyle)
		worksheet.write(curRow, 2, 'Project-BUG-ID', styleBodyTitleStyle)
		worksheet.write(curRow, 3, 'PR/CR/FR', styleBodyTitleStyle)
		worksheet.write(curRow, 4, 'PR-STATUS', styleBodyTitleStyle)
		worksheet.write(curRow, 5, 'REPORTER', styleBodyTitleStyle)
		worksheet.write(curRow, 6, 'Project-name', styleBodyTitleStyle)
		worksheet.write(curRow, 7, 'PRIORITY', styleBodyTitleStyle)
		worksheet.write(curRow, 8, 'IPR', styleBodyTitleStyle)			
		worksheet.write(curRow, 9, 'FUNCTION', styleBodyTitleStyle)
		worksheet.write_merge(curRow, curRow, 10, 11, 'SHORT-DESC', styleBodyTitleStyle)
		worksheet.write(curRow, 12, 'DEADLINE', styleBodyTitleStyle)
		worksheet.write(curRow, 13, 'OWNER', styleBodyTitleStyle)

		nCountFixedPR = 0
		curRow += 1
		if self.appname in self.prNeedDelivHash.keys() and self.prNeedDelivHash[self.appname].keys(): 
			self.brotherBugsDict = {}
			for appBug in self.prNeedDelivHash[self.appname].keys():
				if 'Bugzilla' in self.AlmCheckDict[self.appname].values():				
					self.bygForCirle = []
					self.bygForCirle.append(appBug)
					self.getCloneProjectBugID(appBug, self.appname)				
					count = 0
					while True:					
						for bug in self.bygForCirle: 
							n = len(self.bygForCirle)
							self.getCloneProjectBugID(bug, self.appname)
							m = len(self.bygForCirle)
							if bug in self.bygForCirle:
								continue
						count = count + 1	
						if m == n:	
							break
						elif count >15:
							break
					for bug in self.cloneBugs:
						self.getCloneProjectBugInfo(conf,appBug,bug,curVerTimeStr,lastVerTimeStr,self.appname)
					self.cloneBugs = []

				elif 'ALM' in self.AlmCheckDict[self.appname].values():				
					self.getCloneProjectBugIDALM(appBug, self.appname)
					for bug in self.cloneBugs:						
						self.getCloneProjectBugInfoALM(conf,appBug,bug,curVerTimeStr,lastVerTimeStr,self.appname)
					self.cloneBugs = []
			if self.appname not in self.editCloneDefect.keys():
				self.editCloneDefect[self.appname] = {}
			self.editCloneDefect[self.appname] = copy.deepcopy(self.brotherBugsDict)
			for appb in self.brotherBugsDict.keys():			
				bugNumber = len(self.brotherBugsDict[appb])
				forWriteBugs = []
				forWriteBugs = self.brotherBugsDict.pop(appb)
				for bugDict in forWriteBugs:
					nCountFixedPR += 1						
					worksheet.write(curRow, 0, nCountFixedPR, styleBodyInfoStyle)
					DictForWriteBugs = {}
					worksheet.write(curRow, 1, bugDict['GenericApp_BugID'], styleBodyInfoStyle)
					worksheet.set_link(curRow, 1, self.bugzillaUrlBase % bugDict['GenericApp_BugID'])
					worksheet.write(curRow, 2, bugDict['Project_BugID'], styleBodyInfoStyle)
					worksheet.set_link(curRow, 2, self.bugzillaUrlBase % bugDict['Project_BugID'])		
					if bugDict['Project_BugID'] not in self.projectBugIDs:		
						self.projectBugIDs.append(int(bugDict['Project_BugID']))
					worksheet.write(curRow, 3, bugDict['type'],styleBodyInfoStyle)
					worksheet.write(curRow, 4, bugDict['status'], styleBodyInfoStyle)
					worksheet.write(curRow, 5, bugDict['reporter'], styleBodyInfoStyle)
					worksheet.write(curRow, 6, bugDict['Product_name'], styleBodyInfoStyle)
					worksheet.write(curRow, 7, bugDict['priority'], styleBodyInfoStyle)
					worksheet.write(curRow, 8, bugDict['ipr'], styleBodyInfoStyle)
					worksheet.write(curRow, 9, bugDict['function'], styleBodyInfoStyle)
					worksheet.write_merge(curRow, curRow, 10, 11, bugDict['desc'], styleBodyInfoStyle)
					worksheet.write(curRow, 12, bugDict['deadline'], styleBodyInfoStyle)
					worksheet.write(curRow, 13, bugDict['ownerinfo'], styleBodyInfoStyle)
					curRow += 1	
		else:
			curRow += 1


		self.maxColumn = 13
		worksheet.write_merge(curRow, curRow, 0, self.maxColumn, 'Not Cloned Defect/Task OF Projects', styleReleaseNoteTitleStyle5)
		curRow += 1
		worksheet.write(curRow, 0, 'NO', styleBodyTitleStyle)
		worksheet.write(curRow, 1, 'Generic-BUG-ID', styleBodyTitleStyle)
		worksheet.write(curRow, 2, 'Project-BUG-ID', styleBodyTitleStyle)
		worksheet.write(curRow, 3, 'PR/CR/FR', styleBodyTitleStyle)
		worksheet.write(curRow, 4, 'PR-STATUS', styleBodyTitleStyle)
		worksheet.write(curRow, 5, 'DEADLINE', styleBodyTitleStyle)
		worksheet.write(curRow, 6, 'Project-name', styleBodyTitleStyle)
		worksheet.write(curRow, 7, 'PRIORITY', styleBodyTitleStyle)
		worksheet.write(curRow, 8, 'IPR', styleBodyTitleStyle)			
		worksheet.write(curRow, 9, 'FUNCTION', styleBodyTitleStyle)
		#worksheet.write(curRow, 12, 'TARGET-MILESTONE', styleBodyTitleStyle)
		#worksheet.write(curRow, 12, 'SHORT-DESC', styleBodyTitleStyle)
		worksheet.write_merge(curRow, curRow, 10, 11, 'SHORT-DESC', styleBodyTitleStyle)
		worksheet.write(curRow, 12, 'OWNER', styleBodyTitleStyle)
		worksheet.write(curRow, 13, 'REPORTER', styleBodyTitleStyle)
		curRow += 1
		if self.appname in self.prNotGenericApkFromCodeDict.keys() and self.prNotGenericApkFromCodeDict[self.appname]:			
			nCountPRFromCode = 0
			forWriteNoCloneBugs = []
			forWriteNoCloneBugs = self.prNotGenericApkFromCodeDict.pop(self.appname)					
			for i in forWriteNoCloneBugs:
				#print i
				bugid = i.keys()[0]
				if int(bugid) not in self.projectBugIDs:
					NoCloneBugFromcodeDict = i				
					nCountPRFromCode += 1						
					worksheet.write(curRow, 0, nCountPRFromCode, styleBodyInfoStyle)
					#print NoCloneBugFromcodeDict[bugid]
					if 'BugID' in NoCloneBugFromcodeDict[bugid].keys():
						worksheet.write(curRow, 1, "None", styleBodyInfoStyle)		
						worksheet.write(curRow, 2, NoCloneBugFromcodeDict[bugid]['BugID'], styleBodyInfoStyle)
						worksheet.set_link(curRow, 2, self.bugzillaUrlBase % NoCloneBugFromcodeDict[bugid]['BugID'])
						worksheet.write(curRow, 3, NoCloneBugFromcodeDict[bugid]['type'], styleBodyInfoStyle)
						worksheet.write(curRow, 4, NoCloneBugFromcodeDict[bugid]['status'], styleBodyInfoStyle)
						worksheet.write(curRow, 5, NoCloneBugFromcodeDict[bugid]['reporter'], styleBodyInfoStyle)
						worksheet.write(curRow, 6, NoCloneBugFromcodeDict[bugid]['Product_name'], styleBodyInfoStyle)
						worksheet.write(curRow, 7, NoCloneBugFromcodeDict[bugid]['priority'], styleBodyInfoStyle)
						worksheet.write(curRow, 8, NoCloneBugFromcodeDict[bugid]['ipr'], styleBodyInfoStyle)
						worksheet.write(curRow, 9, NoCloneBugFromcodeDict[bugid]['function'], styleBodyInfoStyle)
						worksheet.write_merge(curRow, curRow, 10, 11, NoCloneBugFromcodeDict[bugid]['desc'], styleBodyInfoStyle)
						worksheet.write(curRow, 12, NoCloneBugFromcodeDict[bugid]['deadline'], styleBodyInfoStyle)
						worksheet.write(curRow, 13, NoCloneBugFromcodeDict[bugid]['ownerinfo'], styleBodyInfoStyle)
					curRow += 1
		self.createReleaseWidthXls(worksheet)	


	def createReleaseNoteForTest(self, conf=None):
		workbook = Workbook()
		worksheet = workbook.add_sheet(conf.getConf('appname', 'The app name'))
		if conf != None:
			### step 1, create xls title
			self.createXlsTitle(conf, worksheet)
			### step 2 create PR SW and RESOLVED PR list
			self.createReleaseNotePRCode(worksheet,self.dirverPRDict)		
		else:
			print "conf is None will exit(0)!"
			sys.exit(0)
		workbook.save('%s/attach/APK_ReleaseNote_%s_%s.xls' % (self.tempdir,self.appname, self.version))
		docmd('scp -r %s/attach/APK_ReleaseNote_%s_%s.xls user@10.92.35.20:/var/www/data/genericapp/%s/v%s/APK_ReleaseNote_%s_%s.xls' % (self.tempdir,self.appname,self.version,self.appname,self.version,self.appname,self.version))	




	## create xls title
	def createXlsTitle(self, conf, worksheet):
		self.maxColumn = 13
		if re.search("YES", self.test):
			self.version = conf.getConf('version', 'project current version')	
			self.baseVersion = conf.getConf('baseversion', 'project base version')

		fullName = conf.getConf('fullname', 'full name')
		worksheet.write_merge(0, 0, 0, self.maxColumn, 'APK RELEASE NOTES' , self.getReleaseNoteTitleStyle(17))
		worksheet.write_merge(1, 2, 0, 1, 'APK-NAME:' , self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(1, 2, 2, 7, self.appname, self.getHeadTitleItemInfoStyle(True, True, True))
		worksheet.write(1, 8, 'RELEASER:', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(1, 1, 9, self.maxColumn, fullName, self.getHeadTitleItemInfoStyle())
		worksheet.write(2, 8, 'RELEASE-DATE:', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(2, 2, 9, self.maxColumn, datetime.date.today().strftime('%Y-%m-%d'), self.getHeadTitleItemInfoStyle())
		worksheet.write_merge(3, 3, 0, 1, 'APK-VERSION:' , self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(3, 3, 2, 7, int(self.version) if self.version.isdigit() else self.version, self.getHeadTitleItemInfoStyle(True, True, True))
		worksheet.write(3, 8, 'BASE:', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(3, 3, 9, self.maxColumn, int(self.baseVersion) if self.baseVersion.isdigit() else self.baseVersion, self.getHeadTitleItemInfoStyle())
		worksheet.write_merge(4, 4, 0, 1, 'NOTE:', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(4, 4, 2, self.maxColumn, '', self.getHeadTitleItemInfoStyle())


	## create PR(include release, sw_verifier, deliver PR) code xls
	def createReleaseNotePRCode(self, worksheet,apkBugs, onGoingDefectTaskDict):		
		styleBodyInfoStyle = self.getBodyInfoStyle()
		styleBodyInfoStyleMan = self.getBodyInfoStyle(20)
		styleBodyTitleStyle = self.getBodyTitleStyle()
		styleReleaseNoteTitleStyle5 = self.getReleaseNoteTitleStyle(5)
		#if re.search("YES",self.test):
			#if self.dirverPRDict:
				#self.createReleaseMiniList(worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5,self.dirverPRDict)
		#else:
		SingleApkBugs = apkBugs	
		self.curRow = 5
		apkDeliveredBugs = {}
		apkSWNoDeliveredBugs = {}
		onGoingDefectTaskDictTMP = {}
		if self.appname in self.apkDeliveredBugs.keys():
			apkDeliveredBugs = self.apkDeliveredBugs[self.appname]			
		self.createReleaseDeliveredBugList(worksheet,apkDeliveredBugs,styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5)
		if self.appname in self.apkSWNoDeliveredBugs.keys():
			apkSWNoDeliveredBugs = self.apkSWNoDeliveredBugs[self.appname]				
		self.createReleaseNoDeliveredBugList(worksheet,apkSWNoDeliveredBugs,styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5)
		if onGoingDefectTaskDict:
			onGoingDefectTaskDictTMP = onGoingDefectTaskDict				
		self.createReleaseOnGoingDefectList(worksheet,onGoingDefectTaskDict,styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5)

		self.createReleaseSdmMes(worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5)			
		if SingleApkBugs:
			self.createReleaseMiniList(worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5,SingleApkBugs,self.appname)
			#if self.AlmCheckDict[self.appname]['related_apk_name'] and self.relatedApkUrlDict.keys(): 
				#self.createReleaseMiniList(worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5,self.relatedApkUrlDict,self.AlmCheckDict[self.appname]['related_apk_name'])
		self.SingleApkBugs = {}
		self.createReleaseWidthXlsForSheet1(worksheet)




	## create dirverDict xls table
	def createReleaseMiniList(self, worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5,SingleApkBugs, appname):
		self.maxColumn = 13
		self.curRow += 1
		bugDict = SingleApkBugs	
		worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'ALL PATCH Change LIST(%s)' % appname, styleReleaseNoteTitleStyle5)
		self.curRow += 1
		worksheet.write_merge(self.curRow, self.curRow, 0, 1, 'NO', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 2, 3, 'Content', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 4, 6, 'Author', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 7, 8, 'Project', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 9, 10, 'TAG-Number', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 11, self.maxColumn,'Date', styleBodyTitleStyle)        
		nCountFixedPR = 0
		for tProject in sorted(bugDict.keys()):
			nCountFixedPR += 1
			self.curRow += 1
			worksheet.write_merge(self.curRow, self.curRow, 0, 1, nCountFixedPR, styleBodyInfoStyle)
			worksheet.write_merge(self.curRow, self.curRow, 2, 3, bugDict[tProject]['commit'].decode('utf-8'), styleBodyInfoStyle)
			worksheet.set_link(self.curRow, 2, bugDict[tProject]['url'])
			worksheet.write_merge(self.curRow, self.curRow, 4, 6, bugDict[tProject]['author'], styleBodyInfoStyle)
			worksheet.write_merge(self.curRow, self.curRow, 7, 8, bugDict[tProject]['project'], styleBodyInfoStyle)
			worksheet.write_merge(self.curRow, self.curRow, 9, 10, bugDict[tProject]['tag'], styleBodyInfoStyle)
			worksheet.write_merge(self.curRow, self.curRow, 11, self.maxColumn, bugDict[tProject]['date'], styleBodyInfoStyle)  



	## defination worksheet width
	def createReleaseWidthXls(self, worksheet):
		worksheet.col(0).width = 1500
		worksheet.col(1).width = 4500
		worksheet.col(2).width = 4500
		worksheet.col(3).width = 3000
		worksheet.col(4).width = 3000
		worksheet.col(5).width = 6000
		worksheet.col(6).width = 7500
		worksheet.col(7).width = 3500
		worksheet.col(8).width = 3000
		worksheet.col(9).width = 4500
		worksheet.col(10).width = 8000
		worksheet.col(11).width = 4500
		worksheet.col(12).width = 3500
		worksheet.col(13).width = 3500
		worksheet.set_normal_magn(90)


	def createReleaseWidthXlsForSheet1(self, worksheet):
		worksheet.col(0).width = 1500
		worksheet.col(1).width = 3000
		worksheet.col(2).width = 3000
		worksheet.col(3).width = 3500
		worksheet.col(4).width = 3500
		worksheet.col(5).width = 6000
		worksheet.col(6).width = 6000
		worksheet.col(7).width = 3500
		worksheet.col(8).width = 3500
		worksheet.col(9).width = 4500
		worksheet.col(10).width = 3500
                #add zhaoshie 20150612
		worksheet.col(11).width = 4500
		worksheet.col(12).width = 8500
		worksheet.col(13).width = 8500
		worksheet.set_normal_magn(90)

	def createReleaseSdmMes(self, worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5):
		self.maxColumn = 13
		self.curRow += 1
		worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'SDM Change List', styleReleaseNoteTitleStyle5)
		self.curRow += 1
		worksheet.write(self.curRow, 0, 'NO', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 1, 2, 'SDM-ID', styleBodyTitleStyle)
		worksheet.write(self.curRow, 3, 'FILE-NAME', styleBodyTitleStyle)
		worksheet.write(self.curRow, 4, 'PROJECT', styleBodyTitleStyle)
		worksheet.write(self.curRow, 5, 'IS_CUSTO', styleBodyTitleStyle)
		worksheet.write(self.curRow, 6, 'ACTION', styleBodyTitleStyle)
		worksheet.write(self.curRow, 7, 'Default Value'.upper(), styleBodyTitleStyle)
		worksheet.write(self.curRow, 8, 'apK DEFECT/TASK'.upper(), styleBodyTitleStyle)	
		worksheet.write(self.curRow, 9, 'peoject DEFECT/TASK'.upper(), styleBodyTitleStyle)
		worksheet.write(self.curRow, 10, 'PATCH_OWNER', styleBodyTitleStyle)
		worksheet.write(self.curRow, 11, 'Description'.upper(), styleBodyTitleStyle)
		#worksheet.write(self.curRow, 11, 'FR/DEFECT/TASK STATUS', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow,12, self.maxColumn,'comment', styleBodyTitleStyle)
		if not self.appPlfDict:
			self.curRow += 1
		nCountFixedPR = 0
		sorted_sdmChangeInfoDict=sorted(self.appPlfDict)
		#add by renzhi2015-12-11
		plfPrIdState = {}
		#end by renzhi2015-12-11
 		for sdm in sorted_sdmChangeInfoDict:
			tem_sdm = sdm
			match = re.match('^plf/(.*)',tem_sdm) 
			if match:
				tem_sdm = match.group(1)
 			self.curRow += 1
			nCountFixedPR += 1
			worksheet.write(self.curRow, 0, nCountFixedPR, styleBodyInfoStyle)
			#modified by renzhi for isdm format 2015-11-5
			if len(tem_sdm.split('/', 1)[1].split('/', 1)) == 2:
				worksheet.write_merge(self.curRow, self.curRow, 1, 2, tem_sdm.split('/', 1)[1].split('/', 1)[1], styleBodyInfoStyle)
				worksheet.write(self.curRow, 3, tem_sdm.split('/', 2)[1], styleBodyInfoStyle)
				worksheet.write(self.curRow, 4, re.sub('\.[pP][lL][fF]$', '', tem_sdm.split('/', 1)[0]), styleBodyInfoStyle)
			else:
				worksheet.write_merge(self.curRow, self.curRow, 1, 2, tem_sdm.split('/', 1)[1].split('/', 1)[0], styleBodyInfoStyle)
				worksheet.write(self.curRow, 3, tem_sdm.split('/', 1)[0], styleBodyInfoStyle)
				worksheet.write(self.curRow, 4, re.sub('\.[pP][lL][fF]$', '', tem_sdm.split('/', 1)[0]), styleBodyInfoStyle)
			#modified by renzhi for isdm format 2015-11-5
            #worksheet.write(self.curRow, 6, sdminfo['action'], styleBodyInfoStyle)
            #worksheet.write_merge(self.curRow, self.curRow, 7, 8, sdminfo['value'], styleBodyInfoStyle)
            		worksheet.write(self.curRow, 5, self.appPlfDict[sdm]['custo'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 6, self.appPlfDict[sdm]['action'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 7, self.appPlfDict[sdm]['value'], styleBodyInfoStyle)
			prPlfVal=[]
			prPlfState = []
			prProjectVal = []

			#for(filename,prList) in self.sdmChangeToPRDict.items():
			if 'pr' not in self.appPlfDict[sdm].keys():
				prPlfVal=[]
				prProjectVal=[]
				prPlfState = []
				prtypeid = ''
				porjectname = ''
			else:			
				allBugs = ','.join(self.appPlfDict[sdm]['pr'])
				#allBugs = ','.join(self.plfChangeInfoDict[sdm]['pr']) 
				#add by zhaoshie 20150619			
				prPlfStr=allBugs.split(',')
				for eachBug in prPlfStr:
					self.clonedDefectOFPLF = []
					if eachBug not in self.clonedDefectOFPLF:
						self.clonedDefectOFPLF.append(eachBug)
					if eachBug:	
						self.getBrotherBugsALM(eachBug, self.appname, self.clonedDefectOFPLF)

					for oneBug in self.clonedDefectOFPLF:
						strings = ','.join(prPlfVal)                    
						if not set(eachBug).difference(strings):
							break
						else:
							#change by renzhi2015-12-11
							if eachBug not in plfPrIdState.keys():	
								if 'P' in eachBug.upper():
									continue						
								prType,prState,porjectname = self.getDefectTypeStatus(eachBug)
								projectList = porjectname.split("/")
								porjectname = projectList[len(projectList) -1 ]							
								prtypeid = '%s %s%s:%s' %(porjectname,prType,eachBug,prState)
								plfPrIdState[eachBug] = prtypeid
							else:
								prtypeid = plfPrIdState[eachBug]
						#end change by renzhi2015-12-11
							apk_project_name = self.AlmCheckDict[self.appname]['apkproject'].split('/')
							if apk_project_name[len(apk_project_name)-1] in prtypeid:	
								prPlfVal.append(prtypeid)
							else:
								prProjectVal.append(prtypeid)

                        prPlfValstring = ','.join(prPlfVal)
			worksheet.write(self.curRow, 8, prPlfValstring, styleBodyInfoStyle)
			prProjectPlfValstring=','.join(prProjectVal)
			worksheet.write(self.curRow, 9, prProjectPlfValstring, styleBodyInfoStyle)
			if self.appname in self.sdmauthor.keys() and sdm in self.sdmauthor[self.appname].keys():
				worksheet.write(self.curRow, 10, self.sdmauthor[self.appname][sdm][0], styleBodyInfoStyle)
			else:
				worksheet.write(self.curRow, 10, '', styleBodyInfoStyle)			
                        #worksheet.write(self.curRow, 11, prPlfStatestring, styleBodyInfoStyle)  #add defect status by zhaoshie 20150618
			worksheet.write(self.curRow, 11, self.appPlfDict[sdm]['desc'], styleBodyInfoStyle)
			if "comment" in self.appPlfDict[sdm].keys():
				worksheet.write_merge(self.curRow,self.curRow, 12,self.maxColumn,self.appPlfDict[sdm]['comment'], styleBodyInfoStyle)
			else:
				worksheet.write_merge(self.curRow,self.curRow, 12, self.maxColumn,'',styleBodyInfoStyle)


	def createReleaseOnGoingDefectList(self,worksheet,onGoingDefectTaskDict,styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5):
		self.maxColumn = 13
		self.curRow += 1
		worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'ONGOING Defect/Task', styleReleaseNoteTitleStyle5)
		self.curRow += 1
		worksheet.write(self.curRow, 0, 'NO', styleBodyTitleStyle)
		worksheet.write(self.curRow, 1, 'BUG-ID', styleBodyTitleStyle)
		worksheet.write(self.curRow, 2, 'PR/CR/FR', styleBodyTitleStyle)
		worksheet.write(self.curRow, 3, 'PR-STATUS', styleBodyTitleStyle)
		worksheet.write(self.curRow, 4, 'DEADLINE', styleBodyTitleStyle)
		worksheet.write(self.curRow, 5, 'OWNER', styleBodyTitleStyle)
		worksheet.write(self.curRow, 6, 'REPORTER', styleBodyTitleStyle)
		worksheet.write(self.curRow, 7, 'PRIORITY', styleBodyTitleStyle)
		worksheet.write(self.curRow, 8, 'IPR', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 9, self.maxColumn,'SHORT-DESC', styleBodyTitleStyle)
		nCountFixedPR = 0
		if not onGoingDefectTaskDict:
			self.curRow += 1
		for bugid in sorted(onGoingDefectTaskDict.keys()):
			nCountFixedPR += 1
			self.curRow += 1
			worksheet.write(self.curRow, 0, nCountFixedPR, styleBodyInfoStyle)
			worksheet.write(self.curRow, 1, bugid, styleBodyInfoStyle)
			worksheet.set_link(self.curRow, 1, self.bugzillaUrlBase % bugid)
			worksheet.write(self.curRow, 2, onGoingDefectTaskDict[bugid]['type'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 3, onGoingDefectTaskDict[bugid]['status'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 4, onGoingDefectTaskDict[bugid]['deadline'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 5, onGoingDefectTaskDict[bugid]['ownerinfo'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 6, onGoingDefectTaskDict[bugid]['reporter'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 7, onGoingDefectTaskDict[bugid]['priority'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 8, onGoingDefectTaskDict[bugid]['ipr'], styleBodyInfoStyle)
			worksheet.write_merge(self.curRow, self.curRow,9, self.maxColumn, onGoingDefectTaskDict[bugid]['desc'], styleBodyInfoStyle)


	def createReleaseDeliveredBugList(self,worksheet, apkDeliveredBugs,styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5):
		self.maxColumn = 13
		self.curRow += 1
		worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'FIXED DEFECT/TASK', styleReleaseNoteTitleStyle5)
		self.curRow += 1
		worksheet.write(self.curRow, 0, 'NO', styleBodyTitleStyle)
		worksheet.write(self.curRow, 1, 'BUG-ID', styleBodyTitleStyle)
		worksheet.write(self.curRow, 2, 'PR/CR/FR', styleBodyTitleStyle)
		worksheet.write(self.curRow, 3, 'PR-STATUS', styleBodyTitleStyle)
		worksheet.write(self.curRow, 4, 'DEADLINE', styleBodyTitleStyle)
		worksheet.write(self.curRow, 5, 'OWNER', styleBodyTitleStyle)
		worksheet.write(self.curRow, 6, 'REPORTER', styleBodyTitleStyle)
		worksheet.write(self.curRow, 7, 'PRIORITY', styleBodyTitleStyle)
		worksheet.write(self.curRow, 8, 'IPR', styleBodyTitleStyle)
		worksheet.write(self.curRow, 9, 'FUNCTION', styleBodyTitleStyle)
		#worksheet.write(self.curRow, 10, 'TARGET-MILESTONE', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 10, self.maxColumn, 'SHORT-DESC', styleBodyTitleStyle)
		nCountFixedPR = 0
		if not apkDeliveredBugs:
			self.curRow += 1
		for bugid in sorted(apkDeliveredBugs.keys()):
			nCountFixedPR += 1
			self.curRow += 1
			worksheet.write(self.curRow, 0, nCountFixedPR, styleBodyInfoStyle)
			worksheet.write(self.curRow, 1, bugid, styleBodyInfoStyle)
			worksheet.set_link(self.curRow, 1, self.bugzillaUrlBase % bugid)
			worksheet.write(self.curRow, 2, apkDeliveredBugs[bugid]['type'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 3, apkDeliveredBugs[bugid]['status'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 4, apkDeliveredBugs[bugid]['deadline'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 5, apkDeliveredBugs[bugid]['ownerinfo'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 6, apkDeliveredBugs[bugid]['reporter'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 7, apkDeliveredBugs[bugid]['priority'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 8, apkDeliveredBugs[bugid]['ipr'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 9, apkDeliveredBugs[bugid]['function'], styleBodyInfoStyle)
			#worksheet.write(self.curRow, 10, apkDeliveredBugs[bugid]['milestone'], styleBodyInfoStyle)
			worksheet.write_merge(self.curRow, self.curRow, 10, self.maxColumn, apkDeliveredBugs[bugid]['desc'], styleBodyInfoStyle)



	def createReleaseNoDeliveredBugList(self,worksheet,SWNoDeliveredBugs,styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5):
		self.maxColumn = 13
		self.curRow += 1
		worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'RESOLVED STATUS FIXED DEFECT/TASK', styleReleaseNoteTitleStyle5)
		self.curRow += 1
		worksheet.write(self.curRow, 0, 'NO', styleBodyTitleStyle)
		worksheet.write(self.curRow, 1, 'BUG-ID', styleBodyTitleStyle)
		worksheet.write(self.curRow, 2, 'PR/CR/FR', styleBodyTitleStyle)
		worksheet.write(self.curRow, 3, 'PR-STATUS', styleBodyTitleStyle)
		worksheet.write(self.curRow, 4, 'DEADLINE', styleBodyTitleStyle)
		worksheet.write(self.curRow, 5, 'OWNER', styleBodyTitleStyle)
		worksheet.write(self.curRow, 6, 'REPORTER', styleBodyTitleStyle)
		worksheet.write(self.curRow, 7, 'PRIORITY', styleBodyTitleStyle)
		worksheet.write(self.curRow, 8, 'IPR', styleBodyTitleStyle)
		worksheet.write(self.curRow, 9, 'FUNCTION', styleBodyTitleStyle)
		#worksheet.write(self.curRow, 10, 'TARGET-MILESTONE', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 10, self.maxColumn, 'SHORT-DESC', styleBodyTitleStyle)
		nCountFixedPR = 0
		if not SWNoDeliveredBugs:
			self.curRow += 1
		for bugid in sorted(SWNoDeliveredBugs.keys()):
			nCountFixedPR += 1
			self.curRow += 1
			worksheet.write(self.curRow, 0, nCountFixedPR, styleBodyInfoStyle)
			worksheet.write(self.curRow, 1, bugid, styleBodyInfoStyle)
			worksheet.set_link(self.curRow, 1, self.bugzillaUrlBase % bugid)
			worksheet.write(self.curRow, 2, SWNoDeliveredBugs[bugid]['type'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 3, SWNoDeliveredBugs[bugid]['status'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 4, SWNoDeliveredBugs[bugid]['deadline'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 5, SWNoDeliveredBugs[bugid]['ownerinfo'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 6, SWNoDeliveredBugs[bugid]['reporter'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 7, SWNoDeliveredBugs[bugid]['priority'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 8, SWNoDeliveredBugs[bugid]['ipr'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 9, SWNoDeliveredBugs[bugid]['function'], styleBodyInfoStyle)
			#worksheet.write(self.curRow, 10, SWNoDeliveredBugs[bugid]['milestone'], styleBodyInfoStyle)
			worksheet.write_merge(self.curRow, self.curRow, 10, self.maxColumn, SWNoDeliveredBugs[bugid]['desc'], styleBodyInfoStyle)

		


	

