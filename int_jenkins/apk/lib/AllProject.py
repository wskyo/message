#!/usr/bin/python
#coding=utf-8

import os
import sys
import re
import datetime
import tempfile
from Utils import *
from Config import *
from UserInfo import *
from ChangeUtils import *
from ApkMailUtils import *
from ReleaseStyle import *
from SheetUtils import *
from DBUtils import *
from DBUtilsALM import *
import glob
import commands
import mechanize
import email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.image import MIMEImage
from pyExcelerator import *
import MySQLdb
import xml.dom.minidom
from time import strftime, localtime
import time
import curses
import datetime
import xlrd
import os.path


class AllProject(ChangeUtils, ReleaseStyle,ApkMailUtils,DBUtils,DBUtilsALM,SheetUtils):
	gitNameVersion = {}
	gitVersionForEmail = {}
	oneProductIdNum = ''
	oneProductIdNumALM = ''
	tagcurversion = ''
	taglastversion = ''
	tagDict = {}
	apkDeliveredBugs = {}
	apkSWNoDeliveredBugs = {}
	prNeedDelivHash = {}
	test = ''
	#mysqlConn = MySQLdb.connect('172.24.61.199', port=3306, user='scm_tools', passwd='SCM_TOOLS123!', db='bugs', charset='gbk')
	def run(self):
		self.gitComment = []
		self.curDict = {}
		self.lastDict = {}
		self.dirverPRDict = {}
		self.nChanged = 0
		self.nCommit = 0 
		self.defRemote = None
		self.AppList = ''
		self.tempdir = ''
		self.authorStr = ''
		self.patchWithoutPRList = []
		self.gitconf = ''		
		self.buildDir = ''
		self.version = ''		
		self.baseVersion = ''
		self.appname = ''
		self.SingleApkBugs = {}		
		self.appPlfDict	= {}	
		self.AlmCheckDict = {}
		self.RelatedApkAlmCheckDict = {}
		self.ProjetcAndSPM = {}
		self.bugzillaUrlBase = ''
		self.projectAssigenID = {}
		self.needAddCommentDefect = []	
		self.needAddCommentProjectDefectDict = {}	
		self.sdmChangeInfoDict = {}
		self.sdmChangeInfoDictForPlf = {}
		self.sdmChangeToPRDict = {}
		self.sdmauthor = {}
		self.plfChangeInfoDict = {}	
		self.maincodeProjectList = {}
		self.wcustores_gitpath = ''
		self.wprocedures_gitpath = ''
		##get all config from here 
		conf = Config();
		## get all args from commands
		conf.addFromArg(sys.argv[1:])
		self.test = conf.getConf('test', 'yes for email test,else for release email')
		self.issssignment = conf.getConf('issssignment', 'create Assignment or no ','yes')
		self.ishomo = conf.getConf('ishomo', 'no for home,will to auto upload apk to project','yes')
		self.isgerrit = conf.getConf('isgerrit', 'no for home,will to auto upload apk to project','no')
		self.projectname = conf.getConf('projectname', 'project name','no')
		self.test = self.test.upper()
		self.apkInfo = {}
		## get all appname and version information
		if not re.search("YES", self.test):
			self.gitVersionFromArg(conf)	
			self.apkInfo = self.gitNameVersion.copy()
			self.gitVersionForEmail = self.gitNameVersion.copy()

		else:
			self.appname = conf.getConf('appname','the app name')
			self.curversion = conf.getConf('version','Current version of this app')
			self.lasversion = conf.getConf('baseversion','last version of this app')
			if self.appname not in self.apkInfo.keys():
				self.apkInfo[self.appname] = []
			self.apkInfo[self.appname] = [self.curversion, self.lasversion]
			self.gitNameVersion = self.apkInfo.copy()

		self.curversion = conf.getConf('version','Current version of this app','no')
		self.lasversion = conf.getConf('baseversion','last version of this app','no')
		workbook = xlrd.open_workbook('/local/int_jenkins/apk/conf/generic_apk.xls')
		for apkname in sorted(self.apkInfo.keys()):
			sheetname = 'apk_info'
			related_apk_name = ''
			self.GetInfoFromXlsConf(workbook, apkname,sheetname,self.AlmCheckDict,self.maincodeProjectList)
			if self.AlmCheckDict[apkname]['related_apk_name']:
				sheetname = 'releated_apk'
				related_apk_name = self.AlmCheckDict[apkname]['related_apk_name']				
				for eachRelatedApk in related_apk_name.strip().split(','):
					if not eachRelatedApk:
						continue
					self.GetInfoFromXlsConf(workbook, eachRelatedApk,sheetname,self.RelatedApkAlmCheckDict,self.maincodeProjectList)
					if eachRelatedApk not in self.AlmCheckDict.keys():
						self.AlmCheckDict[eachRelatedApk] = self.RelatedApkAlmCheckDict[eachRelatedApk]
					#if not re.search("YES", self.test):
					if eachRelatedApk not in self.gitNameVersion.keys():
							#self.gitNameVersion[eachRelatedApk] = self.gitNameVersion[apkname]
						if self.curversion != 'no':
						    self.gitNameVersion[eachRelatedApk] = [self.curversion,self.lasversion]
						else:
						    self.gitNameVersion[eachRelatedApk] = self.getVerNumber(conf,eachRelatedApk)		
		## init conf from xls table and check some message
		self.initConfFromXls(conf)
		## init other message
		self.initSomeConf(conf)
		self.tempdir = tempfile.mkdtemp('SuperSpam', 'temp', '/tmp')
		buildDir = "/local/build/genericapp/"
		if not os.path.isdir(buildDir):
			docmd('mkdir %s' % buildDir)
		self.buildDir = buildDir
                self.tempdir = conf.getConf('tempdir','tmp path',self.tempdir)	
		pushdir(self.buildDir)
		extAttachFileStr = conf.getConf('extattach', 'External attach files', 'none')
		if  extAttachFileStr != 'none':
			for fileName in extAttachFileStr.split(','):
				docmd('cp %s %s/attach' % (self.buildDir + '/' + fileName.strip(), self.tempdir))
		docmd('cp %smisc/SuperSpamReleaseMailFootLogoOneTouch.jpg %s/image/ReleaseMailLogo.jpg' % (getToolPath(), self.tempdir))


		## create mail html
		html = ''
		html_assignment = ''
		html_apkpush = '' 		
		html += self.getMailHeadHtml(conf)		
		pushdir(self.buildDir)
		html_forchangeList = self.getChangeList(conf)	
		self.sdmChangeInfoDictForPlf = self.sdmChangeInfoDict.copy()
		html += self.getMailBodyHtml(conf)
		self.needAddCommentProjectDefectDict = copy.deepcopy(self.prNotGenericApkFromCodeDict)
	
		## start to create releasenote for each app
                print "## start to create releasenote for each app"
		pushdir(self.buildDir)
		if re.search("YES",self.test) and self.AlmCheckDict[self.appname]['creative_apk'] != 'yes':
			print "when test,no need releasenote"
			for eachApk in self.gitNameVersion.keys():
				apkversion = self.gitNameVersion[eachApk][0]
				#docmd('python /local/int_jenkins/misc/insertReleaseinfoWeeklydb.py %s %s ' % (eachApk,apkversion))
				release_type = 'start_build'
				docmd('python /local/int_jenkins/misc/CreateTaskForRealeaseVersionInPRSM.py %s %s %s' % (eachApk,apkversion,release_type))
		else:
			gitNameVersion = self.gitNameVersion.copy()
              		for name in sorted(gitNameVersion.keys()):
				if self.related_apk_change_dict[name] == False and conf.getConf('exitnonewchange', 'Exit if no new change from last version <yes|no>', 'yes') == 'yes':
					continue
				if 'Bugzilla' in self.AlmCheckDict[name].values():
					self.bugzillaUrlBase = 'http://bugzilla.tcl-ta.com/show_bug.cgi?id=%s'
				elif 'ALM' in self.AlmCheckDict[name].values():
					self.bugzillaUrlBase = 'https://alm.tclcom.com:7003/im/issues?selection=%s'
				self.appname = name			
				versions = gitNameVersion.pop(name)
				self.version = versions[0]	
				self.baseVersion = versions[1]			
				if self.appname in self.allAppPrDict.keys():			
					self.SingleApkBugs = self.allAppPrDict.pop(self.appname)					
				self.appPlfDict = {}					
				if self.appname in self.sdmChangeInfoDict.keys():
					self.appPlfDict = self.sdmChangeInfoDict.pop(self.appname)
				self.createReleaseNote(conf, self.SingleApkBugs)
				if self.AlmCheckDict[self.appname]['creative_apk'] != 'yes':
					integrator = 'yan.xiong'
					comment = 'gapk weekly release'
					#docmd('python /local/int_jenkins/misc/insertReleaseinforWhenEmail.py "%s" "%s" "%s" "%s"' %(self.appname,self.version,comment,integrator))
					release_type = 'release'	
					docmd('python /local/int_jenkins/misc/CreateTaskForRealeaseVersionInPRSM.py "%s" "%s" "%s" "%s" "%s"' %(self.appname,self.version,release_type,comment,integrator))		

			
		##move apk from test dir to release dir 
		if re.search("YES",self.test):
			print "No need to upload apk to teleweb when emailing for test"
		else:

			moveApkVersions = self.gitNameVersion.copy()			
			for appname in moveApkVersions.keys():
				if self.related_apk_change_dict[appname] == False and conf.getConf('exitnonewchange', 'Exit if no new change from last version <yes|no>', 'yes') == 'yes':
					continue
				currentversion = moveApkVersions.pop(appname)
				version = currentversion[0]
				##delivered all bugs need delivered	
				if appname in self.prNeedDelivHash.keys():
					print "Now start to delivered all bugs need delivered"
					if 'Bugzilla' in self.AlmCheckDict[appname].values():						
						self.deliverPR(conf, self.prNeedDelivHash[appname],version)
					elif 'ALM' in self.AlmCheckDict[appname].values():
						self.deliverPRALM(conf, self.prNeedDelivHash[appname],version)
				if 'ALM' in self.AlmCheckDict[appname].values() and 'branch' in self.AlmCheckDict[appname].keys() :
					self.create_releasenote(conf,version)				
				
				if appname in self.AlmCheckDict.keys() and "project" in self.AlmCheckDict[appname].keys():
					self.copyApkToBuildServer(appname,version)
					currenttime = (datetime.datetime.now() + datetime.timedelta(days=3)).strftime('%b %d, %Y')
					html_apkpush += '<br align=\'Left\'><B>%s</B> APK v%s has been pushed to the following branch code:' % (appname,version)
					for item in self.AlmCheckDict[appname]['project']:
						project = item.values()[0]['project']
						branch = item.values()[0]['almbranch']
						codeBranch = item.values()[0]['code_branch']
						mtkProjectFelderList = item.values()[0]['mtkProject']
						signedProjectDir = item.values()[0]['signapkdir']
						unsignedProjectDir = item.values()[0]['unsignapkdir']
						custors = item.values()[0]['cu_gitweb']
						wprocedures = item.values()[0]['wp_gitweb']
						plfFeldorUnderApkCode = item.values()[0]['plf_feldor_in_apk']
						notification_user = self.AlmCheckDict[appname]['notification_recerive_user']
						commentDefectList = []
						projectItem = ''
						otherNeedAddCommentList = [] 
						homo = ''
						homo = item.values()[0]['homo']
						#add by lyf  2017-03-30
						if self.ishomo == 'no':
						    homo = 'no'
						#end by lyf 2017-03-30
						print "The homo value is %s" % homo
						self.getNeedAddassignmentIDToComment(project, appname, branch)
						if appname not in self.needAddCommentProjectDefectDict.keys():
							self.needAddCommentProjectDefectDict[appname] = []			
						commentDefectList, otherNeedAddCommentList = self.diffDefect(project, self.needAddCommentProjectDefectDict[appname], self.needAddCommentDefect, branch)
						if homo == 'no':
							print "The project need not to create assigment, push apk to code and edit resolve defect to verified SW"			
							self.wprocedures_gitpath = item.values()[0]['wprocedures']
							self.wcustores_gitpath = item.values()[0]['wcustores']							
							self.GetEachProjectCode(item.values()[0]['wprocedures'],item.values()[0]['wcustores'], item.keys()[0], item.values()[0]['code_branch'])
							html_apkpush += self.getHtml(item.keys()[0], codeBranch)						
							html_apkpush += self.pushApkToCode(appname, version, item.keys()[0], codeBranch, mtkProjectFelderList,signedProjectDir,unsignedProjectDir,custors)
							html_apkpush += self.push_MKFile_Changed_ToCode(appname, version, item.keys()[0], codeBranch, mtkProjectFelderList,wprocedures)			
							if plfFeldorUnderApkCode:
								if appname in self.sdmChangeInfoDictForPlf.keys() and self.sdmChangeInfoDictForPlf[appname]:
									html_apkpush += self.copyPlfFile_From_APKCode_To_ProjectCode(appname,version, item.keys()[0], codeBranch, wprocedures,plfFeldorUnderApkCode, mtkProjectFelderList)
							if commentDefectList:
								self.getEdit_ResolvedAPKDefectForProjectBeforeHome(commentDefectList, appname, version, item.keys()[0], codeBranch)						 
							continue
	
						#add by lyf control create or not  2017-03-30
						if self.issssignment == 'no':
						    continue
						#end by lyf add by lyf control create or not 2017-03-30
						assignDict = {}
						assignDict['Summary'] = "[Qualify][HZ Generic APK][%s v%s]" % (appname,version)
						assignDict['Project'] = project
						assignDict['State'] = 'Assigned'
						assignDict['Priority'] = 'P0 (Urgent)'
						assignDict['Deadline'] = currenttime 
						assignDict['Description'] = "This assignment is for %s(ALM branch:%s)." % (project, ','.join(branch))
						if appname == "JrdGallery2" or appname == "JrdLauncherM" or appname == "JrdSetupWizard":
							appdir = "%s_SDD1" % appname
						else:
							appdir = appname			 
						assignDict['Description'] += "\nYou can get the apk %s from:http://10.92.32.22:8080/%s/v%s/." % (appname, appdir, version)
						assignDict['attachment'] = []
						assignDict['attachment'].append("/local/build/apkPush/%s/v%s/APK_ReleaseNote_%s_%s.xls" % (appname,version,appname,version))
						defectList = self.diffDefectAndTask(commentDefectList)						
						if len(defectList):
											
							assignDict['Description'] += "\nThe defect of %s: %s" % (project,defectList)
							if len(otherNeedAddCommentList):
								assignDict['Description'] += "\nThe defect of other project:%s" % otherNeedAddCommentList
							if item.values()[0]['apk_assignment_specail_owner']:
								assignDict['Assigned User'] = item.values()[0]['apk_assignment_specail_owner']
							else:
								assignDict['Assigned User'] = self.AlmCheckDict[appname]['apk_assignment_common_Owner']


						else:
							if len(otherNeedAddCommentList):
								assignDict['Description'] += "\nThe defect of other project:%s" % otherNeedAddCommentList
							if item.values()[0]['apk_assignment_specail_owner']:
								assignDict['Assigned User'] = item.values()[0]['apk_assignment_specail_owner']
							else:
								assignDict['Assigned User'] = self.AlmCheckDict[appname]['apk_assignment_common_Owner']
						if item.values()[0]['notification_receive_users'] == 'yes':			
							assignDict['Notification Receive Users'] = notification_user
						print "assignDict dic is "
						print assignDict
						assignIDInfo = self.createAssignment(conf, assignDict)
						assignID = assignIDInfo.id
						html_assignment += self.getAssignmentInfoForEmail(appname, assignID,project,version, codeBranch, assignDict['Assigned User'])
						self.EditCommentForDefect(conf, commentDefectList, project, assignID)

				self.moveResultFromTemp(conf,appname,version)
			
		self.mechanizeClose()				
		popdir()		
		html += html_apkpush
		if not re.search("YES", self.test):
			html += '<br><br>'
		html += html_assignment
		if not re.search("YES", self.test):
			html += '<br><br>'
		html += html_forchangeList
		html += self.getFootEMailHtml(conf)	
		self.sendMail(conf, html)

	def cleanup(self):
		conf = Config();
		if conf.getConf('cleanuptmpdir', 'Clean up the temp dir <yes|no>', 'yes') == 'yes':
			chdir('/')			
			docmd('rm -rf %s' % self.tempdir)

	def initSomeConf(self, conf):
		self.mailSubject(conf)
		pmDict = readFile('#','/local/int_jenkins/apk/conf/common.conf')
		if pmDict.keys().__contains__('fullname'):
			conf.getConf('fullname', 'full name', pmDict['fullname'])
		if pmDict.keys().__contains__('defultmail'):
			conf.getConf('defultmail', 'defult mail', pmDict['defultmail'])
		if pmDict.keys().__contains__('tell'):
			conf.getConf('tell', 'Tell', pmDict['tell'])
		if pmDict.keys().__contains__('smtpserver'):
			conf.getConf('smtpserver', 'smtp server', pmDict['smtpserver'])
			conf.getConf('tell', 'Tell', pmDict['tell'])
		if pmDict.keys().__contains__('applist'):
			conf.getConf('applist', 'applist', pmDict['applist'])
			conf.getConf('tell', 'Tell', pmDict['tell'])
		if pmDict.keys().__contains__('cclist'):
			conf.getConf('cclist', 'mail cc to list', pmDict['cclist'])
		if pmDict.keys().__contains__('tolist'):
			conf.getConf('tolist', 'tolist', pmDict['tolist'])
		if pmDict.keys().__contains__('creativelist'):
			conf.getConf('creativelist', 'creativelist', pmDict['creativelist'])
		if pmDict.keys().__contains__('productBugzillaId'):
			conf.getConf('productBugzillaId', 'productBugzillaId', pmDict['productBugzillaId'])
		if pmDict.keys().__contains__('productAlmId'):
			conf.getConf('productAlmId', 'productAlmId', pmDict['productAlmId'])

	## get Mail Subject
	def mailSubject(self, conf):
		if re.search("YES",self.test): 
			version = conf.getConf('version', 'Version number {^\w\w\w-\w$}')	
			appname = conf.getConf('appname', 'project name')
			if self.AlmCheckDict[appname]['creative_apk'].strip() != 'yes':
				mailTitle = '[Generic APK]%s APK v%s test request' %(appname,version)	
			else:
				mailTitle = '[Creative APK]SDD1 Creative %s APK %s Delivery!' %(appname,version)
		else:			
			if len(self.gitVersionForEmail.keys()) > 1:		
				mailTitle = '[Generic APK]SDD1 Generic APK Delivery!'
			else:
				version_title = self.gitVersionForEmail.values()[0][0] 
				mailTitle = '[Generic APK]SDD1 Generic %s APK %s Delivery!' % (self.gitVersionForEmail.keys()[0],version_title)		
		return conf.getConf('mailsubject', 'Mail subject', mailTitle)


	def getAlmAndBranch(self):
		gitconf = "/local/int_jenkins/apk/conf/config"
		F = open(gitconf,'r')
		for line in F:			
			m = line.strip().split("#")								
			if m[0].strip() and m[0].strip() not in self.AlmCheckDict.keys():			
					self.AlmCheckDict[m[0].strip()] = {}
					self.AlmCheckDict[m[0].strip()]['alm'] = m[1].strip()
					self.AlmCheckDict[m[0].strip()]['project'] = m[2].strip()
					if m[1] == "ALM" and len(m) == 4:
						self.AlmCheckDict[m[0].strip()]['branch'] = m[3].strip()
		return self.AlmCheckDict

	def getProjetcAndSPM(self):
		gitconf = "/local/int_jenkins/apk/conf/gitconf"
		F = open(gitconf,'r')
		for line in F:
			m = re.match('^\s*(.*)\s*\#(.*)\s*\#(.*)', line)
			if m:	
				if m.group(1) not in self.ProjetcAndSPM.keys():			
					self.ProjetcAndSPM[m.group(1)] = {}
					self.ProjetcAndSPM[m.group(1)]['project'] = m.group(2)
					if m.group(3):
						self.ProjetcAndSPM[m.group(1)]['spm'] = m.group(3)	
		return self.ProjetcAndSPM


	def getNeedAddassignmentIDToComment(self, project, appname, branch):
		self.needAddCommentDefect = []
		if appname in self.editCloneDefect.keys():
			for bugid in self.editCloneDefect[appname].keys():
				for item in self.editCloneDefect[appname][bugid]:
					if item['Product_name'] == project:
						if item['Project_BugID'] not in self.needAddCommentDefect and item['branch'] in branch:
							self.needAddCommentDefect.append(int(item['Project_BugID']))

	def GetInfoFromXlsConf(self, workbook, appname, sheetName, apkInfoDict, blackCheckList):
		mtkSheet = workbook.sheet_by_name('%s' % sheetName)
		apk_nrows = mtkSheet.nrows
		apk_ncols = mtkSheet.ncols
		apkname = ''
		for j in xrange(1, apk_nrows):
			apkraw_data = mtkSheet.row_values(j)
			if apkraw_data[0].strip() == appname:
        			apkname = mtkSheet.cell(j, 0).value.strip()
        			alm = mtkSheet.cell(j, 1).value.strip()
         			apkproject = mtkSheet.cell(j, 2).value.strip()
        			branch = mtkSheet.cell(j, 3).value.strip()
        			allproject = mtkSheet.cell(j, 4).value.strip().split(',')
				print "the all project is allproject %s" % allproject
                                if self.projectname != 'no':
                                    allproject = self.projectname.split(',')
                                    print "you chose project is %s" %allproject
        			apkDowncodeGitDir = mtkSheet.cell(j, 5).value.strip()
        			apkCodeBranch = mtkSheet.cell(j, 6).value.strip()
				test_email_list = mtkSheet.cell(j, 7).value.strip().split(',')
				apkGitWebLink = mtkSheet.cell(j, 8).value.strip()
				notification_recerive_user_list = mtkSheet.cell(j, 9).value.strip().split(',')
				apk_assignment_common_Owner = mtkSheet.cell(j, 10).value.strip()
				related_apk_name = mtkSheet.cell(j, 11).value.strip()
				creative_apk = mtkSheet.cell(j, 12).value.strip()
				break
		if not apkname:
			print "The apk info is not in generic_apk.xls, please check"
			sys.exit(1)
		sh = workbook.sheet_by_name("project_info")
		nrows = sh.nrows
		ncols = sh.ncols
		print "nrows %d, ncols %s" % (nrows, ncols)
		project = []
		wprocedures = []
		wcustores = []
		spmlist = []
		vpmlist = []
		homo = []
		notification_recerive_user_list_new = []
		if appname and appname not in apkInfoDict.keys():			
			apkInfoDict[appname] = {}
			apkInfoDict[appname]['alm'] = alm
			apkInfoDict[appname]['apkproject'] = apkproject
			if alm == "ALM":
				apkInfoDict[appname]['branch'] = branch
			apkInfoDict[appname]['apkDowncodeGitDir'] = apkDowncodeGitDir
			apkInfoDict[appname]['apkCodeBranch'] = apkCodeBranch
			apkInfoDict[appname]['apkTestEmailToList'] = test_email_list
			apkInfoDict[appname]['apkGitWebLink'] = apkGitWebLink
			apkInfoDict[appname]['related_apk_name'] = related_apk_name
			apkInfoDict[appname]['apk_assignment_common_Owner'] = apk_assignment_common_Owner
			apkInfoDict[appname]['creative_apk'] = creative_apk
			for item in notification_recerive_user_list:
				item = item.strip()
				notification_recerive_user_list_new.append(item)				
			apkInfoDict[appname]['notification_recerive_user'] = ','.join(notification_recerive_user_list_new)
			for eachproject in allproject:
				branchDict = {}
				eachproject = eachproject.strip()
				for i in xrange(1, nrows):
					raw_data = sh.row_values(i)
					if eachproject == raw_data[0].strip():
						if eachproject not in branchDict.keys():
							branchDict[eachproject] = {}
						branchDict[eachproject]['code_branch'] = raw_data[1].strip()
						branchDict[eachproject]['project'] = raw_data[2].strip()
						branchDict[eachproject]['spm'] = raw_data[5].strip()
						branchDict[eachproject]['vpm'] = raw_data[6].strip()
						branchDict[eachproject]['homo'] = raw_data[7].strip()
						#add by lyf
						apkInfoDict[appname]['is_release_mail_owner'] = raw_data[7].strip()
						#add by lyf 
						if branchDict[eachproject]['homo'] == 'yes':
							if appname not in blackCheckList.keys():
								blackCheckList[appname] = []
							if branchDict[eachproject]['project'] not in blackCheckList[appname]:
								blackCheckList[appname].append(eachproject)
						branchDict[eachproject]['almbranch'] = []
						projetc_alm_project_list = raw_data[8].strip().split(',')
						for item in projetc_alm_project_list:
							item =  item.strip()
							branchDict[eachproject]['almbranch'].append(item)				
						branchDict[eachproject]['mtkProject'] = raw_data[9].split(',')
						branchDict[eachproject]['signapkdir'] = raw_data[10].strip()
						branchDict[eachproject]['unsignapkdir'] = raw_data[11].strip()
						branchDict[eachproject]['cu_gitweb'] = raw_data[12].strip()
						branchDict[eachproject]['wp_gitweb'] = raw_data[13].strip()
						branchDict[eachproject]['plf_feldor_in_apk'] = raw_data[14].split(',')
						branchDict[eachproject]['notification_receive_users'] = raw_data[15]
						branchDict[eachproject]['apk_assignment_specail_owner'] = raw_data[16]
						branchDict[eachproject]['wprocedures'] = raw_data[3]
						branchDict[eachproject]['wcustores'] = raw_data[4]
						if 'project' not in apkInfoDict[appname].keys():
							apkInfoDict[appname]['project'] = []
						apkInfoDict[appname]['project'].append(branchDict)



	def GetEachProjectCode(self,wprocedures,wcustores, project_name, code_branch):
		wprocedurecodeDir = "/local/build/apkPush/wprocedures/"
		wcustorcodeDir = "/local/build/apkPush/custores/"
		project_name = project_name.strip()
		wprocedures = wprocedures.strip()
		wcustores = wcustores.strip()
		if not os.path.isdir(wprocedurecodeDir):
			os.system('mkdir -p %s' % wprocedurecodeDir)
		try:
			self.repo_code(wprocedurecodeDir,wprocedures,project_name, code_branch)
		except Exception, e:
			print e
			print 'WARNING: repo code of %s %s fail, please check' % (project_name, code_branch) 
		if not os.path.isdir(wcustorcodeDir):
			os.system('mkdir -p %s' % wcustorcodeDir)
		try:
			self.repo_code(wcustorcodeDir,wcustores, project_name, code_branch)
		except Exception, e:
			print e
			print 'WARNING: repo code of %s %s fail, please check' % (project_name, code_branch)
		

	def repo_code(self, CodeDir, gitClone, project_name, code_branch):
		print "Now checking the code if exist"
		EachcodeDir = CodeDir + project_name
		#if self.isgerrit == 'yes':
		        #os.system('rm -rf %s' %EachcodeDir)
		        #backup_code = CodeDir+project_name+"_bak"
			#if  os.path.isdir(backup_code):
			    #os.chdir(backup_code)
			    #os.system('git pull')
			    #print "copy"
			    #os.system('cp -r %s %s' %(backup_code,EachcodeDir))                       

		if os.path.exists(EachcodeDir + "/.git") == False:
                        print "---git clone---"
			os.chdir(CodeDir)
 			os.system('git clone git@10.92.32.10:%s -b %s %s' % (gitClone, code_branch, project_name))			
   			os.chdir(EachcodeDir)
   			os.system('git checkout %s' % code_branch)
		else:
                        print "---git pull---"
   			os.chdir(EachcodeDir)
                        if self.isgerrit == 'yes':
            		    os.system('git reset --hard HEAD^^^')
                        else:
                            os.system('git reset --hard HEAD')
            		os.system('git clean -df')
            		os.system('git pull')
					
	def copyApkToBuildServer(self, appname, curversion):
		apkDir = "/local/build/apkPush/%s/" % appname
		apkVersionDir = apkDir + "/v" + curversion
		if not os.path.isdir(apkDir):
			os.system('mkdir -p %s' % apkDir)
		else:
			os.chdir(apkDir)
			os.system("rm -rf ./*")
		docmd('scp -o StrictHostKeyChecking=no -r user@10.92.35.20:/var/www/data/genericapp/%s/v%s /local/build/apkPush/%s/' % (appname, curversion,appname))				
				
	def getAssignmentInfoForEmail(self, appname, assignmentID,project,version,branch, assign):
		html = '<br align=\'Left\'><B>%s</B> APK v%s assignment <a href=https://alm.tclcom.com:7003/im/issues?selection=%s>%s</a> for %s(branch:%s) has been created, it has been assigned to %s.' % (appname,version,assignmentID,assignmentID,project, branch, assign)
		return html
	def push_MKFile_Changed_ToCode(self, appname, version, project, branch, mtkProjectFelderList, wprocedures):
		print "Push %s %s MK file to %s wprocedures code branch %s" % (appname, version, project, branch)
		projectCodeDir = "/local/build/apkPush/wprocedures/%s/" % project
		signedApkDir, signedApkName, UnSignedApkDir,UnSignedApkName = self.getName_ApkNeedPush(appname, version)

                #begin add by shie
                os.chdir(projectCodeDir)
                os.system('git reset --hard HEAD ; git pull')
                #end

		# find old apk name in MK file and find the MK file patch,name
		for eachMtkProjectName in mtkProjectFelderList:
			eachMtkProjectName = eachMtkProjectName.strip()
			eachMtkProjectNameDir = projectCodeDir + eachMtkProjectName
			search_mkfilr_dir = eachMtkProjectNameDir + "/*"
			os.chdir(eachMtkProjectNameDir)
			MakeFile_And_OldApkName_List = self.getMKfile_and_oldApkName(search_mkfilr_dir,appname,signedApkName,UnSignedApkName)
			if MakeFile_And_OldApkName_List:
				for eachItem in MakeFile_And_OldApkName_List:	
					if len(eachItem)==1 and not eachItem[0]:
						continue
					if re.search("unsigned", eachItem[1]):
						replace_apk_result = commands.getstatusoutput("find . -name %s -print0 | xargs -0 sed -i s/%s/%s/g" % (eachItem[0], eachItem[1], UnSignedApkName))
					else:	
						replace_apk_result = commands.getstatusoutput("find . -name %s -print0 | xargs -0 sed -i s/%s/%s/g" % (eachItem[0], eachItem[1], signedApkName))
		# push apk tu server
		linkname_in_email = "wprocedures weblink"
		self.gitPushAPK_TO_Server(projectCodeDir, appname, version, project, branch,linkname_in_email,"wprocedures")
		html = self.getApkLinkOfCode(appname, version, project, branch, projectCodeDir, wprocedures, linkname_in_email)
		return html


	def pushApkToCode(self, appname, version, project, branch, mtkProjectFelderList,signedProjectDir,unsignedProjectDir, custors):
		print "Push %s APK %s to %s code branch %s" % (appname, version, project, branch)
		projectCodeDir = "/local/build/apkPush/custores/%s/" % project
		signedApkDir, signedApkName, UnSignedApkDir,UnSignedApkName = self.getName_ApkNeedPush(appname, version)
		signedApkDir = signedApkDir.replace('./', "/local/build/apkPush/%s/" % appname) 
		UnSignedApkDir = UnSignedApkDir.replace('./', "/local/build/apkPush/%s/"  % appname)
                #add by shie
                os.chdir(projectCodeDir)
		os.system('git reset --hard HEAD; git pull')
                #end

		# delete old gapk in code
		match_appname = appname.split('_')[0]
		for eachMtkProjectName in mtkProjectFelderList:
			eachMtkProjectName = eachMtkProjectName.strip()
			eachMtkProjectNameDir = projectCodeDir + eachMtkProjectName
			signedapkCodeDir = eachMtkProjectNameDir + "/" + signedProjectDir
			unsignedapkCodeDir = eachMtkProjectNameDir + "/" + unsignedProjectDir
			os.chdir(eachMtkProjectNameDir)
			delSignedApkDir = commands.getstatusoutput('find . -name "%s_*_signed*.apk"' % match_appname)
			if delSignedApkDir[1]:
				delSignedApkDirList = delSignedApkDir[1].split("\n")
				for item in delSignedApkDirList:						
					os.system("rm -rf %s" % item)

			# copy new signed apk to code
			if signedProjectDir:
				self.copyNewApk_TO_code(signedApkDir, signedapkCodeDir)					
			
			delunSignedApkDir = commands.getstatusoutput('find . -name "%s_*_unsigned*.apk"' % match_appname)
			if delunSignedApkDir[1]:
				delunSignedApkrList = delunSignedApkDir[1].split("\n")
				for item in delunSignedApkrList:			
					os.system("rm -rf %s" % item)
			# copy new unsigned apk to code
			print signedApkDir,UnSignedApkDir,"copy======"
			if unsignedProjectDir:
				self.copyNewApk_TO_code(UnSignedApkDir, unsignedapkCodeDir)

		# push apk tu server
		linkname_in_email = "custors weblink"
		self.gitPushAPK_TO_Server(projectCodeDir, appname, version, project, branch,linkname_in_email,"wcustores")
		html = self.getApkLinkOfCode(appname, version, project, branch, projectCodeDir,custors, linkname_in_email)
		return html

	def getApkLinkOfCode(self, appname, version, project, codeBranch, projectCodeDir, gitDir, linkname):
		if linkname == "plf weblink":
			comment = "push plf files for %s version %s to %s branch %s" % (appname,version,project,codeBranch)
		elif linkname == "custors weblink":
			comment = "push apk for %s version %s to %s branch %s" % (appname,version,project,codeBranch)
		elif linkname == "wprocedures weblink":
			comment = "push mk file for %s version %s apk to %s branch %s" % (appname,version,project,codeBranch)
		os.chdir(projectCodeDir)
		print "the current dir is %s " % commands.getoutput('pwd')
		print "codeBranch is %s" % codeBranch
		print "the comment is %s" % comment
		patchList = commands.getoutput('git log origin/%s --format=%s | grep "%s" | sort' % (codeBranch, "%s^^^^^^%H^^^^^^$PWD", comment)).split('\n')
		html = ''
		if len(patchList):
			for item in range(len(patchList)):
				itemInfo = patchList[item].split('^^^^^^')
				if len(itemInfo) == 0:
					continue
				if 3 != len(itemInfo):
                			print "patchList have problems. patchList = %s" % patchList
					print "The pacth has no modification"
				
				else:
					if gitDir and itemInfo[1].strip():
						gitLink = '%s%s' % (gitDir, itemInfo[1].strip())
						#html = '<br align=\'Left\'><a href=%s>%s</a>' % (gitLink,linkname)
						html = ' <a href=%s>%s</a>' % (gitLink,linkname)
		if self.isgerrit == 'yes':	
	                changeId = self.getChangeId()
	                gerrit_link="http://10.92.32.10:8081/#/c/%s/" %changeId
	                html = ' <a href=%s>%s</a>' % (gerrit_link,linkname)							
		return html
		


	def getHtml(self, project, codeBranch):
		html = '<br align=\'Left\'>%s(%s):' % (project, codeBranch)		
		return html						
	def getName_ApkNeedPush(self, appname, version):
		apkBaseDir = "/local/build/apkPush/%s" % appname
		match_appname = appname.split('_')[0]
		signedApkName = ''
		UnSignedApkName = ''
		if os.path.isdir(apkBaseDir):
			os.chdir(apkBaseDir)
			print '%s--------find . -name %s*_signed*.apk' %(apkBaseDir,match_appname)
			signedApkDir = commands.getstatusoutput('find . -name "%s*_signed*.apk"' % match_appname)
			if signedApkDir:
				signedApkDirList = os.path.split(signedApkDir[1])
				signedApkDir = signedApkDir[1]
				signedApkName = signedApkDirList[1]
			UnSignedApkDir = commands.getstatusoutput('find . -name "%s*_unsigned*.apk"' %  match_appname)
			if UnSignedApkDir:
				UnSignedApkDirList = os.path.split(UnSignedApkDir[1])
				UnSignedApkDir = UnSignedApkDir[1]
				UnSignedApkName = UnSignedApkDirList[1]
		print signedApkDir,UnSignedApkDir,'=========='
		return signedApkDir, signedApkName, UnSignedApkDir,UnSignedApkName

	def copyNewApk_TO_code(self, source, dist):
		print "source is %s" % source
		print "dist is %s" % dist
		if os.path.exists(source) and os.path.exists(dist):
			os.system('cp %s %s' % (source,dist))


	def gitPushAPK_TO_Server(self, projectCodeDir, appname, version, project, branch, linkname,windatadir=''):
		if linkname == "plf weblink":
			comment = "push plf files for %s version %s to %s branch %s" % (appname,version,project,branch)
		elif linkname == "custors weblink":
			comment = "push apk for %s version %s to %s branch %s" % (appname,version,project,branch)
		elif linkname == "wprocedures weblink":
			comment = "push mk file for %s version %s apk to %s branch %s" % (appname,version,project,branch)
		os.chdir(projectCodeDir)
		os.system('git pull; git add -A; git commit -m "%s"' % comment)
		if self.isgerrit =='no':
		    os.system('git pull; git push origin HEAD:refs/heads/%s' % branch)
		else:
		    #git push ssh://".$author_name."@10.92.32.10:29418/".$git_path_name." HEAD:refs/for/".$result_git_path_name
		    git_project = ''
		    if windatadir == 'wcustores':
		        git_project = self.wcustores_gitpath
		    else:
		        git_project = self.wprocedures_gitpath
		    if git_project == '':
		    	print "git project can't be empty!"
		    	sys.exit(1)
		    print 'git pull; git push ssh://shie.zhao@10.92.32.10:29418/%s HEAD:refs/for/%s' %(git_project,branch)
		    print "===git push gerrit==="
                    os.system('git pull')
		    os.system('git push ssh://shie.zhao@10.92.32.10:29418/%s HEAD:refs/for/%s' %(git_project,branch))
		    print "===end git push gerrit==="
                    changeid = self.getChangeId()
		    if changeid == "":
		        print "Push Gerrit Error,Please Contant to VER to fixed!"
		    	sys.exit(1)
		    print self.AlmCheckDict[appname]['apkTestEmailToList']
		    reviewer = "shie.zhao@tcl.com"
		    if len(self.AlmCheckDict[appname]['apkTestEmailToList']) == 1:
		    	reviewer = self.AlmCheckDict[appname]['apkTestEmailToList'][0].replace('<','').replace('>','')
		    else:
		        reviewer = ' -a '.join(self.AlmCheckDict[appname]['apkTestEmailToList']).replace('<','').replace('>','')
		    #print reviewer
		    reviewer_cmd = "ssh -o ConnectTimeout=8 -p 29418 shie.zhao@10.92.32.10 gerrit set-reviewers -p %s -a %s %s" %(git_project,reviewer,changeid)
		    print reviewer_cmd
		    os.system(reviewer_cmd)

	def getMKfile_and_oldApkName(self, search_mkfilr_dir,appname,signedApkName,UnSignedApkName):
		match_appname = appname.split('_')[0]
		dirs_and_files = commands.getstatusoutput('grep %s_.*.apk %s' % (match_appname, search_mkfilr_dir))
		dirs_and_files_list = dirs_and_files[1].split('\n')
		MakeFile_And_OldApkName_List_sum = []
		
		for item in dirs_and_files_list:
			item = item.replace(" ", '').replace('\t','')
			item = item.strip("\\").strip().strip("\t")
			fileList = item.split(":")
			if len(fileList) == 3:
				fileList.remove(fileList[1])
				fileList[1] = fileList[1].strip('=')
			fileList[0] = os.path.basename(fileList[0])
			MakeFile_And_OldApkName_List_sum.append(fileList)
		return MakeFile_And_OldApkName_List_sum	
		
	def copyPlfFile_From_APKCode_To_ProjectCode(self, appname,version, project, branch, wprocedures,plfFeldorUnderApkCode, mtkProjectFelderList):
		print "Push %s plf file to %s code branch %s" % (appname, project, branch)
		apkDir = "/local/build/genericapp/%s" % appname
		plfDir = "/local/build/genericapp/%s/plf" % appname
		projectCodeDir = "/local/build/apkPush/wprocedures/%s/" % project
		html = ''
		os.chdir(apkDir)
		os.system('git reset --hard HEAD; git pull')
		for item in range(len(plfFeldorUnderApkCode)):
			plfFeldorUnderApkCode[item] = plfFeldorUnderApkCode[item].strip()
			if not plfFeldorUnderApkCode[item]:
				continue
			apkPlfCodeDir = "/local/build/genericapp/%s/plf/%s" % (appname,plfFeldorUnderApkCode[item])
			BeCopiedFiles = apkPlfCodeDir + "/*"
			if os.path.exists(plfDir) and os.path.exists(apkPlfCodeDir):					
				# copy plf files from apk code to project code
				eachMtkProjectName = mtkProjectFelderList[item].strip()
				eachMtkProjectNameDir = projectCodeDir + eachMtkProjectName + "/plf"
				os.chdir(eachMtkProjectNameDir)
				docmd('cp -r %s %s' % (BeCopiedFiles,eachMtkProjectNameDir))
			# push apk tu server
		
		linkname_in_email = "plf weblink"
		self.gitPushAPK_TO_Server(projectCodeDir, appname, version, project, branch,linkname_in_email)
		html = self.getApkLinkOfCode(appname, version, project, branch, projectCodeDir, wprocedures, linkname_in_email)
		return html	

        def getChangeId(self):               
                currentCommitId = getoutput("git log -1 | head -n 1 | awk '{print $2}'")                
	        changeIdLine = getoutput("git ls-remote origin refs/changes/* | grep %s | awk '{print $2}'" %currentCommitId)
                changes=changeIdLine.split("/")
                changeId = ''
                if len(changes) > 3:
                	changeId=changes[3]
	        return changeId



