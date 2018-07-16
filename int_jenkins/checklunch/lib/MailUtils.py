#!/usr/bin/python
#coding=utf-8
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
import commands
from Utils import *
import time


class MailUtils:
	def getMailHeadHtml(self, conf):
		html = '<html xmlns="http://www.w3.org/1999/xhtml">'
		html += '<head>'
		html += '<meta http-equiv="Content-Type" content="text/html; charset=gb2312" />'
		html += '<style type="text/css">'
		html += 'body {font-family:arial; font-size:10pt;}'
		html += 'td {font-family:arial; font-size:10pt;}'
		html += '</style>'
		projectName = conf.getConf('project', 'Project name in check list file name').upper()
		mailTitle = '[LUNCH_CONFIG_CHECK][%s] remind to check lunch config value!' %projectName
		html += '<title>%s</title>' %mailTitle
		html += '</head>'
		return html

	def getMailBodyHtml(self, conf,host_result_dic,tf_result_dic):
		projectName = conf.getConf('project', 'Project name in check list file name').upper()
		html = ''
		html += '<p>Dear SPM,</p>'
                html += '<p align=\'Left\'>Please check %s lunch file value in ProjectConfig.mk and device.mk file.' %projectName
		ss = u"ProjectConfig.mk和差异记录表比较,存在如下更新："
		html += '<p><b>%s</b></p>' %ss
		html += '<table border="1" width="90%" bgcolor="#99cc66" cellpadding="2">'
		html +=  '<tr><th width="30%">ProjectConfig.mk</th><th colspan="2" width="30%">pixi4_4_host</th><th colspan="2" width="30%">pixi4_4_tf</th></tr>'
		html +=  '<tr><th width="30%">Updated</th><th width="15%">before</th><th width="15%">after</th><th width="15%">before</th><th width="15%">after</th></tr>'
		strFormat = '<tr><td align="left">%s</td><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td></tr>'
		for key in host_result_dic.keys():
			h_before = host_result_dic[key]['before']
			h_after = host_result_dic[key]['after']
			t_before = tf_result_dic[key]['before']
			t_after = tf_result_dic[key]['after']
			html += strFormat %(key,h_before,h_after,t_before,t_after)			


		html += '</table>'
		html += '<br/><br/>'
		return html

	def getFootEMailHtml(self, conf):
		html = ''
		html += 'Best Regards,<br />'
		html += conf.getConf('fullName','send mail name, defualt is hudson.admin.hz', 'Hudson.admin.hz')+'<br />'
		html += 'TEL: '+conf.getConf('TEL', 'send email tel, defualt 0752-8228580(68580)', '0752-8228580(68580)')+'<br />'
		html += 'MAIL: '+conf.getConf('EMail','email, hudson.admin.hz@tcl.com', 'hudson.admin.hz@tcl.com')+'<br />'
		html += 'ADDR: 17 Huifeng 3rd Road, Zhongkai Hi-tech Developmen District,Huizhou,Guangdong'
		html += '</font></p>'
		html += '</body>'
		html += '</html>'
		return html
		
	def sendMail(self,conf,html):
		fullName = conf.getConf('fullname', 'full name')
		defultEmaill = conf.getConf('defultmail', 'Defult Email')

		projectName = conf.getConf('project', 'Project name in check list file name').upper()
		mailTitle = '[LUNCH_CONFIG_CHECK][%s] remind to check lunch config value!' %projectName

		msg = MIMEMultipart('mixed')
		msg['Date'] = strftime("%a, %d %b %Y %T", localtime()) + ' +0800'
		msg['Subject'] = mailTitle
		msg['From'] = '"\'%s\'" <%s>' % (fullName, defultEmaill)

		smtpAddrSet = set([])
		sendTo = self.getSpmList()
		msg['To'] = ''
		msg['Cc'] = ''
		tmp = self.getMailList(conf).split(',')
		smtpAddrSet.add(sendTo)

		if msg['To'] == '':
			msg['To'] = '"\'%s\'" <%s>' %(sendTo,sendTo)
		else:
			msg['To'] = msg['To'] + '"\'%s\'" <%s>' %(sendTo,sendTo)

		for cto in tmp:
			smtpAddrSet.add(cto)
			if msg['Cc'] == '':
				msg['Cc'] = '"\'%s\'" <%s>' %(cto,cto)
			else:
				msg['Cc'] = msg['Cc'] + '"\'%s\'" <%s>' %(cto,cto)


		contMsg = MIMEMultipart('related')
		htmlPart = MIMEBase('text', 'html', charset="us-ascii")
		html = html.decode('utf-8')
		html = html.encode('utf-8')
		htmlPart.set_payload(html)
		encoders.encode_base64(htmlPart)
		#htmlPart["Content-Disposition"] = 'filename="%s.html"' % conf.getConf('mailsubject', 'Mail subject').replace(' ', '_')
		htmlPart["Content-Disposition"] = 'filename="%s.html"' % mailTitle
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
			smtpAddrSet.add('<xueqin.zhang@tcl.com>')			                   
		s.sendmail(sendMailAccount, list(smtpAddrSet), msg.as_string())
		s.quit()
		print '-------------------'
		print '--== MAIL SENT ==--'
		print '-------------------'



				

