#!/usr/bin/python

import os
import sys
import re
import glob
import commands
import datetime
import tempfile
import time
import codecs
import xml.dom.minidom
from Utils import *
from Config import *
from UserInfo import *
from PersoCompatibleCheck import *
import mailUtils
####################################
# version tool allproject 
# this python will create version and manifest if you chose add version adn manifest
####################################

class AllProject:
	def __init__(self):
		self.conf = Config()
		self.userInfo = UserInfo()
		self.jobname = ''
		self.buildurl = ''
		self.buildnumber = ''
		self.buildstate = ''
		self.buildlog = ''
		self.address = ''
		self.project = ''

	
	def getResult(self,jobname,buildno,row):
		cmd ='ssh user@10.92.35.20 "tail -20 /usr/tomcat/apache-tomcat-6.0.28/webapps/jenkins/jobs/%s/builds/%s/log"' %(jobname,buildno) 
		print cmd
		#cmd =' ssh user@10.92.35.20 "tail -20 /usr/tomcat/apache-tomcat-6.0.28/webapps/jenkins/jobs/pixi3-55_3g-release/builds/264/log"'
		LogList = commands.getstatusoutput(cmd)
		#print LogList
		if LogList[0] >> 8 != 0:
			print "get build log error" 
		#print LogList[1]
		self.buildlog = LogList[1]
		#print self.buildlog



	def mail_mail_content(self):
		html = '''<html xmlns="http://www.w3.org/1999/xhtml">
		    <head>
		    <meta http-equiv="Content-Type" content="text/html;charset=gb2312"/>
		    <style type="text/css">
		    body {font-family:arial; font-size:10pt;}
		    td {font-family:arial; font-size:10pt;}
		    </style>
		    <title>Patch Review List</title>
		    </head>
		    <body>
		    <p>Dear Sir/Miss,</p> 
		    '''
 		html +="You project has finished.<br>"
 		html +="You can get building's results on Jenkins Server:<b>%s</b>.<br>"%self.buildurl
 		html +="If success,you can find it at telweb:<font color='red'><b>%s/black/v%s-black-%s</b></font><br>"%(self.project,self.basever,self.blacksuffix)	
		return html

	def mail_bottom_content(self):
	    html = '<br /> '
	    html += '<p><font color="gray">'
	    html += 'Best Regards,<br />'
	    html += 'hudson.admin.hz' + '<br />'
	    html += 'TEL: 0752-2639 227 <br />'
	    html += 'MAIL: ' + 'hudson.admin.hz@tcl.com' + '<br />'
	    html += 'ADDR: HZ Product Innovation Center SWD1 TCL COMMUNICATION TECHNOLOGY HOLDINGS LIMITED'+ \
		    '70 Huifeng 4th,ZhongKai Hi-tech Development District,Huizhou,Guangdong 516006 P.R.China'
	    html += '</font></p>'
	    html += '</body>'
	    html += '</html>'
	    return html


	def set_mail_info(self,address,buildstate,jobname,buildurl,buildlog,basever,blacksuffix):
	    to_list = []
	    cc_list = [] 
	    to_list_str = address 
	    cc_list_str = ''
	    domain = 'hudson.admin.hz'
	    domain_passwd = 'Hzsw#123'
	    name='hudson.admin.hz'
	    mail='hudson.admin.hz@tcl.com'

	    if to_list_str.strip():
		to_list = to_list_str.split(',')
	    if cc_list_str.strip():
		cc_list = cc_list_str.split(',')
	    subject = '[HZ SWD1 BLACKBUILD] %s %s-black-%s build'%(jobname,basever,blacksuffix)
	    mail_content = self.mail_mail_content()
	    mail_content += self.mail_bottom_content()
	    mailUtils.mailUtils(domain,mail, subject, mail_content, to_list,name,domain_passwd,cc_list,None,None)
		
	
	###version run from here 
	def run(self):
		conf = Config();
		## get all args from commands
		conf.addFromArg(sys.argv[1:])
		self.jobname = conf.getConf('jobname', 'Build Job Name')
		self.buildurl = conf.getConf('buildurl', 'Build Job URL')
		self.buildnumber = conf.getConf('buildnumber', 'Build Job Number')
		#self.buildstate = conf.getConf('buildstate', 'Build Result')
		self.address = conf.getConf('addr', 'email')
		self.basever = conf.getConf('baseversion', 'baseversion version')
		self.blacksuffix = conf.getConf('blacksuffix', 'blacksuffix')
		self.project = conf.getConf('project', 'tewebproject')
		#self.getResult(self.jobname,self.buildnumber,20)

 		self.set_mail_info(self.address,self.buildstate,self.jobname,self.buildurl,self.buildlog,self.basever,self.blacksuffix)
		




        def cleanup(self):
		if self.conf.getConf('cleanuptmpdir', 'Clean up the temp dir <yes|no>', 'no') == 'yes':
			chdir('/')
			docmd('rm -rf %s' % self.workDir)

