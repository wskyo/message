#!/usr/bin/python
#coding=utf-8
############################################################################
## Sheet Utils for create xls table.
## add by jianbo.deng for superspam create 2013-08-27
############################################################################

import re
import datetime
import time
import commands

from ReleaseStyle import *
from pyExcelerator import *
from Utils import *
from Config import *
from UserInfo import *
import DeveloperUtils

## xls table max column defualt is 12	

class SheetUtils:
	## create relase note main method
	def createReleaseNoteFromBugzilla(self, conf=None):
        	from DBUtils import *
		needDeliverPR = False
		curVerTimeStr = ''
		lastVerTimeStr = ''
		productIdNumList = []
		prFromCodeList = []
		bugzillaDatePRList = []
		prManualChangeList = []
		prVeriSWFromCodeInfoDict = {}
		prResolveFromCodeInfoDict = {}
		prVeriSWOldResolveInfoDict = {}
		#add by renzhi.yang to get all delivered bug of the project on 2015-2-5 
		allDeliveredBugsInfoDict = {}
		#end add by renzhi
		productIdSqlList = []
        	self.OGPRTitleList = ['HOMO_OG','P0_OG','P1_IPR_300_OG','OTHERS_OG','INTERNAL_OG_TOTAL','EXTERNAL_OG_TOTAL','TOTAL_OG']
        	self.prOGFromDBDict = {}
        	self.OGHomoDefectDict = {}
        	self.prResolveInfoDict = {}
        	self.prSWAndRelOnOtherDict = {}
		workbook = Workbook()
		worksheet = workbook.add_sheet('INT_Release_Note')

		mysqlConn=MySQLdb.connect('172.24.61.199', port=3306, user='scm_tools', passwd='SCM_TOOLS123!', db='bugs', charset='gbk')
		if conf != None:
			### init productIdNumList and prFromCodeList
			self.getIDNumberAndCodeList(conf, productIdNumList, prFromCodeList, mysqlConn)
			### step 1, create xls title
			self.createXlsTitle(conf, worksheet)
			self.createGoogleInfo(conf, worksheet)
			### get current version manifest create time and lase versin manifest creaete time
			curVerTimeStr,lastVerTimeStr = self.getCurrAndLaseTime(conf)
			### step 2 create PR SW and RESOLVED PR list
			self.getSWAndRelPRList(conf, mysqlConn, prFromCodeList, prVeriSWFromCodeInfoDict, prResolveFromCodeInfoDict, curVerTimeStr, lastVerTimeStr)
			#add for reqirement for ongoing pr list begin 01-12-2015 by INT
			###get ongoing pr list
			self.getOGPRDict(conf,mysqlConn,productIdNumList,self.OGPRTitleList,self.prOGFromDBDict,curVerTimeStr,lastVerTimeStr)
			#add for reqirement for ongoing pr list end 01-12-2015 by INT
			self.getOGHomoDefect(conf,mysqlConn,productIdNumList,self.OGHomoDefectDict,curVerTimeStr,lastVerTimeStr)
			self.prOGFromDBDict[self.OGPRTitleList[0]]=self.OGHomoDefectDict.__len__()
			### create PR old RESOLVED list
			self.getVeriSWOldResolveInfoDict(mysqlConn, productIdNumList, prVeriSWOldResolveInfoDict, prVeriSWFromCodeInfoDict, prResolveFromCodeInfoDict,curVerTimeStr, lastVerTimeStr, conf)
			#add by renzhiyang 2015-2-5
			self.getAllDeliveredBugs(mysqlConn, productIdNumList,allDeliveredBugsInfoDict,conf)
			self.getPrSWAndRelOnOtherDict(conf,mysqlConn,lastVerTimeStr, curVerTimeStr)
			#end add by renzhi 2015-2-5
			self.deliverPRlist(conf, mysqlConn, prVeriSWFromCodeInfoDict, prVeriSWOldResolveInfoDict)
			### create PR xls table
			self.createReleaseNotePRCode(worksheet, prVeriSWFromCodeInfoDict, prResolveFromCodeInfoDict, prVeriSWOldResolveInfoDict)
		##return worksheet
			#self.getPrSWAndRelOnOtherDict(conf,mysqlConn,lastVerTimeStr, curVerTimeStr)
			self.createOnOtherBranchNote(workbook)
			#add by renzhiyang 2015-2-5
			worksheetdelivered = workbook.add_sheet('all_delivered_bugs_of_project')
			self.createReleaseNoteAllDeliveredBugs(worksheetdelivered, allDeliveredBugsInfoDict)
			#end add by renzhi 2015-2-5
			worksheetWifiCheck = workbook.add_sheet('power_comsuption_modification')
			self.createReleaseNoteWifiCheck(worksheetWifiCheck)				
		else:
			print "conf is None will exit(0)!"
			sys.exit(0)
		workbook.save('%s/attach/ReleaseNote_%s_SW%s.xls' % (self.tempdir, conf.getConf('prlistprojname', 'Project name in PR List file name'), conf.getConf('version','current version')))
		docmd('cp %s/attach/ReleaseNote_%s_SW%s.xls /tmp/' % (self.tempdir, conf.getConf('prlistprojname', 'Project name in PR List file name'), conf.getConf('version', 'current version')))
	def createReleaseNoteFromALM(self, conf=None):
		from IntegrityDBUtils import *
		needDeliverPR = False
		curVerTimeStr = ''
		lastVerTimeStr = ''
		productIdNumList = []
		prFromCodeList = []
		bugzillaDatePRList = []
		prManualChangeList = []
		prVeriSWFromCodeInfo = []
		prResolveFromCodeInfo = []
		prVeriSWOldResolveInfo = []
		prVeriSWFromCodeInfoDict = {}
		prResolveFromCodeInfoDict = {}
		prVeriSWOldResolveInfoDict = {}
		productIdSqlList = []
		workbook = Workbook()
		worksheet = workbook.add_sheet('INT_Release_Note')

		### add by ruifeng for ALM releasenote begin
		conf = Config()
		versionStr = conf.getConf('version', 'Version number {^\w\w\w-\w$}')
		if versionStr[-1] == '0':
			version = versionStr[:-2]
		else:
			version = versionStr
		### add by ruifeng for ALM releasenote end

		self.intClient = IntegrityClient(wsdl="https://172.24.147.71:7003/webservices/10/2/Integrity/?wsdl",
		credential_username="hz.int",
		credential_password="ptc")
		if conf != None:
			print '++++++++++'
			print self.prFromCodeDict
			### add by ruifeng for ALM releasenote begin
			integrity_projects = conf.getConf('bugProduct', 'integrity_projects')
			integrity_branch = conf.getConf('projbugbranch', 'integrity_branch')
			### add by ruifeng for ALM releasenote end
			### init productIdNumList and prFromCodeList
			self.getIDNumberAndCodeList(conf, productIdNumList, prFromCodeList, self.intClient)
			### step 1, create xls title
			self.createXlsTitle(conf, worksheet)
			### get current version manifest create time and lase versin manifest creaete time
			curVerTimeStr,lastVerTimeStr = self.getCurrAndLaseTime(conf)
			### step 2 create PR SW and RESOLVED PR list
			self.getSWAndRelPRList(conf, self.intClient, prFromCodeList, prVeriSWFromCodeInfo, prResolveFromCodeInfo, curVerTimeStr, lastVerTimeStr)
			### create PR old RESOLVED list
			self.getVeriSWOldResolveInfo(self.intClient, productIdNumList, prVeriSWOldResolveInfo, prVeriSWFromCodeInfo, curVerTimeStr, lastVerTimeStr, conf)
			### deliver PR
			self.deliverPRlist(conf, self.intClient, prVeriSWFromCodeInfo, prVeriSWOldResolveInfo)
			### change array to dict
			self.changeArrayToDict(prVeriSWFromCodeInfo, prResolveFromCodeInfo, prVeriSWOldResolveInfo, prVeriSWFromCodeInfoDict, prResolveFromCodeInfoDict, prVeriSWOldResolveInfoDict)
 			### create PR xls table
			self.createReleaseNotePRCode(worksheet, prVeriSWFromCodeInfoDict, prResolveFromCodeInfoDict, prVeriSWOldResolveInfoDict)
			### add by ruifeng for ALM releasenote begin
			try:
				#integrity_branch = self.branch_of_version(version)
				ret = self.intClient.createReleaseNote(Project=integrity_projects, State='Active', Branch=integrity_branch, Version='SW%s'%version)
    				if not ret:
     					print "createReleaseNote Error"
			except:
				pass
            ### add by ruifeng for ALM releasenote end
        ##return worksheet
        	else:
            		print "conf is None will exit(0)!"
            		sys.exit(0)
        	workbook.save('%s/attach/ReleaseNote_%s_SW%s.xls' % (self.tempdir, conf.getConf('prlistprojname', 'Project name in PR List file name'), conf.getConf('version','current version')))
        ##adjust pr reporter  add by lyf
	def adjustSWReportPR(self,reportname):
		##modify by renzhi for ALm
		reporterMail = ''
		flag = False		
		#match = re.match('.+<(.+)>$',reportname)
		#if match:
			#reporterMail = match.group(1)
		if reportname in DeveloperUtils.engineer:
			flag = True
		##end by renzhi for ALM
		return flag
        ##adjust pr reporter  end by lyf

	## create xls title
	def createXlsTitle(self, conf, worksheet):
                print self.maxColumn
		version = conf.getConf('version', 'project current version')
		fullName = conf.getConf('fullname', 'full name')
		baseVersion = conf.getConf('baseversion', 'project base version')
        	worksheet.write_merge(0, 0, 0, self.maxColumn, 'RELEASE NOTES' , self.getReleaseNoteTitleStyle(11))
		worksheet.write_merge(1, 2, 0, 1, 'PROJECT-NAME:' , self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(1, 2, 2, 7, conf.getConf('releasenoteprojname', 'Project name in release note'), self.getHeadTitleItemInfoStyle(True, True, True))
		worksheet.write(1, 8, 'RELEASER:', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(1, 1, 9, self.maxColumn, fullName, self.getHeadTitleItemInfoStyle())
		worksheet.write(2, 8, 'RELEASE-DATE:', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(2, 2, 9, self.maxColumn, datetime.date.today().strftime('%Y-%m-%d'), self.getHeadTitleItemInfoStyle())
		worksheet.write_merge(3, 3, 0, 1, 'MAIN-VERSION:' , self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(3, 3, 2, 7, int(version) if version.isdigit() else version, self.getHeadTitleItemInfoStyle(True, True, True))
		worksheet.write(3, 8, 'BASE:', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(3, 3, 9, self.maxColumn, int(baseVersion) if baseVersion.isdigit() else baseVersion, self.getHeadTitleItemInfoStyle())
		worksheet.write_merge(4, 4, 0, 1, 'NOTE:', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(4, 4, 2, self.maxColumn, '', self.getHeadTitleItemInfoStyle())

	##add for google info
	def createGoogleInfo(self, conf, worksheet):
		self.curRow += 1
                print self.maxColumn
		worksheet.write_merge(self.curRow, self.curRow, 0, 3, 'android security patch level', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(self.curRow, self.curRow, 4, self.maxColumn, self.curCodeSecuPatchLevel, self.getHeadTitleItemInfoStyle(bold=True))
		self.curRow += 1
        	worksheet.write_merge(self.curRow, self.curRow, 0, 3, 'GMS version from current version code' , self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write(self.curRow, 4, self.GMSVersionFromCode, self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(self.curRow, self.curRow, 5, 6, 'GMS Latest released version', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write(self.curRow, 7, self.GMSVersionReleased, self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write(self.curRow, 8, 'GMS lastest deadline', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(self.curRow, self.curRow, 9, self.maxColumn, self.GMSDeadline, self.getHeadTitleItemInfoStyle(bold=True))
		self.curRow += 1
        	worksheet.write_merge(self.curRow, self.curRow, 0, 3, 'Google CTS lastest version' , self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write(self.curRow, 4, self.GoogleCTSVersion, self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(self.curRow, self.curRow, 5, 6, 'GoogleCTS lastest version deadline', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(self.curRow, self.curRow, 7, self.maxColumn, self.GoogleCTSNewVersionDeadline, self.getHeadTitleItemInfoStyle(bold=True))
		self.curRow += 1
        	worksheet.write_merge(self.curRow, self.curRow, 0, 3, 'Google GTS lastest version' , self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write(self.curRow, 4, self.GoogleGTSVersion, self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(self.curRow, self.curRow, 5, 6, 'GoogleGTS lastest version deadline', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(self.curRow, self.curRow, 7, self.maxColumn, self.GoogleGTSNewVersionDeadline, self.getHeadTitleItemInfoStyle(bold=True))
		self.curRow += 1
	def createOnOtherBranchNote(self, workbook):
		styleBodyInfoStyle = self.getBodyInfoStyle()
		styleBodyInfoStyleMan = self.getBodyInfoStyle(20)
		styleBodyTitleStyle = self.getBodyTitleStyle()
		styleReleaseNoteTitleStyle5 = self.getReleaseNoteTitleStyle(5)
		self.curRow = 0
		if self.prSWAndRelOnOtherDict.__len__() > 0:
			for sheetName in self.prSWAndRelOnOtherDict.keys():
				sheet = workbook.add_sheet(sheetName)
                #sheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'Bug Branch:%s' % sheetName , self.getReleaseNoteTitleStyle(17))
 				sheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'Bug Branch:%s' % sheetName , self.getReleaseNoteTitleStyle(11))
				self.curRow += 1
				if self.prSWAndRelOnOtherDict[sheetName][0].__len__() > 0:
					self.createReleaseVeriSWPR(sheet, self.prSWAndRelOnOtherDict[sheetName][0], None, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5)
				if self.prSWAndRelOnOtherDict[sheetName][1].__len__() > 0:
					self.createReleaseResolvePR(sheet, self.prSWAndRelOnOtherDict[sheetName][1], styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5)
					self.createReleaseWidthXls(sheet)

	def createReleaseNotePRCode(self, worksheet, prVeriSWFromCodeInfoDict, prResolveFromCodeInfoDict, prVeriSWOldResolveInfoDict):
		styleBodyInfoStyle = self.getBodyInfoStyle()
		styleBodyInfoStyleMan = self.getBodyInfoStyle(20)
		styleBodyTitleStyle = self.getBodyTitleStyle()
		styleReleaseNoteTitleStyle5 = self.getReleaseNoteTitleStyle(5)
		styleHighLightBodyStyle = self.getHighLightBodyStyle(10)

		# modify for newreleasenote by ruifeng 20150115 begin
		if prVeriSWFromCodeInfoDict or prVeriSWOldResolveInfoDict:
			self.createReleaseVeriSWPR(worksheet, prVeriSWFromCodeInfoDict, prVeriSWOldResolveInfoDict, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5,styleHighLightBodyStyle)
		if prResolveFromCodeInfoDict:
			self.createReleaseResolvePR(worksheet, prResolveFromCodeInfoDict, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5,styleHighLightBodyStyle) 
		if self.patchWithoutPRList:
			self.createReleaseNotePatch(worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5)
		if self.apkChangeInfoDict:
			self.createReleaseApkMes(worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5)
		if self.sdmChangeInfoDict:
			self.createReleaseSdmMes(worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5)
		if self.prOGFromDBDict:
			for number in self.prOGFromDBDict.values():
				if number != 0:
					self.createReleaseOGPR(worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5)
					break
		if self.OGHomoDefectDict:
			self.createReleaseOGHomoDefect(worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5)
		for i in range(self.curRow+1):
			worksheet.write(i, 14,'  ')
		self.createReleaseWidthXls(worksheet)  	
	    
    ## create SW_Verifier xls table
	def createReleaseVeriSWPR(self, worksheet, prVeriSWFromCodeInfoDict, prVeriSWOldResolveInfoDict, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5,styleHighLightBodyStyle):
		self.curRow += 1
		worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'Fixed FR/Defect/Task List', styleReleaseNoteTitleStyle5)
		self.curRow += 1
		worksheet.write(self.curRow, 0, 'NO', styleBodyTitleStyle)
		worksheet.write(self.curRow, 1, 'BUG-ID', styleBodyTitleStyle)
		worksheet.write(self.curRow, 2, 'FR/DEFECT', styleBodyTitleStyle)
		worksheet.write(self.curRow, 3, 'REPORTER', styleBodyTitleStyle)
		worksheet.write(self.curRow, 4, 'STATUS', styleBodyTitleStyle)
		worksheet.write(self.curRow, 5, 'OWNER', styleBodyTitleStyle)
		worksheet.write(self.curRow, 6, 'FUNCTION', styleBodyTitleStyle)
		worksheet.write(self.curRow, 7, 'SHORT-DESC', styleBodyTitleStyle)
		worksheet.write(self.curRow, 8, 'CHANGE-MENUTREE-OR-IMAGE', styleBodyTitleStyle)
		#worksheet.write_merge(self.curRow, self.curRow, 7, 8, 'SHORT-DESC', styleBodyTitleStyle)
		worksheet.write(self.curRow, 9, 'MODULES-IMPACT', styleBodyTitleStyle)
		worksheet.write(self.curRow, 10, 'TEST-SUGGESTION', styleBodyTitleStyle)
                #add by zhaoshie 20150612
		worksheet.write(self.curRow, 11, 'ROOT-CAUSE', styleBodyTitleStyle)
		worksheet.write(self.curRow, 12, 'ROOT-CAUSE-DETAIL', styleBodyTitleStyle)
		worksheet.write(self.curRow, 13, 'SOLUTION', styleBodyTitleStyle)
        # modify for newreleasenote by ruifeng 20150115 begin
  		nCountFixedPR = 0
		if prVeriSWFromCodeInfoDict:
			for bugid in sorted(prVeriSWFromCodeInfoDict.keys()):
				nCountFixedPR += 1
				self.curRow += 1
				if self.adjustSWReportPR(prVeriSWFromCodeInfoDict[bugid]['reporter']):
					worksheet.write(self.curRow, 0, nCountFixedPR, styleHighLightBodyStyle)
					worksheet.write(self.curRow, 1, str(bugid), styleHighLightBodyStyle)
					worksheet.set_link(self.curRow, 1, self.bugzillaUrlBase % bugid)
					worksheet.write(self.curRow, 2, prVeriSWFromCodeInfoDict[bugid]['type'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 3, prVeriSWFromCodeInfoDict[bugid]['reporter'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 4, prVeriSWFromCodeInfoDict[bugid]['status'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 5, prVeriSWFromCodeInfoDict[bugid]['ownerinfo'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 6, prVeriSWFromCodeInfoDict[bugid]['function'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 7, prVeriSWFromCodeInfoDict[bugid]['desc'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 8, prVeriSWFromCodeInfoDict[bugid]['menutree_iamge'], styleHighLightBodyStyle)
					#worksheet.write_merge(self.curRow, self.curRow, 7, 8, prVeriSWFromCodeInfoDict[bugid]['desc'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 9, prVeriSWFromCodeInfoDict[bugid]['impact'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 10, prVeriSWFromCodeInfoDict[bugid]['suggestion'], styleHighLightBodyStyle)
                                        #add by zhaoshie 20150612
					worksheet.write(self.curRow, 11, prVeriSWFromCodeInfoDict[bugid]['rootcause'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 12, prVeriSWFromCodeInfoDict[bugid]['rootcauseDetail'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 13, prVeriSWFromCodeInfoDict[bugid]['Solution'], styleHighLightBodyStyle)
				else:	
					worksheet.write(self.curRow, 0, nCountFixedPR, styleBodyInfoStyle)
					worksheet.write(self.curRow, 1, str(bugid), styleBodyInfoStyle)
					worksheet.set_link(self.curRow, 1, self.bugzillaUrlBase % bugid)
					worksheet.write(self.curRow, 2, prVeriSWFromCodeInfoDict[bugid]['type'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 3, prVeriSWFromCodeInfoDict[bugid]['reporter'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 4, prVeriSWFromCodeInfoDict[bugid]['status'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 5, prVeriSWFromCodeInfoDict[bugid]['ownerinfo'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 6, prVeriSWFromCodeInfoDict[bugid]['function'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 7, prVeriSWFromCodeInfoDict[bugid]['desc'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 8, prVeriSWFromCodeInfoDict[bugid]['menutree_iamge'], styleBodyInfoStyle)
					#worksheet.write_merge(self.curRow, self.curRow, 7, 8, prVeriSWFromCodeInfoDict[bugid]['desc'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 9, prVeriSWFromCodeInfoDict[bugid]['impact'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 10, prVeriSWFromCodeInfoDict[bugid]['suggestion'], styleBodyInfoStyle)
                                        #add by zhaoshie 20150612
					worksheet.write(self.curRow, 11, prVeriSWFromCodeInfoDict[bugid]['rootcause'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 12, prVeriSWFromCodeInfoDict[bugid]['rootcauseDetail'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 13, prVeriSWFromCodeInfoDict[bugid]['Solution'], styleBodyInfoStyle)

		if prVeriSWOldResolveInfoDict:
			for bugid in sorted(prVeriSWOldResolveInfoDict.keys()):
				nCountFixedPR += 1
				self.curRow += 1
				if self.adjustSWReportPR(prVeriSWOldResolveInfoDict[bugid]['reporter']):
					worksheet.write(self.curRow, 0, nCountFixedPR, styleHighLightBodyStyle)
					worksheet.write(self.curRow, 1, str(bugid), styleHighLightBodyStyle)
					worksheet.set_link(self.curRow, 1, self.bugzillaUrlBase % bugid)
					worksheet.write(self.curRow, 2, prVeriSWOldResolveInfoDict[bugid]['type'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 3, prVeriSWOldResolveInfoDict[bugid]['reporter'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 4, prVeriSWOldResolveInfoDict[bugid]['status'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 5, prVeriSWOldResolveInfoDict[bugid]['ownerinfo'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 6, prVeriSWOldResolveInfoDict[bugid]['function'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 7, prVeriSWOldResolveInfoDict[bugid]['desc'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 8, prVeriSWOldResolveInfoDict[bugid]['menutree_iamge'], styleHighLightBodyStyle)
					#worksheet.write_merge(self.curRow, self.curRow, 7, 8, prVeriSWOldResolveInfoDict[bugid]['desc'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 9, prVeriSWOldResolveInfoDict[bugid]['impact'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 10, prVeriSWOldResolveInfoDict[bugid]['suggestion'], styleHighLightBodyStyle)
                                        #add by zhaoshie 20150612
					worksheet.write(self.curRow, 11, prVeriSWOldResolveInfoDict[bugid]['rootcause'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 12, prVeriSWOldResolveInfoDict[bugid]['rootcauseDetail'], styleHighLightBodyStyle)
					worksheet.write(self.curRow, 13, prVeriSWOldResolveInfoDict[bugid]['Solution'], styleHighLightBodyStyle)


				else:
					worksheet.write(self.curRow, 0, nCountFixedPR, styleBodyInfoStyle)
					worksheet.write(self.curRow, 1, str(bugid), styleBodyInfoStyle)
					worksheet.set_link(self.curRow, 1, self.bugzillaUrlBase % bugid)
					worksheet.write(self.curRow, 2, prVeriSWOldResolveInfoDict[bugid]['type'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 3, prVeriSWOldResolveInfoDict[bugid]['reporter'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 4, prVeriSWOldResolveInfoDict[bugid]['status'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 5, prVeriSWOldResolveInfoDict[bugid]['ownerinfo'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 6, prVeriSWOldResolveInfoDict[bugid]['function'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 7, prVeriSWOldResolveInfoDict[bugid]['desc'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 8, prVeriSWOldResolveInfoDict[bugid]['menutree_iamge'], styleBodyInfoStyle)
					#worksheet.write_merge(self.curRow, self.curRow, 7, 8, prVeriSWOldResolveInfoDict[bugid]['desc'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 9, prVeriSWOldResolveInfoDict[bugid]['impact'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 10, prVeriSWOldResolveInfoDict[bugid]['suggestion'], styleBodyInfoStyle)	
                                        #add by zhaoshie 20150612
					worksheet.write(self.curRow, 11, prVeriSWOldResolveInfoDict[bugid]['rootcause'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 12, prVeriSWOldResolveInfoDict[bugid]['rootcauseDetail'], styleBodyInfoStyle)
					worksheet.write(self.curRow, 13, prVeriSWOldResolveInfoDict[bugid]['Solution'], styleBodyInfoStyle)				
			# modify for newreleasenote by ruifeng 20150115 end

	
	## create release note ResolvePR table
	def createReleaseResolvePR(self, worksheet, prResolveFromCodeInfoDict, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5,styleHighLightBodyStyle):
		self.curRow += 1
		worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'Resolved FR/Defect/Task List', styleReleaseNoteTitleStyle5)
		self.curRow += 1
		worksheet.write(self.curRow, 0, 'NO', styleBodyTitleStyle)
		worksheet.write(self.curRow, 1, 'BUG-ID', styleBodyTitleStyle)
		worksheet.write(self.curRow, 2, 'FR/DEFECT', styleBodyTitleStyle)
		worksheet.write(self.curRow, 3, 'REPORTER', styleBodyTitleStyle)
		worksheet.write(self.curRow, 4, 'STATUS', styleBodyTitleStyle)
		worksheet.write(self.curRow, 5, 'OWNER', styleBodyTitleStyle)
		worksheet.write(self.curRow, 6, 'FUNCTION', styleBodyTitleStyle)
		worksheet.write(self.curRow, 7, 'SHORT-DESC', styleBodyTitleStyle)
		worksheet.write(self.curRow, 8, 'CHANGE-MENUTREE-OR-IMAGE', styleBodyTitleStyle)
		#worksheet.write_merge(self.curRow, self.curRow, 7, 8, 'SHORT-DESC', styleBodyTitleStyle)
		worksheet.write(self.curRow, 9, 'MODULES-IMPACT', styleBodyTitleStyle)
		worksheet.write(self.curRow, 10, 'TEST-SUGGESTION', styleBodyTitleStyle)
                #add by zhaoshie 20150612
		worksheet.write(self.curRow, 11, 'ROOT-CAUSE', styleBodyTitleStyle)
		worksheet.write(self.curRow, 12, 'ROOT-CAUSE-DETAIL', styleBodyTitleStyle)
		worksheet.write(self.curRow, 13, 'SOLUTION', styleBodyTitleStyle)

		nCountFixedPR = 0
		for bugid in sorted(prResolveFromCodeInfoDict.keys()):
			nCountFixedPR += 1
			self.curRow += 1
			if self.adjustSWReportPR(prResolveFromCodeInfoDict[bugid]['reporter']):
				worksheet.write(self.curRow, 0, nCountFixedPR, styleHighLightBodyStyle)
				worksheet.write(self.curRow, 1, str(bugid), styleHighLightBodyStyle)
				worksheet.set_link(self.curRow, 1, self.bugzillaUrlBase % bugid)
				worksheet.write(self.curRow, 2, prResolveFromCodeInfoDict[bugid]['type'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 3, prResolveFromCodeInfoDict[bugid]['reporter'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 4, prResolveFromCodeInfoDict[bugid]['status'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 5, prResolveFromCodeInfoDict[bugid]['ownerinfo'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 6, prResolveFromCodeInfoDict[bugid]['function'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 7, prResolveFromCodeInfoDict[bugid]['desc'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 8, prResolveFromCodeInfoDict[bugid]['menutree_iamge'], styleHighLightBodyStyle)
				#worksheet.write_merge(self.curRow, self.curRow, 7, 8, prResolveFromCodeInfoDict[bugid]['desc'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 9, prResolveFromCodeInfoDict[bugid]['impact'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 10, prResolveFromCodeInfoDict[bugid]['suggestion'], styleHighLightBodyStyle)
                                #add by zhaoshie 20150612
				worksheet.write(self.curRow, 11, prResolveFromCodeInfoDict[bugid]['rootcause'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 12, prResolveFromCodeInfoDict[bugid]['rootcauseDetail'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 13, prResolveFromCodeInfoDict[bugid]['Solution'], styleHighLightBodyStyle)	
			else:
				worksheet.write(self.curRow, 0, nCountFixedPR, styleBodyInfoStyle)
				worksheet.write(self.curRow, 1, str(bugid), styleBodyInfoStyle)
				worksheet.set_link(self.curRow, 1, self.bugzillaUrlBase % bugid)
				worksheet.write(self.curRow, 2, prResolveFromCodeInfoDict[bugid]['type'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 3, prResolveFromCodeInfoDict[bugid]['reporter'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 4, prResolveFromCodeInfoDict[bugid]['status'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 5, prResolveFromCodeInfoDict[bugid]['ownerinfo'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 6, prResolveFromCodeInfoDict[bugid]['function'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 7, prResolveFromCodeInfoDict[bugid]['desc'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 8, prResolveFromCodeInfoDict[bugid]['menutree_iamge'], styleBodyInfoStyle)				
				#worksheet.write_merge(self.curRow, self.curRow, 7, 8, prResolveFromCodeInfoDict[bugid]['desc'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 9, prResolveFromCodeInfoDict[bugid]['impact'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 10, prResolveFromCodeInfoDict[bugid]['suggestion'], styleBodyInfoStyle)
                                #add by zhaoshie 20150612
				worksheet.write(self.curRow, 11, prResolveFromCodeInfoDict[bugid]['rootcause'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 12, prResolveFromCodeInfoDict[bugid]['rootcauseDetail'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 13, prResolveFromCodeInfoDict[bugid]['Solution'], styleBodyInfoStyle)	
		
	
	## create release old verifier SW 
	def createReleaseVeriSWOldResolve(self, worksheet, prVeriSWOldResolveInfoDict, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5,styleHighLightBodyStyle):
		self.curRow += 1
		worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'OLD FIXED PR/CR/FR/PATCH LIST', styleReleaseNoteTitleStyle5)
		self.curRow += 1
		worksheet.write(self.curRow, 0, 'NO', styleBodyTitleStyle)
		worksheet.write(self.curRow, 1, 'BUG-ID', styleBodyTitleStyle)
		worksheet.write(self.curRow, 2, 'PR/CR/FR', styleBodyTitleStyle)
		worksheet.write(self.curRow, 3, 'REPORTER', styleBodyTitleStyle)
		worksheet.write(self.curRow, 4, 'PR-STATUS', styleBodyTitleStyle)
		worksheet.write(self.curRow, 5, 'OWNER', styleBodyTitleStyle)
		worksheet.write(self.curRow, 6, 'FUNCTION', styleBodyTitleStyle)
		worksheet.write(self.curRow, 7, 'TARGET-MILESTONE', styleBodyTitleStyle)
		worksheet.write(self.curRow, 8, 'SHORT-DESC', styleBodyTitleStyle)
		worksheet.write(self.curRow, 9, 'CF-COMMENT-CEA', styleBodyTitleStyle)
		worksheet.write(self.curRow, 10, 'MODULES-IMPACT', styleBodyTitleStyle)
		worksheet.write(self.curRow, 11, 'TEST-SUGGESTION', styleBodyTitleStyle)
		worksheet.write(self.curRow, 12, 'PERSO-RE-GENERATION', styleBodyTitleStyle)
                #add by zhaoshie 20150612
		worksheet.write(self.curRow, 13, 'ROOT-CAUSE', styleBodyTitleStyle)
		worksheet.write(self.curRow, 14, 'ROOT-CAUSE-DETAIL', styleBodyTitleStyle)
		worksheet.write(self.curRow, 15, 'SOLUTION', styleBodyTitleStyle)

		nCountFixedPR = 0
		for bugid in sorted(prVeriSWOldResolveInfoDict.keys()):
			nCountFixedPR += 1
			self.curRow += 1
			if self.adjustSWReportPR(prVeriSWOldResolveInfoDict[bugid]['reporter']):
				worksheet.write(self.curRow, 0, nCountFixedPR, styleHighLightBodyStyle)
				worksheet.write(self.curRow, 1, bugid, styleHighLightBodyStyle)
				worksheet.write(self.curRow, 2, prVeriSWOldResolveInfoDict[bugid]['type'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 3, prVeriSWOldResolveInfoDict[bugid]['reporter'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 4, prVeriSWOldResolveInfoDict[bugid]['status'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 5, prVeriSWOldResolveInfoDict[bugid]['ownerinfo'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 6, prVeriSWOldResolveInfoDict[bugid]['function'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 7, prVeriSWOldResolveInfoDict[bugid]['milestone'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 8, prVeriSWOldResolveInfoDict[bugid]['desc'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 9, prVeriSWOldResolveInfoDict[bugid]['commentcea'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 10, prVeriSWOldResolveInfoDict[bugid]['impact'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 11, prVeriSWOldResolveInfoDict[bugid]['suggestion'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 12, prVeriSWOldResolveInfoDict[bugid]['persoregen'], styleHighLightBodyStyle)
                                #add by zhaoshie 20150612
				worksheet.write(self.curRow, 13, prVeriSWOldResolveInfoDict[bugid]['rootcause'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 14, prVeriSWOldResolveInfoDict[bugid]['rootcauseDetail'], styleHighLightBodyStyle)
				worksheet.write(self.curRow, 15, prVeriSWOldResolveInfoDict[bugid]['Solution'], styleHighLightBodyStyle)	
			else:
				worksheet.write(self.curRow, 0, nCountFixedPR, styleBodyInfoStyle)
				worksheet.write(self.curRow, 1, bugid, styleBodyInfoStyle)
				worksheet.write(self.curRow, 2, prVeriSWOldResolveInfoDict[bugid]['type'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 3, prVeriSWOldResolveInfoDict[bugid]['reporter'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 4, prVeriSWOldResolveInfoDict[bugid]['status'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 5, prVeriSWOldResolveInfoDict[bugid]['ownerinfo'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 6, prVeriSWOldResolveInfoDict[bugid]['function'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 7, prVeriSWOldResolveInfoDict[bugid]['milestone'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 8, prVeriSWOldResolveInfoDict[bugid]['desc'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 9, prVeriSWOldResolveInfoDict[bugid]['commentcea'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 10, prVeriSWOldResolveInfoDict[bugid]['impact'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 11, prVeriSWOldResolveInfoDict[bugid]['suggestion'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 12, prVeriSWOldResolveInfoDict[bugid]['persoregen'], styleBodyInfoStyle)
                                #add by zhaoshie 20150612
				worksheet.write(self.curRow, 13, prVeriSWOldResolveInfoDict[bugid]['rootcause'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 14, prVeriSWOldResolveInfoDict[bugid]['rootcauseDetail'], styleBodyInfoStyle)
				worksheet.write(self.curRow, 15, prVeriSWOldResolveInfoDict[bugid]['Solution'], styleBodyInfoStyle)

	## create Patch xls
	def createReleaseNotePatch(self, worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5):
		self.curRow += 1
		worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'PATCHS(WITHOUT PR/CR/FR)', styleReleaseNoteTitleStyle5)
		self.curRow += 1
		worksheet.write(self.curRow, 0, 'NO', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 1, 4, 'AUTHOR', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 5, self.maxColumn, 'WEB-LINK', styleBodyTitleStyle)
		nCountFixedPR = 0
		for item in sorted(self.patchWithoutPRList):
			self.curRow += 1
			nCountFixedPR += 1
			worksheet.write(self.curRow, 0, nCountFixedPR, styleBodyInfoStyle)
			try:
				worksheet.write_merge(self.curRow, self.curRow, 1, 4, item[0].decode('utf8'), styleBodyInfoStyle)
				worksheet.write_merge(self.curRow, self.curRow, 5, self.maxColumn, Formula('HYPERLINK("%s";"%s")' % (item[2], re.sub('"', '', item[1].decode('utf8')))), styleBodyInfoStyle)
			except:
				pass

	## create Apk xls
	def createReleaseApkMes(self, worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5):
		self.curRow += 1
        	worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'APK Change List', styleReleaseNoteTitleStyle5)
		self.curRow += 1
		worksheet.write(self.curRow, 0, 'NO', styleBodyTitleStyle)
  		worksheet.write_merge(self.curRow, self.curRow, 1, 6, 'APK-NAME', styleBodyTitleStyle)
        	#add and modified by junbiao.chen 20150105
  		worksheet.write(self.curRow, 7, 'IS-REMOVEABLE', styleBodyTitleStyle)
   		worksheet.write(self.curRow, 8, 'ACTION', styleBodyTitleStyle)
  		worksheet.write(self.curRow, 9, 'FR/DEFECT/TASK', styleBodyTitleStyle)
  		worksheet.write_merge(self.curRow, self.curRow, 10 , self.maxColumn, 'REMARK', styleBodyTitleStyle)
		nCountFixedPR = 0
  		self.modifyChangeApkInfoDict()
   		sorted_newestApkChangeInfoDict=sorted(self.newestApkChangeInfoDict.keys())
  		for filename in sorted_newestApkChangeInfoDict:
			self.curRow += 1
			nCountFixedPR += 1
  			isRemoveable=''
   			short_filename=''
  			if filename.lower().find('/removeable/') != -1:
   				isRemoveable='Removeable'
  				short_filename=filename.partition('/Removeable/')[2]
  			elif filename.lower().find('/unremoveable/') != -1:
  				isRemoveable='Unremoveable'
  				short_filename=filename.partition('/Unremoveable/')[2]
				print short_filename
   			else:
   				pass
   			worksheet.write(self.curRow, 0, nCountFixedPR, styleBodyInfoStyle)
  			worksheet.write_merge(self.curRow, self.curRow, 1, 6, short_filename, styleBodyInfoStyle)
  			worksheet.write(self.curRow, 7, isRemoveable, styleBodyInfoStyle)
   			worksheet.write(self.curRow, 8, self.newestApkChangeInfoDict[filename]['action'], styleBodyInfoStyle)
  			worksheet.write(self.curRow, 9, self.newestApkChangeInfoDict[filename]['pr'], styleBodyInfoStyle)
  			worksheet.write_merge(self.curRow, self.curRow, 10, self.maxColumn, self.newestApkChangeInfoDict[filename]['old'], styleBodyInfoStyle)
             #end add and modified by junbiao.chen 20150105
	def modifyChangeApkInfoDict(self):
		tmpChangedApkList=[]
		index=0
		self.newestApkChangeInfoDict={}
		sorted_apkChangeInfoList=sorted(self.apkChangeInfoDict.keys())
		for k in range(0,len(sorted_apkChangeInfoList),1):
			if len(sorted_apkChangeInfoList)==0:
 				break
			filename=sorted_apkChangeInfoList[0]
			tmpChangedApkList.insert(index,[])
			tmpChangedApkList[index].append(filename)
			sorted_apkChangeInfoList.pop(0)
			for i in range(0,len(sorted_apkChangeInfoList),1):
				remainingFilename=sorted_apkChangeInfoList[0]
 				if remainingFilename.lower().partition('_v')[0]==tmpChangedApkList[index][0].lower().partition('_v')[0]:
                #if remainingFilename.lower()[:40]==tmpChangedApkList[index][0].lower()[:40]:
					tmpChangedApkList[index].append(remainingFilename)
					sorted_apkChangeInfoList.pop(0)
				else:
					break                
			index+=1
		for eachChangedApkList in tmpChangedApkList:
            		if len(eachChangedApkList)>0:
                		oldApks=''
                		newest_index=self.findNewestApkIndex(eachChangedApkList)
                		newest_apkName=eachChangedApkList[newest_index]
                		newest_action=self.apkChangeInfoDict[newest_apkName]['action']
                		if 'pr' not in self.apkChangeInfoDict[newest_apkName].keys():
                    			prVal=''
                                        prStr=''
                		else:
                    			newest_pr=self.apkChangeInfoDict[newest_apkName]['pr']
                    			prStr = ', '.join(newest_pr)
		    			if prStr.isdigit():
						prStr=int(prStr)
                		eachChangedApkList.remove(newest_apkName)
                		if newest_action=='Add':
                    			for eachOldApkIndex in range(0,len(eachChangedApkList),1):
                        			if eachChangedApkList[eachOldApkIndex].lower().find('/removeable/') != -1:
                            				eachChangedApkList[eachOldApkIndex]=eachChangedApkList[eachOldApkIndex].partition('/Removeable/')[2]
						elif eachChangedApkList[eachOldApkIndex].lower().lower().find('/unremoveable/') != -1:
                           				eachChangedApkList[eachOldApkIndex]=eachChangedApkList[eachOldApkIndex].partition('/Unremoveable/')[2]
                    			oldApks=','.join(eachChangedApkList)
                		if oldApks=="":
                    			self.newestApkChangeInfoDict[newest_apkName]={'action':newest_action,'pr':prStr,'old':""}
                		else:
                    			self.newestApkChangeInfoDict[newest_apkName]={'action':newest_action,'pr':prStr,'old':"Old:"+oldApks}
			else:
				self.newestApkChangeInfoDict[eachChangedApkList[0]]=self.apkChangeInfoDict[eachChangedApkList[0]]

	def findNewestApkIndex(self,eachChangedApkList):
		theNewestApkName=eachChangedApkList[0]
		theDate=commands.getoutput("echo "+self.apkChangeInfoDict[eachChangedApkList[0]]['date']+" | awk '{print $1,$2,$3,$4,$5}'")
		theNewestApkDate=int(time.mktime(time.strptime(theDate,"%a %b %d %H:%M:%S %Y")))
		theNewestApkAction=self.apkChangeInfoDict[eachChangedApkList[0]]['action']
        	newest_index=0
		index=1
		for index in range(0,len(eachChangedApkList),1):
			theDate=commands.getoutput("echo "+self.apkChangeInfoDict[eachChangedApkList[index]]['date']+" | awk '{print $1,$2,$3,$4,$5}'")
			curApkDate=int(time.mktime(time.strptime(theDate,"%a %b %d %H:%M:%S %Y")))
			curApkAction=self.apkChangeInfoDict[eachChangedApkList[index]]['action']
			if curApkDate>theNewestApkDate:
				theNewestApkName=eachChangedApkList[index]
				theNewestApkDate=curApkDate
				theNewestApkAction=curApkAction
				newest_index=index
			elif curApkDate==theNewestApkDate:
				if curApkAction=='Add':
					theNewestApkName=eachChangedApkList[index]
					theNewestApkDate=curApkDate
					theNewestApkAction=curApkAction
					newest_index=index
		return newest_index
	## create sdm xls
	def createReleaseSdmMes(self, worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5):
                from DBUtils import *
		self.curRow += 1
		worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'SDM Change List', styleReleaseNoteTitleStyle5)
		self.curRow += 1
		worksheet.write(self.curRow, 0, 'NO', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 1, 2, 'SDM-ID', styleBodyTitleStyle)
		worksheet.write(self.curRow, 3, 'FILE-NAME', styleBodyTitleStyle)
		worksheet.write(self.curRow, 4, 'MODULE', styleBodyTitleStyle)
		worksheet.write(self.curRow, 5, 'IS_CUSTO', styleBodyTitleStyle)
		worksheet.write(self.curRow, 6, 'ACTION', styleBodyTitleStyle)
		worksheet.write(self.curRow, 7, 'Default Value'.upper(), styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 8, 9, 'Description'.upper(), styleBodyTitleStyle)
		worksheet.write(self.curRow, 10, 'FR/DEFECT/TASK', styleBodyTitleStyle)
		worksheet.write(self.curRow, 11, 'PATCH_OWNER', styleBodyTitleStyle)
		#worksheet.write(self.curRow, 11, 'FR/DEFECT/TASK STATUS', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow,self.curRow, 12, self.maxColumn,'comment', styleBodyTitleStyle)
		nCountFixedPR = 0
		sorted_sdmChangeInfoDict=sorted(self.sdmChangeInfoDict)
		tempPlfDict = {}
		prPlfVal = []
   		#for (sdm, sdminfo) in self.sdmChangeInfoDict.items():
		mysqlConn=MySQLdb.connect('172.24.61.199', port=3306, user='scm_tools', passwd='SCM_TOOLS123!', db='bugs', charset='gbk')
 		for sdm in sorted_sdmChangeInfoDict:
			tem_sdm = sdm
			if "/plf" in tem_sdm:
				tem_sdm = tem_sdm.replace("/plf",'')
			self.curRow += 1
			nCountFixedPR += 1
			worksheet.write(self.curRow, 0, nCountFixedPR, styleBodyInfoStyle)
			worksheet.write_merge(self.curRow, self.curRow, 1, 2, tem_sdm.split('/', 1)[1].split('/', 1)[1], styleBodyInfoStyle)
			worksheet.write(self.curRow, 3, tem_sdm.split('/', 2)[1], styleBodyInfoStyle)
			worksheet.write(self.curRow, 4, re.sub('\.[pP][lL][fF]$', '', tem_sdm.split('/', 1)[0]), styleBodyInfoStyle)
            		#worksheet.write(self.curRow, 6, sdminfo['action'], styleBodyInfoStyle)
            		#worksheet.write_merge(self.curRow, self.curRow, 7, 8, sdminfo['value'], styleBodyInfoStyle)
            		worksheet.write(self.curRow, 5, self.sdmChangeInfoDict[sdm]['custo'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 6, self.sdmChangeInfoDict[sdm]['action'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 7, self.sdmChangeInfoDict[sdm]['value'], styleBodyInfoStyle)
			worksheet.write_merge(self.curRow, self.curRow, 8, 9, self.sdmChangeInfoDict[sdm]['desc'], styleBodyInfoStyle)

			#for(filename,prList) in self.sdmChangeToPRDict.items():
			if 'pr' not in self.sdmChangeInfoDict[sdm].keys():
				prPlfVal = []
				prtypeid = ''
				prPlfState = []
				prPlfStr = ''
			else:
				prPlfVal = []
				prtypeid = ''
				prPlfState = []
				prPlfStr = ''
				prPlfStr = ','.join(self.sdmChangeInfoDict[sdm]['pr'])
				bugdb = self.getDefectTypeStatus(mysqlConn,prPlfStr)
				for bugid in bugdb.keys():
					strings = ','.join(prPlfVal)
					bugidstring = str(bugid)
					print bugidstring
					if not set(bugidstring).difference(strings):
						break
					else:
						prtypeid = '%s%s:%s' %(bugdb[bugid]['type'],bugid,bugdb[bugid]['status'])
						prPlfVal.append(prtypeid) 
                        prPlfValstring = ','.join(prPlfVal)
                        #prPlfStatestring = ','.join(prPlfState)
			worksheet.write(self.curRow, 10, prPlfValstring, styleBodyInfoStyle)
			#worksheet.write(self.curRow, 11, prPlfStatestring, styleBodyInfoStyle)
			if sdm in self.sdmauthor.keys():
				worksheet.write(self.curRow, 11, self.sdmauthor[sdm][0], styleBodyInfoStyle)
				if sdm in self.updatesdmChangeInfoDict.keys():			
					self.updatesdmChangeInfoDict[sdm]['author'] = self.sdmauthor[sdm][0]
					self.updatesdmChangeInfoDict[sdm]['pr'] = self.sdmChangeInfoDict[sdm]['pr']
					self.updatesdmChangeInfoDict[sdm]['comment'] = self.sdmChangeInfoDict[sdm]['comment'] 
					if 'url' not in self.updatesdmChangeInfoDict[sdm].keys():
						self.updatesdmChangeInfoDict[sdm]['url'] = []
						self.updatesdmChangeInfoDict[sdm]['url'] = self.sdmChangeToURLDict[sdm]
					else:
						self.updatesdmChangeInfoDict[sdm]['url'] = self.updatesdmChangeInfoDict[sdm]['url'] + self.sdmChangeToURLDict[sdm]
			else:
				worksheet.write(self.curRow, 11, '', styleBodyInfoStyle)		
			if "comment" in self.sdmChangeInfoDict[sdm].keys():
				worksheet.write_merge(self.curRow,self.curRow,  12, self.maxColumn, self.sdmChangeInfoDict[sdm]['comment'], styleBodyInfoStyle)
			else:
				worksheet.write_merge(self.curRow, self.curRow, 12, self.maxColumn, '',styleBodyInfoStyle)

	def createReleaseOGPR(self,worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5):
		self.curRow += 1
       		worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'OnGoing FR/Defect  Status', styleReleaseNoteTitleStyle5)
        	self.curRow += 1
        	worksheet.write_merge(self.curRow, self.curRow, 0, 1, self.OGPRTitleList[0], styleBodyTitleStyle)
        	worksheet.write_merge(self.curRow, self.curRow, 2, 3, self.OGPRTitleList[1], styleBodyTitleStyle)
        	worksheet.write_merge(self.curRow, self.curRow, 4, 5, self.OGPRTitleList[2], styleBodyTitleStyle)
        	worksheet.write_merge(self.curRow, self.curRow, 6, 7, self.OGPRTitleList[3], styleBodyTitleStyle)
        	worksheet.write_merge(self.curRow, self.curRow, 8, 9, self.OGPRTitleList[4], styleBodyTitleStyle)
        	worksheet.write_merge(self.curRow, self.curRow, 10, 11, self.OGPRTitleList[5], styleBodyTitleStyle)
        	worksheet.write_merge(self.curRow,self.curRow, 12, self.maxColumn,  self.OGPRTitleList[6], styleBodyTitleStyle)
        	self.curRow += 1
        	worksheet.write_merge(self.curRow, self.curRow, 0, 1, self.prOGFromDBDict[self.OGPRTitleList[0]], styleBodyInfoStyle)
        	worksheet.write_merge(self.curRow, self.curRow, 2, 3, self.prOGFromDBDict[self.OGPRTitleList[1]], styleBodyInfoStyle)
        	worksheet.write_merge(self.curRow, self.curRow, 4, 5, self.prOGFromDBDict[self.OGPRTitleList[2]], styleBodyInfoStyle)
        	worksheet.write_merge(self.curRow, self.curRow, 6, 7, self.prOGFromDBDict[self.OGPRTitleList[3]], styleBodyInfoStyle)
        	worksheet.write_merge(self.curRow, self.curRow, 8, 9, self.prOGFromDBDict[self.OGPRTitleList[4]], styleBodyInfoStyle)
        	worksheet.write_merge(self.curRow, self.curRow, 10, 11, self.prOGFromDBDict[self.OGPRTitleList[5]], styleBodyInfoStyle)
        	worksheet.write_merge(self.curRow, self.curRow, 12, self.maxColumn,self.prOGFromDBDict[self.OGPRTitleList[6]], styleBodyInfoStyle)
	def createReleaseOGHomoDefect(self,worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5):
		OGHomoTitle = ['NO','BUG_ID','CU_REF','REPORTER','STATUS','OWNER','FUNCTION','SHORT_DESC','COMPONENT','CF_COMMENT_CEA']
		self.curRow += 1
		worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'OnGoing HOMO FR/Defect/Task  List', styleReleaseNoteTitleStyle5)
		self.curRow += 1
		for i in range(4):
			worksheet.write(self.curRow, i, OGHomoTitle[i], styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 4, 5, OGHomoTitle[4], styleBodyTitleStyle)
		worksheet.write(self.curRow, 6, OGHomoTitle[5], styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 7, 8, OGHomoTitle[6], styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 9, 10, OGHomoTitle[7], styleBodyTitleStyle)
		worksheet.write(self.curRow, 11, OGHomoTitle[8], styleBodyTitleStyle)
		worksheet.write_merge(self.curRow, self.curRow, 12,self.maxColumn, OGHomoTitle[9], styleBodyTitleStyle)
		nCountFixedPR = 0
		for bugid in sorted(self.OGHomoDefectDict.keys()):
			nCountFixedPR += 1
			self.curRow += 1
			worksheet.write(self.curRow, 0, nCountFixedPR, styleBodyInfoStyle)
			worksheet.write(self.curRow, 1, str(bugid), styleBodyInfoStyle)
			worksheet.set_link(self.curRow, 1, self.bugzillaUrlBase % bugid)
			worksheet.write(self.curRow, 2, self.OGHomoDefectDict[bugid][OGHomoTitle[2]], styleBodyInfoStyle)
			worksheet.write(self.curRow, 3, self.OGHomoDefectDict[bugid][OGHomoTitle[3]], styleBodyInfoStyle)
			worksheet.write_merge(self.curRow,self.curRow, 4, 5, self.OGHomoDefectDict[bugid][OGHomoTitle[4]], styleBodyInfoStyle)
			worksheet.write(self.curRow, 6, self.OGHomoDefectDict[bugid][OGHomoTitle[5]], styleBodyInfoStyle)
			worksheet.write_merge(self.curRow,self.curRow, 7, 8, self.OGHomoDefectDict[bugid][OGHomoTitle[6]], styleBodyInfoStyle)
			worksheet.write_merge(self.curRow, self.curRow, 9, 10, self.OGHomoDefectDict[bugid][OGHomoTitle[7]], styleBodyInfoStyle)
			worksheet.write(self.curRow, 11, self.OGHomoDefectDict[bugid][OGHomoTitle[8]], styleBodyInfoStyle)
			worksheet.write_merge(self.curRow, self.curRow, 12,self.maxColumn, self.OGHomoDefectDict[bugid][OGHomoTitle[9]], styleBodyInfoStyle)
	## defination worksheet width
	def createReleaseWidthXls(self, worksheet):
		worksheet.col(0).width = 1500
		worksheet.col(1).width = 3000
		worksheet.col(2).width = 3000
		worksheet.col(3).width = 4000
		worksheet.col(4).width = 3000
		worksheet.col(5).width = 4000
		worksheet.col(6).width = 5000
		worksheet.col(7).width = 5000
		worksheet.col(8).width = 5000
		worksheet.col(9).width = 5000
		worksheet.col(10).width = 10000
                #add zhaoshie 20150612
		worksheet.col(11).width = 4000
		worksheet.col(12).width = 8000
		worksheet.col(13).width = 8000
		worksheet.set_normal_magn(90)

	def createDeliveredWidthXls(self, worksheet):
		worksheet.col(0).width = 1500
		worksheet.col(1).width = 3000
		worksheet.col(2).width = 3000
		worksheet.col(3).width = 5000
		worksheet.col(4).width = 3000
		worksheet.col(5).width = 5000
		worksheet.col(6).width = 4000
		worksheet.col(7).width = 4000
		worksheet.col(8).width = 5000		
		worksheet.col(9).width = 10000
		worksheet.set_normal_magn(90)

	def createWifiCheckWidthXls(self, worksheet):
		worksheet.col(0).width = 1500
		worksheet.col(1).width = 5000
		worksheet.col(2).width = 3000
		worksheet.col(3).width = 3000
		worksheet.col(4).width = 5000
		worksheet.col(5).width = 3000
		worksheet.col(6).width = 3000
		worksheet.col(7).width = 6000
		worksheet.set_normal_magn(90)
	## get curVerTime and lastVerTimer
	def getCurrAndLaseTime(self, conf):
		maniPrefix = conf.getConf('manifestprefix', 'Prefix dir for manifest files')
		pushdir('.repo/manifests/'+maniPrefix)
		curVerTimeStr = ''
		lastVerTimeStr = ''
		for line in commands.getoutput('git log --pretty=format:"%%ci|%%s" v%s.xml' % conf.getConf('version', 'project current version')).split('\n'):
			match = re.match('^(\d\d\d\d-\d\d-\d\d\s+\d\d:\d\d:\d\d)\s+\+\d+\|create\s[^\s]+\.xml\sby\sint_jenkins', line)
			if match:
				curVerTimeStr = match.group(1)
				break
		for line in commands.getoutput('git log --pretty=format:"%%ci|%%s" v%s.xml' % conf.getConf('baseversion', 'project base version')).split('\n'):
			match = re.match('^(\d\d\d\d-\d\d-\d\d\s+\d\d:\d\d:\d\d)\s+\+\d+\|create\s[^\s]+\.xml\sby\sint_jenkins', line)
			if match:
				lastVerTimeStr = match.group(1)
				break
		popdir()
		if not lastVerTimeStr and conf.getConf('isBigVersion', 'version is big version') == 'yes':
			lastVerTimeStr = conf.getConf('lastVerTimeStr', 'The time you created last manifest time,format:2016-8-15 12:00:00')
		if not curVerTimeStr and conf.getConf('isBigVersion', 'version is big version') == 'yes':
			curVerTimeStr = conf.getConf('curVerTimeStr', 'The time you created current manifest time,format:2016-8-15 12:00:00')
		print 'Last manifest time: %s' % lastVerTimeStr
		print 'Current manifest time: %s' % curVerTimeStr
		return curVerTimeStr,lastVerTimeStr
		
	def getApkVersion(self,apkname):
		digitsInApk=[]
		index=0
		start_index=0
		end_index=0
		version=''
		for i in range(0,len(apkname),1):
			index+=1
			if index>len(apkname):
				break
			if apkname[index-1].isdigit():
				start_index=index-1
				for j in range(index,len(apkname),1):
					if apkname[j]!='.' and not apkname[j].isdigit():
						if apkname[j-1]=='.':
                                                	end_index=j-1
                                        	else:
                                                	end_index=j
                                        	index=j
                                        	digitsInApk.append(apkname[start_index:end_index])
                                        	break
                	else:
                        	continue
        	for each in digitsInApk:
                	if each.find('.')!=-1:
                        	version=each
        	return version
	#start add by yangrenzhi2015-2-5
	def createReleaseNoteAllDeliveredBugs(self, worksheet, allDeliveredBugsInfoDict):
		styleBodyInfoStyle = self.getBodyInfoStyle()
		styleBodyInfoStyleMan = self.getBodyInfoStyle(20)
		styleBodyTitleStyle = self.getBodyTitleStyle()
		styleReleaseNoteTitleStyle5 = self.getReleaseNoteTitleStyle(5)
		styleHighLightBodyStyle = self.getHighLightBodyStyle(10)
		# modify for newreleasenote by ruifeng 20150115 begin
		if allDeliveredBugsInfoDict:
			self.createReleaseDelivered(worksheet, allDeliveredBugsInfoDict, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5,styleHighLightBodyStyle)
		else:
			pass
                self.createDeliveredWidthXls(worksheet)

	def createReleaseDelivered(self,worksheet, allDeliveredBugsInfoDict, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5,styleHighLightBodyStyle):
		self.maxColumn = 9
		worksheet.write_merge(self.curRow2, self.curRow2, 0, self.maxColumn, 'All DELIVERED BUGS List', styleReleaseNoteTitleStyle5)
		self.curRow2 += 1
		worksheet.write(self.curRow2, 0, 'NO', styleBodyTitleStyle)
		worksheet.write(self.curRow2, 1, 'BUG-ID', styleBodyTitleStyle)
		worksheet.write(self.curRow2, 2, 'PR/FR/CR', styleBodyTitleStyle)
		worksheet.write(self.curRow2, 3, 'REPORTER', styleBodyTitleStyle)
		worksheet.write(self.curRow2, 4, 'STATUS', styleBodyTitleStyle)
		worksheet.write(self.curRow2, 5, 'OWNER', styleBodyTitleStyle)
		worksheet.write(self.curRow2, 6, 'FUNCTION', styleBodyTitleStyle)
		worksheet.write(self.curRow2, 7, 'COMMENT-CEA', styleBodyTitleStyle)
		worksheet.write_merge(self.curRow2, self.curRow2, 8, self.maxColumn, 'SHORT-DESC', styleBodyTitleStyle)
        # modify for newreleasenote by ruifeng 20150115 begin
  		nCountFixedPR = 0
		if allDeliveredBugsInfoDict:
			for bugid in sorted(allDeliveredBugsInfoDict.keys()):
				nCountFixedPR += 1
				self.curRow2 += 1
				if self.adjustSWReportPR(allDeliveredBugsInfoDict[bugid]['reporter']):
					worksheet.write(self.curRow2, 0, nCountFixedPR, styleHighLightBodyStyle)
					worksheet.write(self.curRow2, 1, str(bugid), styleHighLightBodyStyle)
					worksheet.set_link(self.curRow2, 1, self.bugzillaUrlBase % bugid)
					worksheet.write(self.curRow2, 2, allDeliveredBugsInfoDict[bugid]['type'], styleHighLightBodyStyle)
					worksheet.write(self.curRow2, 3, allDeliveredBugsInfoDict[bugid]['reporter'], styleHighLightBodyStyle)
					worksheet.write(self.curRow2, 4, allDeliveredBugsInfoDict[bugid]['status'], styleHighLightBodyStyle)
					worksheet.write(self.curRow2, 5, allDeliveredBugsInfoDict[bugid]['ownerinfo'], styleHighLightBodyStyle)
					worksheet.write(self.curRow2, 6, allDeliveredBugsInfoDict[bugid]['function'], styleHighLightBodyStyle)
					worksheet.write(self.curRow2, 7, allDeliveredBugsInfoDict[bugid]['commentcea'], styleHighLightBodyStyle)
					worksheet.write_merge(self.curRow2, self.curRow2, 8, self.maxColumn, allDeliveredBugsInfoDict[bugid]['desc'], styleHighLightBodyStyle)
				else:
					worksheet.write(self.curRow2, 0, nCountFixedPR, styleBodyInfoStyle)
					worksheet.write(self.curRow2, 1, str(bugid), styleBodyInfoStyle)
					worksheet.set_link(self.curRow2, 1, self.bugzillaUrlBase % bugid)
					worksheet.write(self.curRow2, 2, allDeliveredBugsInfoDict[bugid]['type'], styleBodyInfoStyle)
					worksheet.write(self.curRow2, 3, allDeliveredBugsInfoDict[bugid]['reporter'], styleBodyInfoStyle)
					worksheet.write(self.curRow2, 4, allDeliveredBugsInfoDict[bugid]['status'], styleBodyInfoStyle)
					worksheet.write(self.curRow2, 5, allDeliveredBugsInfoDict[bugid]['ownerinfo'], styleBodyInfoStyle)
					worksheet.write(self.curRow2, 6, allDeliveredBugsInfoDict[bugid]['function'], styleBodyInfoStyle)
					worksheet.write(self.curRow2, 7, allDeliveredBugsInfoDict[bugid]['commentcea'], styleBodyInfoStyle)
					worksheet.write_merge(self.curRow2, self.curRow2, 8, self.maxColumn, allDeliveredBugsInfoDict[bugid]['desc'], styleBodyInfoStyle)
				##end add by renzhiyang 2015-02-5
	def createReleaseNoteWifiCheck(self, worksheetWifiCheck):
		self.curRow = -1
                self.maxColumn = 7
		styleBodyInfoStyle = self.getBodyInfoStyle()
		styleBodyInfoStyleMan = self.getBodyInfoStyle(20)
		styleBodyTitleStyle = self.getBodyTitleStyle()
		styleReleaseNoteTitleStyle5 = self.getReleaseNoteTitleStyle(5)
		styleHighLightBodyStyle = self.getHighLightBodyStyle(10)
		title = u"功耗影响"
		self.curRow += 1
		worksheetWifiCheck.write_merge(self.curRow, self.curRow, 0, self.maxColumn, title, styleReleaseNoteTitleStyle5)
		self.curRow += 1
		worksheetWifiCheck.write(self.curRow, 0, 'NO', styleBodyTitleStyle)
		worksheetWifiCheck.write(self.curRow, 1, 'FileDir', styleBodyTitleStyle)
		worksheetWifiCheck.write(self.curRow, 2, 'GitName', styleBodyTitleStyle)
		worksheetWifiCheck.write(self.curRow, 3, 'KeyWord', styleBodyTitleStyle)
		worksheetWifiCheck.write(self.curRow, 4, 'Affect_Func', styleBodyTitleStyle)
		worksheetWifiCheck.write(self.curRow, 5, 'Changed', styleBodyTitleStyle)
		worksheetWifiCheck.write(self.curRow, 6, 'BugID', styleBodyTitleStyle)
		worksheetWifiCheck.write(self.curRow, 7, 'WebLink', styleBodyTitleStyle)
		if not self.allNeedCheckFileInfoAboutWifi.keys():
			self.curRow += 1
		count = 1
		for keyNumber in sorted(self.allNeedCheckFileInfoAboutWifi.keys()):
			self.curRow += 1
			worksheetWifiCheck.write(self.curRow, 0, count, styleBodyInfoStyle)
			FileDir = self.allNeedCheckFileInfoAboutWifi[keyNumber]['filename']
			if 'all' in FileDir:
				FileDirAction = u'All files'
			else:
				FileDirAction = FileDir
			worksheetWifiCheck.write(self.curRow, 1, FileDirAction, styleBodyInfoStyle)
			worksheetWifiCheck.write(self.curRow, 2, self.allNeedCheckFileInfoAboutWifi[keyNumber]['gitname'], styleBodyInfoStyle)
			worksheetWifiCheck.write(self.curRow, 3, self.allNeedCheckFileInfoAboutWifi[keyNumber]['special_word'], styleBodyInfoStyle)	
			worksheetWifiCheck.write(self.curRow, 4, self.allNeedCheckFileInfoAboutWifi[keyNumber]['description'], styleBodyInfoStyle)
			if 'changed' in self.allNeedCheckFileInfoAboutWifi[keyNumber].keys():
				if self.allNeedCheckFileInfoAboutWifi[keyNumber]['changed'] == 'YES':
					worksheetWifiCheck.write(self.curRow, 5, self.allNeedCheckFileInfoAboutWifi[keyNumber]['changed'], styleHighLightBodyStyle)
				else:
					worksheetWifiCheck.write(self.curRow, 5, self.allNeedCheckFileInfoAboutWifi[keyNumber]['changed'], styleBodyInfoStyle)
			else:
				worksheetWifiCheck.write(self.curRow, 5, 'NO', styleBodyInfoStyle)
				
			if 'BugID' in self.allNeedCheckFileInfoAboutWifi[keyNumber].keys():
				worksheetWifiCheck.write(self.curRow, 6, self.allNeedCheckFileInfoAboutWifi[keyNumber]['BugID'], styleBodyInfoStyle)
			if 'commitUrl' in self.allNeedCheckFileInfoAboutWifi[keyNumber].keys():		
				worksheetWifiCheck.write(self.curRow, 7, '\n'.join(self.allNeedCheckFileInfoAboutWifi[keyNumber]['commitUrl']), styleBodyInfoStyle)
			count = count + 1
		self.createWifiCheckWidthXls(worksheetWifiCheck)
