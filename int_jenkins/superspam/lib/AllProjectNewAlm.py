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
from MailUtils import *
from InterfaceUtils import *
from SheetUtilsAlm import *
from CheckUtils import *
from DBUtilsAlm import *
from ReleaseStyle import *
from CheckWifi import *
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
class AllProjectNewAlm(ChangeUtils, MailUtils, InterfaceUtils, SheetUtilsAlm, CheckUtils, DBUtilsAlm, ReleaseStyle, CheckWifi):

	## superspam start from this
	def run(self):
		self.lineNum = 0
		## flow dict is for create sheet
		self.prFromCodeDict = {}
		self.patchWithoutPRList = []
		self.apkChangeInfoDict = {}
		self.sdmChangeInfoDict = {}
		self.updatesdmChangeInfoDict = {}
		self.sdmauthor = {}
		self.sdmChangeToPRDict = {}
		self.sdmChangeToURLDict = {}
        	self.plfChangeInfoDict = {}
		self.wifiRelatedDict = {}
		self.allNeedCheckFileInfoAboutWifi = {}
		self.wifiBugsDict = {}
		self.googleSecuPatchLevel = ''
		self.curCodeSecuPatchLevel = ''
		self.GMSVersionReleased = ''
		self.GMSDeadline = ''
		self.GMSVersionFromCode = ''
		self.GoogleCTSVersion = ''
		self.GoogleCTSNewVersionDeadline = ''
		self.GoogleGTSVersion = ''
		self.GoogleGTSNewVersionDeadline = ''
		self.GoogleGmsLastVertion = ''
		self.GoogleCTSLastVertion = ''
		self.GoogleGTSLastVertion = ''
		self.googlechecklist = []
		self.maxColumn = 13
		self.curRow = 4
		self.curRow2 = 0
		self.needDeliverPR = False
        	self.bugzillaUrlBase = 'https://alm.tclcom.com:7003/im/issues?selection=%s'
        	self.username="user"
        	self.password="zxq_123"
        	self.ip='10.92.35.20'
		self.errorInfo = ''
		##get all config from here 
		conf = Config();
		## get all args from commands
		conf.addFromArg(sys.argv[1:])
		## init conf from xls table and check some message
		self.initConfFromXls(conf)
		## init other message
		self.initSomeConf(conf)
		self.allNeedCheckFileInfoAboutWifi = self.getAffectFileDict()
		self.tempdir = tempfile.mkdtemp('SuperSpam', 'temp', '/tmp')
		docmd('mkdir %s/image' % self.tempdir)
		docmd('mkdir %s/attach' % self.tempdir)
		conf.getConf('tempdir', 'temp dir', self.tempdir)
		

		sendTo = conf.getConf('sendto', 'Send mail to <self|all>')

		projBuildRoot = conf.getConf('projbuildroot', 'Project build root')
		version = conf.getConf('version', 'current version')
		project = conf.getConf('project', 'current project')
		if project == 'pixi3-45':
			buildDir = "/local/build/pixi3-45-release"
			self.checkCode(buildDir,version)
			self.getImgeFromOtherServer(version)
		else:
			buildDir = conf.getConf('builddir', 'Build directory', projBuildRoot+'v'+version)
		buildok = conf.getConf('buildok', 'build ok or nok<yes|no>','yes' )
		print "build dir %s" %buildDir
		self.buildDir = buildDir
	
		pushdir(buildDir)

		extAttachFileStr = conf.getConf('extattach', 'External attach files', 'none')
		if  extAttachFileStr != 'none':
			for fileName in extAttachFileStr.split(','):
				docmd('cp %s %s/attach' % (projBuildRoot + 'v' + version + '/' + fileName.strip(), self.tempdir))
		docmd('cp %smisc/SuperSpamReleaseMailFootLogoOneTouch.jpg %s/image/ReleaseMailLogo.jpg' % (getToolPath(), self.tempdir))
		if buildok == 'yes':
			## superspam preload
			self.preLoad(conf)
		##get android security patch level,gsm,cts,gts info
		self.googlechecklist=self.getItemInfo(project)
		self.googleSecuPatchLevel = self.googlechecklist[0]
		self.GMSVersionReleased = self.googlechecklist[1]
		self.GMSDeadline = self.googlechecklist[2]
		self.GoogleCTSVersion = self.googlechecklist[3]
		self.GoogleCTSNewVersionDeadline = self.googlechecklist[4]
		self.GoogleGTSVersion = self.googlechecklist[5]
		self.GoogleGTSNewVersionDeadline = self.googlechecklist[6]
		self.GoogleGmsLastVertion = self.googlechecklist[7]
		self.GoogleCTSLastVertion = self.googlechecklist[8]
		self.GoogleGTSLastVertion = self.googlechecklist[9]
		self.curCodeSecuPatchLevel = self.getPlatformSecurityPathchValue(buildDir)
		self.GMSVersionFromCode  = self.getGmsValue(buildDir)
		print "self.curCodeSecuPatchLevel",self.curCodeSecuPatchLevel
		print "self.GMSVersionFromCode",self.GMSVersionFromCode
		print "self.GoogleCTSLastVertion",self.GoogleCTSLastVertion
		print "self.GoogleGTSLastVertion",self.GoogleGTSLastVertion
		print "self.GoogleGmsLastVertion",self.GoogleGmsLastVertion
		pushdir(buildDir)	

		## create mail html
		html = '' 
		html += self.getMailHeadHtml(conf)
		html += self.getMailBodyHtml(conf)
		html += self.getChangeList(conf)
		html += self.getFootEMailHtml(conf)
		#print '------------------------------html start----------------------------------'
		#print html
		#print '-------------------------------html end ----------------------------------'
		pushdir(buildDir)
		version = conf.getConf('version', 'current version')
		if conf.getConf('genchecklist', 'Generate mini test check list <yes|no>', self.isBigVersion(version)) == 'yes' and buildok == 'yes':
			self.mkMiniTestCheckList(conf)
                #/zhaoshie 20141120 close for hz-sdd1 mini version
		#if conf.getConf('genminichecklist', 'Generate mini test check list <yes|no>', self.isMiniVersion(version)) == 'yes':
		#	self.mkMiniSWCheckList(conf)
		if conf.getConf('curchecklist', 'Generate cursor based mini test check list <yes|no>', 'no') == 'yes':
			self.mkCursorMiniTestCheckList(conf)

		if buildok == 'yes':
			if conf.getConf('genreleasenote', 'Generate release note <yes|no>', 'yes') == 'yes':
                                if self.isMiniVersion(version) == 'yes':
                                	os.system('/local/int_jenkins/sortresult/projects/ssh.sh %s %s %s %s'%(self.username,self.ip,self.password,conf.getConf('prlistprojname', 'Project name in PR List file name')))
                                	if project == 'pixi3-45':
                                		try:
                                			docmd('rsync -rl zhaoshie@10.92.35.31:/tmp/MiniSW_ReleaseNote_%s_%s.xls /tmp' %(conf.getConf('prlistprojname', 'Project name in PR List file name'), conf.getConf('version','current version')))
                                		except:
                                			docmd('rsync -rl zhaoshie@10.92.35.26:/tmp/MiniSW_ReleaseNote_%s_%s.xls /tmp' %(conf.getConf('prlistprojname', 'Project name in PR List file name'), conf.getConf('version','current version')))
                                	docmd('scp /tmp/MiniSW_ReleaseNote_%s_%s.xls user@10.92.35.20:/var/www/data/Release_Note/%s' % ( conf.getConf('prlistprojname', 'Project name in PR List file name'), conf.getConf('version','current version'),conf.getConf('prlistprojname', 'Project name in PR List file name')))
                                	docmd('mv /tmp/MiniSW_ReleaseNote_%s_%s.xls %s/attach/' % ( conf.getConf('prlistprojname', 'Project name in PR List file name'), conf.getConf('version','current version'),self.tempdir))
				else:
                                	self.createReleaseNote(conf)
		else:
			## load compiling log
			self.loadcompilelog(conf)
			
		popdir()
		if buildok == 'yes':
			## move result from temp to appli or Dialy
			self.moveResultFromTemp(conf)
                        #self.unlock_zz(conf)  #2017-5-23 for zz perso auto unlock
		## send mail

		##closed by renzhiyang
		#f = open ('%s/ChangeList.html'%self.tempdir,'w')		
		#html = html
		#f.write(html)
                #f.close()
		##end 2016-7-7

		self.sendMail(conf, html)
		docmd('rm -rf %s' % self.tempdir+'/attach/*')
		if buildok == 'yes' and (conf.getConf('isBigVersion', 'version is big version') == 'yes' or conf.getConf('isDailyVersion', 'version is Daily version') == 'yes'):
                    os.system('/local/int_jenkins/sortresult/projects/ssh.sh %s %s %s %s'%(self.username,self.ip,self.password,conf.getConf('prlistprojname', 'Project name in PR List file name')))
                    version =  conf.getConf('version', 'current version')
		    if "pixi3-5_3g" == conf.getConf('releasenoteprojname', 'project name '):
			if version[2] == '6' or version[2] == 'T':
                            projectname = "Pixi3-5_3G_RPMB"
                        else:
                            projectname = conf.getConf('prlistprojname', 'Project name in PR List file name')	
		    else:   
			projectname = conf.getConf('prlistprojname', 'Project name in PR List file name')		 
                    docmd('scp /tmp/ReleaseNote_%s_SW%s.xls user@10.92.35.20:/var/www/data/Release_Note/%s' % (conf.getConf('prlistprojname', 'Project name in PR List file name'), 
conf.getConf('version','current version'),projectname))


		if buildok == 'yes' and conf.getConf('isBigVersion', 'version is big version') == 'yes':
			comparetimeResult = self.compare_time_for_email(self.googleSecuPatchLevel,self.curCodeSecuPatchLevel)
			if not comparetimeResult:
				self.sendMailForRemindPlatformSesurityPatch(conf)


		#insert buildinfo
		if buildok == 'yes':
			self.InsertBuildInfo(conf)

		#copy CopySymbols
		pushdir(buildDir)
		if conf.getConf('isBigVersion', 'version is big version') == 'yes':
			self.CopySymbols(conf)

		#create releasenote
		if conf.getConf('isBigVersion', 'version is big version') == 'yes':#  or self.isMiniVersion(version) == 'yes'
			if buildok == 'yes':
				self.create_releasenote(conf)


		#insert release info for weekly report
 		codebranch = conf.getConf('codebranch', 'The development branch of ')
		if buildok == 'yes' and (conf.getConf('isBigVersion', 'version is big version') == 'yes' or self.isMiniVersion(version) == 'yes'):
			comment = conf.getConf('version_use','The use of current version offered by spm')
			self.InsertWeeklyReport(conf,self.almlogname,comment)
			release_type = 'release'	
			os.system('python /local/int_jenkins/misc/CreateTaskForRealeaseVersionInPRSM.py "%s" "%s" "%s" "%s" "%s"' % (codebranch,version,release_type,comment,self.almlogname))

		if buildok == 'yes' and conf.getConf('isBigVersion', 'version is big version') == 'yes':
			self.updatesdmChangeInfoDict = str(self.updatesdmChangeInfoDict)
			self.updatesdmChangeInfoDict = self.updatesdmChangeInfoDict.replace('\"','')
			os.system('python /local/int_jenkins/misc/CreateTaskForSdmChangeInPRSM.py "%s" "%s" "%s"' % (self.updatesdmChangeInfoDict,codebranch,version))
		#upload img to weitai FTP only pixi4-5	close by renzhi.yang 2016-7-26
		#if self.isMiniVersion(version) == 'yes':
			#self.uploadImgFTP(conf)
		if buildok == 'no':
			os.system('python /local/int_jenkins/misc/CreateTaskForBuildErrorInPRSM.py "%s" "%s" "%s"' % (codebranch,version,self.errorInfo))
			 

	def cleanup(self):
		conf = Config();
		if conf.getConf('cleanuptmpdir', 'Clean up the temp dir <yes|no>', 'yes') == 'yes':
			chdir('/')
			docmd('rm -rf %s' % conf.getConf('tempdir','temp dir'))
		


		


