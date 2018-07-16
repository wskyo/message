#!/usr/bin/python

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
from commands import *
from time import strftime, localtime
from commands import *
import commands
from Utils import *
import time

class MailUtils:

	def createEmail(self, conf, project, version, attachDir, codeBranch,xmlExisting,updateInfor):
		toList = ['<xiaofen.zhong@tcl.com>','<shuang.zhong.hz@tcl.com>','<yunna.hua@tcl.com>','<junbo.zeng@tcl.com>','<xiaoling.luo@tcl.com>','<jinghu@tcl.com>','<yanxiang.zhang@tcl.com>']
		ccList = []
		html = ''
		variant = ''
		userLaunch = ''
		engLaunch = ''
		smtpAddrSet = set([])
		html += '<p align=\'Left\'><b>Dear perso team,</b><br/></p>'
		if not xmlExisting:
			html += '<p align=\'Left\'>Please help to build the perso of project %s <font color="#FF0000">v%s </font>,the manifest file already <font color="#FF0000">created </font>,thanks!</b><br/></p>'%(project, version)
		elif xmlExisting and updateInfor:
			html += '<p align=\'Left\'>Please help to build the perso of project %s <font color="#FF0000">v%s </font>,the manifest file already <font color="#FF0000">updated </font>,thanks!</b><br/></p>'%(project, version)

		if project == "pixi4-35_3g":
			html += '<p>V%s Manifest:<br/><a href=http://10.92.32.10/gitweb.cgi/?p=sdd1/odm_manifest.git;a=blob;f=int/%s/v%s.xml>http://10.92.32.10/gitweb.cgi/?p=sdd1/odm_manifest.git;a=blob;f=int/%s/v%s.xml</a></p>' % (version, project, version, project, version)
		elif project == "Pixi3-5_3G_RPMB":
			html += '<p>V%s Manifest:<br/><a href=http://10.92.32.10/gitweb.cgi/?p=sdd1/manifest.git;a=blob;f=int/pixi3-5_3g/v%s.xml>http://10.92.32.10/gitweb.cgi/?p=sdd1/manifest.git;a=blob;f=int/pixi3-5_3g/v%s.xml</a></p>' % (version, version, version)		
		else:
			html += '<p>V%s Manifest:<br/><a href=http://10.92.32.10/gitweb.cgi/?p=sdd1/manifest.git;a=blob;f=int/%s/v%s.xml>http://10.92.32.10/gitweb.cgi/?p=sdd1/manifest.git;a=blob;f=int/%s/v%s.xml</a></p>' % (version, project, version, project, version)
		html += '<p>v%s code branch:%s</p>' % (version, codeBranch)
		if self.lunch_value == True:
			variant = conf.getConf('Variant','To build user or eng')
			userLaunch = conf.getConf('UserLaunch','UserLaunch fron xls')
			engLaunch = conf.getConf('EngLaunch','EngLaunch fron xls')
		if userLaunch and (variant == "user"):
			html += '<p>maincode build lunch:%s</p>' % userLaunch
		elif engLaunch and (variant == 'eng'):
			html += '<p>maincode build lunch:%s</p>' % engLaunch			
	
		html += '<br>'
		html += '<p align=\'Left\'>Best Regards</b></font><br/></p>'
		html += '<p align=\'Left\'>Integration Team</b></font><br/></p>'
	
		sender = '<hudson.admin.hz@tcl.com>'
		msg = MIMEMultipart('mixed')
		msg['From'] = sender
		msg['To'] = ''
		msg['Cc'] = ''
		int_list = conf.getConf('officelist','the email address of integrator').split(',')
		spm_list = conf.getConf('Spmlist','the email address of spm').split(',')
		#perso_list = conf.getConf('perso','the email address of perso').split(',')
		#toList = toList + perso_list
		ccList = int_list + spm_list
		for to in toList:
			smtpAddrSet.add(to)
			if msg['To'] == '':
				msg['To'] = '"\'%s\'" <%s>' %(to,to)
			else:
				msg['To'] = msg['To'] + '"\'%s\'" <%s>' %(to,to)	
		for cto in ccList:
			smtpAddrSet.add(cto)
			if msg['Cc'] == '':
				msg['Cc'] = '"\'%s\'" <%s>' %(cto,cto)
			else:
				msg['Cc'] = msg['Cc'] + '"\'%s\'" <%s>' %(cto,cto)
		if not xmlExisting:
			msg['Subject'] = "[%s][v%s.xml Created] Please help to build the perso of v%s" %(project,version,version)
		elif xmlExisting and updateInfor:
			msg['Subject'] = "[%s][v%s.xml Updated] Please help to build the perso of v%s" %(project,version,version)			
		htmlPart = MIMEBase('text', 'html', charset="us-ascii")
		html = html.encode('utf-8')
		htmlPart.set_payload(html)
		encoders.encode_base64(htmlPart)
		htmlPart["Content-Disposition"] = 'filename="%s.html"' % msg['Subject'].replace(' ', '_')
		contMsg = MIMEMultipart('related')
		contMsg.attach(htmlPart)
		msg.attach(contMsg)
	
		attach = MIMEBase('application', 'octet-stream')
		fp=open(attachDir, 'rb')
		attach.set_payload(fp.read())
		fp.close()
		encoders.encode_base64(attach)
		attach["Content-Disposition"] = 'attachment; filename="%s"' % os.path.split(attachDir)[1]
		msg.attach(attach)

        	server=smtplib.SMTP()
        	server.connect('mail.tcl.com')
       		server.login('hudson.admin.hz@tcl.com','Hzsw#123')
		if smtpAddrSet != None and smtpAddrSet.__len__() == 0:
			smtpAddrSet.add('<renzhi.yang.hz@tcl.com>')
        	server.sendmail('hudson.admin.hz@tcl.com',list(smtpAddrSet),msg.as_string())
		print list(smtpAddrSet)
		print msg.as_string()
		server.quit()
		os.system('rm -rf mailtoperso.html')
