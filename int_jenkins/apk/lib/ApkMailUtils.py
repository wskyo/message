#!/usr/bin/python
#coding=utf-8

############################################################################
## MailUtils be user to create mail html and send mail to recipients.
## this class has mail head, body, foot, attach method for comment mail message.
## add by jianbo.deng for superspam create 2013-08-27
############################################################################

import sys
import os
import re
import glob

import email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.image import MIMEImage
from time import strftime, localtime
from commands import *
from Utils import *
import time
#import chardet


class ApkMailUtils:

	## mail head please didn't modified
	def getMailHeadHtml(self, conf):
		html = '<html xmlns="http://www.w3.org/1999/xhtml">'
		html += '<head>'
		html += '<meta http-equiv="Content-Type" content="text/html; charset=gb2312" />'
		html += '<style type="text/css">'
		html += 'body {font-family:arial; font-size:10pt;}'
		html += 'td {font-family:arial; font-size:10pt;}'
		html += '</style>'
		html += '<title>%s APK</title>' % conf.getConf('mailsubject', 'mail subject title')
		html += '</head>'
		return html

	def getMailBodyHtml(self, conf):
		html = ''
		html += self.getBodyHalfHtml(conf)
		return html
		

	###create 1. AP/Modem Database from 2. Images List 3. Manifest path
	def getBodyHalfHtml(self, conf):
		html = '<p>Dear all,</p>' 
		if re.search("YES",self.test):
			VersionsMail = self.gitNameVersion.copy()
			version = conf.getConf('version', 'project current version')
			projectName = conf.getConf('appname', 'Project name in check list file name')
			if projectName == "JrdMusic":
				projectName="JrdMusicKK"
			#if projectName == "JrdGallery2" or projectName == "JrdLauncherM" or projectName == "JrdSetupWizard":
				#projectName_teleweb = "%s_SDD1" %projectName
			if self.AlmCheckDict[projectName]['ischange']:
				if self.AlmCheckDict[projectName]['creative_apk'].strip() != 'yes':
		        		html += '<p align=\'Left\'>Please check %s APK(codeBranch:%s) v%s at:<a href=http://10.92.35.20/data/genericapp/%s/v%s/>http://10.92.35.20/data/genericapp/%s/v%s/</a></p>'  % (projectName, self.AlmCheckDict[projectName]['apkCodeBranch'],version,projectName,version,projectName,version)
				else:
		        		html += '<p align=\'Left\'>Please check %s APK(codeBranch:%s) v%s at:<a href=http://10.92.35.20/data/CreativeApk/%s/v%s/>http://10.92.35.20/data/CreativeApk/%s/v%s/</a></p>'  % (projectName, self.AlmCheckDict[projectName]['apkCodeBranch'],version,projectName,version,projectName,version)
		        else:
                                if conf.getConf('exitnonewchange', 'Exit if no new change from last version <yes|no>', 'yes') == 'yes':
		        	     return "!!! NO NEW CHANGE SINCE LAST VERSION !!!"
                                else:
                                     print "---!!! NO NEW CHANGE SINCE LAST VERSION !!!-----"
			for eachRelatedApk in self.AlmCheckDict[projectName]['related_apk_name'].strip().split(','):
				if not eachRelatedApk:
					continue
				versions = VersionsMail.pop(eachRelatedApk)
				version = versions[0]
				if self.AlmCheckDict[projectName]['creative_apk'].strip() != 'yes':
					html += '<p align=\'Left\'>Please check %s APK(codeBranch:%s) v%s at:<a href=http://10.92.35.20/data/genericapp/%s/v%s/>http://10.92.35.20/data/genericapp/%s/v%s/</a></p>'  % (eachRelatedApk,self.AlmCheckDict[eachRelatedApk]['apkCodeBranch'],version,eachRelatedApk,version,eachRelatedApk,version)
				else:
					html += '<p align=\'Left\'>Please check %s APK(codeBranch:%s) v%s at:<a href=http://http://10.92.35.20/data/CreativeApk/%s/v%s/>http://10.92.35.20/data/CreativeApk/%s/v%s/</a></p>'  % (eachRelatedApk,self.AlmCheckDict[eachRelatedApk]['apkCodeBranch'],version,eachRelatedApk,version,eachRelatedApk,version)
			if self.AlmCheckDict[projectName]['creative_apk'].strip() != 'yes':
				html += '<p align=\'Left\'>'+ 'Please test APK and feedback ASAP.'
				note = u"Note: 如果APK有新增SDM值，并且该SDM值需要同步编译项目主代码验证，请工程师take此apk并编译项目的black版本，以便VAL进行Qualify。请在测试结果反馈中提供该black版本的teleweb下载路径,谢谢"				 
				html += '<p align=\'Left\'><font color="#FF0000">%s</font>' % note
				if projectName in self.maincodeProjectList.keys():
					html += '<p align=\'Left\'>%s for project:%s' % (projectName, ','.join(self.maincodeProjectList[projectName]))
				for eachRelatedApk in self.AlmCheckDict[projectName]['related_apk_name'].strip().split(','):
					if not eachRelatedApk:
						continue
					if eachRelatedApk in self.maincodeProjectList.keys():
						html += '<p align=\'Left\'>%s for project:%s' % (eachRelatedApk, ','.join(self.maincodeProjectList[eachRelatedApk]))	
		else:
			if len(self.gitVersionForEmail.keys()) > 1:	 
				html += '<p align=\'Left\'>SDD1 Generic APKs have been delivered to <a href=https://teleweb-hz.tcl-ta.com/SECURITY/LIVRAISON_BF/0_Huizhou/Android_SP/genericapp/>https://teleweb-hz.tcl-ta.com/SECURITY/LIVRAISON_BF/0_Huizhou/Android_SP/genericapp/</a></p>'
			VersionsMail = self.gitNameVersion.copy()
			for name in sorted(VersionsMail.keys()):
				versions = VersionsMail.pop(name)
				print versions				
				version = versions[0]
                                if name == "JrdGallery2" or name == "JrdLauncherM" or name == "JrdSetupWizard":
                                    appname = "%s_SDD1" %name
                                else:
                                    appname = name				
				html += '<br align=\'Left\'><B>%s</B> APK %s has been delivered to:<a href=https://teleweb-hz.tcl-ta.com/SECURITY/LIVRAISON_BF/0_Huizhou/Android_SP/genericapp/%s/v%s/>https://teleweb-hz.tcl-ta.com/SECURITY/LIVRAISON_BF/0_Huizhou/Android_SP/genericapp/%s/v%s/</a>.' % (name,version,appname,version,appname,version)
				if name in self.sdmChangeInfoDict.keys() and self.sdmChangeInfoDict[name]:
					html += '<br align=\'Left\'><B><font color="#FF0000">There is SDM changed in APK %s %s.</font></B>' % (name,version)

			
		html += '<br><br>'
		return html

	### email foot 
	def getFootEMailHtml(self, conf):
		html = '<br/><img src="cid:ReleaseMailLogo.jpg">'
		html += '<p><font color="gray">'
		html += 'Best Regards,<br />'
		html += conf.getConf('fullName','send mail name, defualt is hudson.admin.hz', 'Hudson.admin.hz')+'<br />'
		html += 'TEL: '+conf.getConf('TEL', 'send email tel, defualt 0752-8228580(68580)', '0752-8228580(68580)')+'<br />'
		html += 'MAIL: '+conf.getConf('EMail','email, hudson.admin.hz@tcl.com', 'hudson.admin.hz@tcl.com')+'<br />'
		html += 'ADDR: 17 Huifeng 3rd Road, Zhongkai Hi-tech Developmen District,Huizhou,Guangdong'
		html += '</font></p>'
		html += '</body>'
		html += '</html>'
		return html

	def getMailList(self,conf):
		toList = conf.getConf('applist','if not mail list,pls input')
		return toList

	def getMailToList(self,conf):
		toList = conf.getConf('tolist','if not mail list,pls input')
		return toList

	def getMailcreativelist(self,conf):
		creativelist = conf.getConf('creativelist','if not mail list,pls input')
		return creativelist
	def getCCMailList(self,conf):
		#toList =  conf.getConf('minilist','if not mail list,pls input')
		#toList = ',%s' % conf.getConf('cclist','if not mail list,pls input')
		toList = conf.getConf('cclist','if not mail list,pls input')
		return toList

	def sendMail(self, conf, html):
		fullName = conf.getConf('fullname', 'full name')
		defultEmaill = conf.getConf('defultmail', 'Defult Email')
		officeList = None
		#miniList = None
		DailyList = None
		msg = MIMEMultipart('mixed')
		msg['Date'] = strftime("%a, %d %b %Y %T", localtime()) + ' +0800'
		msg['Subject'] = conf.getConf('mailsubject', 'Mail subject')
	
		msg['From'] = '"\'%s\'" <%s>' % (fullName, defultEmaill)
		
		smtpAddrSet = set([])
		
		## big version will send to office list
		print self.getMailList(conf)
		#msg['To'] = '"\'%s\'" <%s>' % (self.getMailList(conf),self.getMailList(conf))
		msg['To'] = ''
		msg['Cc'] = ''
		if re.search("YES",self.test):
			tmp = self.getMailList(conf).split(',')
			projectName = conf.getConf('appname', 'Project name in check list file name')	
			if projectName in self.AlmCheckDict.keys():
				if 'apkTestEmailToList' in self.AlmCheckDict[projectName].keys():
					tmp = tmp + self.AlmCheckDict[projectName]['apkTestEmailToList']				
			if self.AlmCheckDict[projectName]['creative_apk'].strip() == 'yes':
					tmp = self.AlmCheckDict[projectName]['apkTestEmailToList'] + conf.getConf('creativelist', 'creativelist list').split(',')				
			print "tmp is %s" % tmp
			for to in tmp:
				smtpAddrSet.add(to)
				if msg['To'] == '':
					msg['To'] = '"\'%s\'" <%s>' %(to,to)
				else:
					msg['To'] = msg['To'] + '"\'%s\'" <%s>' %(to,to)
			cctmp = self.getCCMailList(conf).split(',')
			for cto in cctmp:
				if self.AlmCheckDict[projectName]['creative_apk'].strip() != 'yes':
					smtpAddrSet.add(cto)
					if msg['Cc'] == '':
						msg['Cc'] = '"\'%s\'" <%s>' %(cto,cto)
					else:
						msg['Cc'] = msg['Cc'] + '"\'%s\'" <%s>' %(cto,cto)		
				
		else:
			ltmp = self.getMailToList(conf).split(',')
			for apkname in self.apkInfo.keys():
				if apkname in self.AlmCheckDict.keys():
					if self.AlmCheckDict[apkname]['is_release_mail_owner'] == "no":
						ltmp = ltmp + self.AlmCheckDict[apkname]['apkTestEmailToList']

			for tol in ltmp:
				smtpAddrSet.add(tol)
				if msg['To'] == '':
					msg['To'] = '"\'%s\'" <%s>' %(tol,tol)
				else:
					
					msg['To'] = msg['To'] + '"\'%s\'" <%s>' %(tol,tol)
		contMsg = MIMEMultipart('related')

		htmlPart = MIMEBase('text', 'html', charset="us-ascii")
		html = html.encode('utf-8')
		#print chardet.detect(html)
		htmlPart.set_payload(html)
		encoders.encode_base64(htmlPart)
		htmlPart["Content-Disposition"] = 'filename="%s.html"' % conf.getConf('mailsubject', 'Mail subject').replace(' ', '_')
		contMsg.attach(htmlPart)
	
		imageSet = set([])
	
		for imageStr in re.findall('<\s*img\s+src\s*=\s*\"?\s*cid\s*:\s*[^<>\"]+\s*\"?\s*>', html, re.M):
			match = re.search('<\s*img\s+src\s*=\s*\"?\s*cid\s*:\s*([^<>\"]+)\s*\"?\s*>', imageStr)
			if match:
				imageSet.add(match.group(1))
	
		for imageFile in list(imageSet):
			fp = open(self.tempdir+'/image/'+imageFile, 'r')
			imagePart = MIMEImage(fp.read())
			fp.close
			imagePart.add_header('Content-ID', '<%s>' % imageFile)
			imagePart["Content-Disposition"] = 'filename="%s"' % imageFile
			contMsg.attach(imagePart)
	
		msg.attach(contMsg)
	
		for attachFile in glob.glob(self.tempdir+'/attach/*'):
			attach = MIMEBase('application', 'octet-stream')
			fp=open(attachFile, 'rb')
			attach.set_payload(fp.read())
			fp.close()
			encoders.encode_base64(attach)
			attach["Content-Disposition"] = 'attachment; filename="%s"' % os.path.split(attachFile)[1]
			msg.attach(attach)
		##smtp server change here
		smtpServer = conf.getConf('smtpserver', 'Smtp server', 'mail.tcl.com')
		#smtpServer = '192.168.166.100'
		sendMailAccount = defultEmaill
                #print 'smtpServer ----- %s' % smtpServer
		if (conf.getConf('nosmtpauth', 'Do not authenticate smtp account <yes|no>', 'yes' if smtpServer == 'mail.tcl.com' else 'no') == 'no' or (sendMailAccount != 'hudson.admin.hz@tcl.com')):
			smtpPassword = conf.getConf('mailpassword', 'Passowrd for Email account <%s>' % sendMailAccount, echo=False)
                        #print "======if csz for the email password====="
		else:
			#smtpPassword = '12345678'
			smtpPassword = 'Hzsw#123'
			#print "======else csz for the email password====="
		s = smtplib.SMTP(smtpServer)
		s.set_debuglevel(int(conf.getConf('smtpdebug', 'Smtp debug level <^\d$>', '1')))

		if smtpPassword:
			#print '====the password is:%s====' %smtpPassword
			s.login(sendMailAccount[:sendMailAccount.index('@')], smtpPassword)
		if smtpAddrSet != None and smtpAddrSet.__len__() == 0:
			smtpAddrSet.add('<renzhi.yang.hz@tcl.com>')
		s.sendmail(sendMailAccount, list(smtpAddrSet), msg.as_string())
		s.quit()
		print '-------------------'
		print '--== MAIL SENT ==--'
		print '-------------------'


	def moveResultFromTemp(self, conf,appname,version):	
		curversion = 'v%s' % version 		
		print curversion
		print appname
		if appname == "JrdMusic":
			appname = "JrdMusicKK"
		if appname == "JrdGallery2" or appname == "JrdLauncherM" or appname == "JrdSetupWizard":
			appname_teleweb = "%s_SDD1" %appname
		else:
			appname_teleweb = appname				
		docmd('ssh sl_hz_hran@10.92.32.26 rm -rfv /mfs/teleweb/genericapp/%s/%s' % (appname_teleweb,curversion))			
		docmd('scp -o StrictHostKeyChecking=no -r user@10.92.35.20:/var/www/data/genericapp/%s/%s sl_hz_hran@10.92.32.26:/mfs/teleweb/genericapp/%s/' % (appname, curversion,appname_teleweb))
		#docmd('scp -o StrictHostKeyChecking=no -r user@10.92.35.20:/var/www/data/genericapp/%s/%s/APK_ReleaseNote_%s_%s.xls %s/attach/' % (appname,curversion,appname,version,self.tempdir))
