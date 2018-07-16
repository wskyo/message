#!/usr/bin/python

############################################################################
## MailUtils be user to create mail html and send mail to recipients.
## this class has mail head body mail message.
## add by xueqin.zhang for auto cts/gts mail create 2016-03-28
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
		html += '<title>%s Delivery</title>' % conf.getConf('mailsubject', 'mail subject title')
		html += '</head>'
		return html

	def getMailBodyHtml(self, conf,summary_dic,testpackage_result_dic):
		version = conf.getConf('version', 'project current version')
		projectName = conf.getConf('project', 'Project name in check list file name')
                testtype = conf.getConf('testtype', 'Test Type').upper()
                googleversion = conf.getConf('googleversion', 'Test Type').upper()
                persoversion = conf.getConf('persoversion', 'Test Type').upper()
                projectupper = conf.getConf('projectupper', 'Project uppername')
		passnum = summary_dic['pass']
		failnum = summary_dic['failed']
		timeoutnum = summary_dic['timeout']
		notexcutednum = summary_dic['notExecuted']

		html = ''
		html += '<p>Dear all,</p>'
                html += '<p align=\'Left\'>'+ '%s v%s+%s %s test finished.<br/></p>' % (projectupper, version, persoversion, testtype)
                html += '<p align=\'Left\'>You can find results and logs at:<a href=http://10.92.35.20/data/google_CTS_results/%s/%s/v%s+%s/>http://10.92.35.20/data/google_CTS_results/%s/%s/v%s+%s/</a></p>'  % (projectName,testtype,version,persoversion,projectName,testtype,version,persoversion)
                html += '<p align=\'Left\'>'+ 'Note: This version use %s %s to test.<br/></p>' % (testtype, googleversion)
		html += '<p><br/><b>Summary:</b><br/></p>'
		html += '<table border="1" width="60%" bgcolor="#99cc66" cellpadding="2">'
		html +=  '<tr><th width="25%">Tests Passed</th><th width="25%">Tests Failed</th><th width="25%">Tests Timed out</th><th width="25%">Tests Not Executed</th></tr>'
		strFormat =  '<tr><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td><td align="center">%s</td></tr>'
		html += strFormat %(passnum,failnum,timeoutnum,notexcutednum)
		html += '</table>'
		html += '<p><br/><b>Case fail below need to check:</b><br/></p>'
		html += '<table border="1" width="90%" bgcolor="#99cc66" cellpadding="2">'
		html +=  '<tr><th width="20%">Test</th><th width="10%">Result</th><th width="50%">Detail</th><th width="10%">Comment</th></tr>'
		strFormat1 =  '<tr><td align="left" colspan="4">Test Package: %s</td></tr>'
		strFormat2 =  '<tr><td align="left">%s</td><td align="center" bgcolor="red">fail</td><td align="left">%s</td><td align="left"></td></tr>'
        	for key, value in testpackage_result_dic.items():
            		if value.__len__() != 0:
				html += strFormat1 %key
				for key1,value1 in value.items():
					html += strFormat2 %(key1,value1)
		html += '</table>'
		return html

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

	def sendMail(self, conf, html):
		fullName = conf.getConf('fullname', 'full name')
		defultEmaill = conf.getConf('defultmail', 'Defult Email')
		buildok = conf.getConf('buildok', 'build ok or no <yes|no>','yes')
		officeList = None
		miniList = None
		DailyList = None
		msg = MIMEMultipart('mixed')
		msg['Date'] = strftime("%a, %d %b %Y %T", localtime()) + ' +0800'
		msg['Subject'] = conf.getConf('mailsubject', 'Mail subject')
		msg['From'] = '"\'%s\'" <%s>' % (fullName, defultEmaill)
		
		smtpAddrSet = set([])
		sendTo = conf.getConf('sendto', 'email send to list<self|all>', )
		version = self.getVersion(conf)

		print self.getMailList(conf)
		msg['To'] = ''
		tmp = self.getMailList(conf).split(',')
		smtpAddrSet = self.getMailList(conf).split(',')		
		
		for to in tmp:
			if msg['To'] == '':
				msg['To'] = '"\'%s\'" <%s>' %(to,to)
			else:
				msg['To'] = msg['To'] + '"\'%s\'" <%s>' %(to,to)
		
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
			smtpAddrSet.add('<shie.zhao@tcl.com>')			                   
		s.sendmail(sendMailAccount, list(smtpAddrSet), msg.as_string())
		s.quit()
		print '-------------------'
		print '--== MAIL SENT ==--'
		print '-------------------'



				

