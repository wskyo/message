#!/usr/bin/python

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


class MiniMailUtils:

	## mail head please didn't modified
	def getMailHeadHtml(self, conf):
		html = '<html xmlns="http://www.w3.org/1999/xhtml">'
		html += '<head>'
		html += '<meta http-equiv="Content-Type" content="text/html; charset=gb2312" />'
		html += '<style type="text/css">'
		html += 'body {font-family:arial; font-size:10pt;}'
		html += 'td {font-family:arial; font-size:10pt;}'
		html += '</style>'
		version = conf.getConf('version', 'project current version')
		projectName = conf.getConf('project', 'Project name in check list file name')
		html += '<title>%s Mini</title>' % conf.getConf('mailsubject', 'mail subject title')
		html += '</head>'
		return html

	def getMailBodyHtml(self, conf):
		html = ''
		html += self.getBodyHalfHtml(conf)
		return html
		

	###create 1. AP/Modem Database from 2. Images List 3. Manifest path
	def getBodyHalfHtml(self, conf):
		version = conf.getConf('version', 'project current version')
		projectName = conf.getConf('project', 'Project name in check list file name')
		isMiniVersion = conf.getConf('isMiniVersion', 'is mini version or not, defualt is no', 'no')
		miniVersionBand = conf.getConf('BAND', 'mini version band defualt is EU', 'EU')

		releasenoteprojname = conf.getConf('releasenoteprojname', 'release note project name')

		html = '<p>Dear all,</p>'
                if miniVersionBand != '':
                	html += '<p align=\'Left\'>'+ 'Please check %s mini %s v%s:   %s/tmp/v%s_%s/.' %(projectName,miniVersionBand,version,projectName,version,miniVersionBand)
		else : 
                	html += '<p align=\'Left\'>'+ 'Please check %s mini %s v%s:   %s/tmp/v%s/.' %(projectName,miniVersionBand,version,projectName,version)
		html += '<p align=\'Left\'>'+ 'Makesure changes in MiniSW_ReleaseNote are related with this mini version.And please feedback ASAP.  '
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
		toList = conf.getConf('dirverlist','if not mail list,pls input')
		return toList

	def getCCMailList(self,conf):
		toList =  conf.getConf('officelist','if not mail list,pls input')
		toList += ',%s' % conf.getConf('Spmlist','if not mail list,pls input')
		return toList

	def sendMail(self, conf, html):
		fullName = conf.getConf('fullname', 'full name')
		defultEmaill = conf.getConf('defultmail', 'Defult Email')
		officeList = None
		miniList = None
		DailyList = None
		msg = MIMEMultipart('mixed')
		msg['Date'] = strftime("%a, %d %b %Y %T", localtime()) + ' +0800'
		msg['Subject'] = conf.getConf('mailsubject', 'Mail subject')
	
		msg['From'] = '"\'%s\'" <%s>' % (fullName, defultEmaill)
		
		smtpAddrSet = set([])

		version = conf.getConf('version', 'current version')
		## big version will send to office list
		print self.getMailList(conf)
		#msg['To'] = '"\'%s\'" <%s>' % (self.getMailList(conf),self.getMailList(conf))
		msg['To'] = ''
		msg['Cc'] = ''
		tmp = self.getMailList(conf).split(',')
		##smtpAddrSet = self.getMailList(conf)		
		
		for to in tmp:
			smtpAddrSet.add(to)
			if msg['To'] == '':
				msg['To'] = '"\'%s\'" <%s>' %(to,to)
			else:
				msg['To'] = msg['To'] + '"\'%s\'" <%s>' %(to,to)
		cctmp = self.getCCMailList(conf).split(',')
		for cto in cctmp:
			smtpAddrSet.add(cto)
			if msg['Cc'] == '':
				msg['Cc'] = '"\'%s\'" <%s>' %(cto,cto)
			else:
				msg['Cc'] = msg['Cc'] + '"\'%s\'" <%s>' %(cto,cto)
		
		contMsg = MIMEMultipart('related')

		htmlPart = MIMEBase('text', 'html', charset="us-ascii")
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
			smtpAddrSet.add('<swd1.hz@tcl.com>')
		s.sendmail(sendMailAccount, list(smtpAddrSet), msg.as_string())
		s.quit()
		print '-------------------'
		print '--== MAIL SENT ==--'
		print '-------------------'


