#!/usr/bin/python
#coding=utf-8

import os
import sys
import re
from commands import *
import time
import datetime
import MySQLdb
import glob
sys.path.append('/local/int_jenkins/lib')
from Utils import *
from Config import *
import common
import send_mail
from time import strftime, localtime
import commands
import tempfile	
reload(sys)
sys.setdefaultencoding("utf-8")

class Email:
	def mail_head_content(self, importbranch,link, patchnum,patchdir):
		html = '''<html xmlns="http://www.w3.org/1999/xhtml">
		<head>
		<meta http-equiv="Content-Type" content="text/html;charset=gb2312"/>
		<style type="text/css">
		body {font-family:arial; font-size:10pt;}
		td {font-family:arial; font-size:10pt;}
		</style>
		<title>libnvram.so changed</title>
		</head>
		<body>
		<p>Dear fanyan,</p>
		<p> </p>
		'''
		html += '<p align=\'Left\'>The file libnvram.so has been chaned in mtk patch P%s in %s ,Please check,thanks!</b><br/></p>'%(patchnum, importbranch)
		html += '<p align=\'Left\'><b>You can find mtk patch (P%s) in:<font color="#FF0000">%s</font></b></p>' % (patchnum, patchdir)
		html += '<p align=\'Left\'><b>Change Info on gitweb:</b><br/></p>'
		html += '<p align=\'Left\'><a href=%s>%s</a></b><br/></p>'  %(link,link)
		html = html.encode('utf-8')
		return html

	def mail_bottom_content(self):
		html = '<br/><img src="cid:ReleaseMailLogo.jpg">'
		html += '<p><font color="gray">'
		html += 'Best Regards,<br />'
		html += 'hudson.admin.hz<br />'
		html += 'TEL:  0752-8228580 <br />'
		html += 'MAIL: hudson.admin.hz@tcl.com<br />'
		html += 'ADDR: HZ Product Innovation Center SWD1 TCL COMMUNICATION TECHNOLOGY HOLDINGS LIMITED'+ \
            '17 Huifeng 4th,ZhongKai Hi-tech Development District,Huizhou,Guangdong 516006 P.R.China'
		html += '</font></p>'
		html += '</body>'
		html += '</html>'
		html = html.encode('utf-8')
		return html

	def createEmail(self, spmlist, emailToList,importbranch, link,patchnum,patchdir):
		#to_list = ['yan.fang@tcl.com']
		#cc_list_confirm = ['shie.zhao@tcl.com','jinguo.zheng@tcl.com','jie.fang@tcl.com','renzhi.yang.hz@tcl.com']
		to_list = ['renzhi.yang.hz@tcl.com']
		cc_list_confirm = ['renzhi.yang.hz@tcl.com']
		cc_list = spmlist + cc_list_confirm + emailToList	
		print "to_list",to_list
		print "cc_list",cc_list
		subject = "[libnvram.so warning][%s]Vendor libnvram.so file has changed in import branch" % importbranch	
		mail_content = self.mail_head_content(importbranch,link, patchnum,patchdir)
		mail_content += self.mail_bottom_content()
		common.show("Send mail")
		tmp_dir = tempfile.mktemp('mail', 'tmp')
		os.makedirs(tmp_dir)
		(img_dir, attach_dir) = self.prepare_attach(tmp_dir)
		send_mail.send_mail('hudson.admin.hz', 'hudson.admin.hz@tcl.com', subject, mail_content, to_list,'hudson.admin.hz','Hzsw#123',cc_list, img_dir, attach_dir)

	def prepare_attach(self,tmp_dir):
		img_dir = '%s/image' % tmp_dir
		attach_dir = '%s/attach' % tmp_dir
		common.docmd('mkdir %s' % img_dir)
		common.docmd('mkdir %s' % attach_dir)
		tools_int_dir =  '/local/int_jenkins/misc'
		common.docmd('cp %s/SuperSpamReleaseMailFootLogoOneTouch.jpg %s/ReleaseMailLogo.jpg' % (tools_int_dir, img_dir))
		return (img_dir, attach_dir)


def main():
	email = Email()
	print sys.argv
	spmlist = []
	emailToList = []
	spmlist.append(sys.argv[1])
	emailToList.append(sys.argv[2])
	importbranch = sys.argv[3]
	link = sys.argv[4]
	patchnum = sys.argv[5]	
	patchdir = sys.argv[6]
	email.createEmail(spmlist, emailToList,importbranch, link,patchnum,patchdir)



if __name__ == '__main__':  
    main()
