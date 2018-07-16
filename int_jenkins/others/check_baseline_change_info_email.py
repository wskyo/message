#!/usr/bin/python
############################################################################
## check whether there is new mtx file generated
## add by renzhi.yang for sortresult create 2016-04-19
###########################################################################
import os
import sys
import email
import smtplib
sys.path.append('/local/int_jenkins/lib')
import re
from commands import *
import commands
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.image import MIMEImage
	
def createEmail(project, version, baselineInfo):
	toList =['<shie.zhao@tcl.com>','<xueqin.zhang@tcl.com>','<renzhi.yang.hz@tcl.com>','<liyun.liu.hz@tcl.com>','<yan.xiong@tcl.com>','<yinfang.lai@tcl.com>','<xiaoying.huang@tcl.com>','<shuangyan.he@tcl.com>','<chunlei.hu@tcl.com>']
	#toList = ['<renzhi.yang.hz@tcl.com>']
	ccList = []
	html = ''
	smtpAddrSet = set([])
	html += '<p align=\'Left\'><b>Dear Integrator,</b><br/></p>'
	html += '<p align=\'Left\'>The project %s mtk baseline has changed. ' % project
	html += '<p align=\'Left\'>Please change the right mtk baseline info in the file under /local/int_jenkins/superspam/projects'
	html += '<p align=\'Left\'>The old mtk baseline value: <font color="#FF0000"> %s </font></b><br/></p>'%baselineInfo			
	
	html += '<br>'
	html += '<p align=\'Left\'>Best Regards</b></font><br/></p>'
	html += '<p align=\'Left\'>Integration Team</b></font><br/></p>'
	
	sender = '<hudson.admin.hz@tcl.com>'
	msg = MIMEMultipart('mixed')
	msg['From'] = sender
	msg['To'] = ''
	msg['Cc'] = ''
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

	msg['Subject'] = "[mtk baseline changed] Please change %s baseline info" %project		
	htmlPart = MIMEBase('text', 'html', charset="us-ascii")
	html = html.encode('utf-8')
	htmlPart.set_payload(html)
	encoders.encode_base64(htmlPart)
	htmlPart["Content-Disposition"] = 'filename="%s.html"' % msg['Subject'].replace(' ', '_')
	contMsg = MIMEMultipart('related')
	contMsg.attach(htmlPart)
	msg.attach(contMsg)

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




if __name__ == "__main__":
	project = sys.argv[1]
	version = sys.argv[2]
	baselineInfo = sys.argv[3]
	print sys.argv
	createEmail(project, version, baselineInfo)

