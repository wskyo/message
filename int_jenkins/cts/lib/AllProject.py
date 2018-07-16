#!/usr/bin/python

import os
import sys
import re
import datetime
import tempfile
from Utils import *
from Config import *
from UserInfo import *
from CtsMailUtils import *
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
#from pyExcelerator import *
#import MySQLdb
import xml.dom.minidom
from time import strftime, localtime
import time
import curses


class AllProject(CtsMailUtils):

	## superspam start from this
	def run(self):
		
		conf = Config();

		## get all args from commands
		conf.addFromArg(sys.argv[1:])
		pmDict = readFile('#','/local/int_jenkins/cts/conf/common.conf')
		##info = UserInfo()
		if pmDict.keys().__contains__('fullname'):
			conf.getConf('fullname', 'full name', pmDict['fullname'])
		if pmDict.keys().__contains__('defultmail'):
			conf.getConf('defultmail', 'defult mail', pmDict['defultmail'])
		if pmDict.keys().__contains__('tell'):
			conf.getConf('tell', 'Tell', pmDict['tell'])
		if pmDict.keys().__contains__('smtpserver'):
			conf.getConf('smtpserver', 'smtp server', pmDict['smtpserver'])
			conf.getConf('tell', 'Tell', pmDict['tell'])
		if pmDict.keys().__contains__('dirverlist'):
			conf.getConf('intlist', 'dirverlist', pmDict['dirverlist'])

		print pmDict
		

		#sendTo = conf.getConf('sendto', 'Send mail to <self|all>')

		projBuildRoot = conf.getConf('project', 'Project')
		version = conf.getConf('version', 'current version')
                self.tempdir = conf.getConf('tempdir','tmp path','/tmp/%s-00' %version)
		if not (os.path.exists(self.tempdir)):
			docmd('mkdir %s' % self.tempdir)
		#docmd('mkdir %s/image' % self.tempdir)
		#docmd('mkdir %s/attach' % self.tempdir)
	
		#pushdir(buildDir)
		#docmd('cp %smisc/SuperSpamReleaseMailFootLogoOneTouch.jpg %s/image/ReleaseMailLogo.jpg' % (getToolPath(), self.tempdir))


		## create mail html
		html = '' 
		html += self.getMailHeadHtml(conf)
		html += self.getMailBodyHtml(conf)	
		html += self.getFootEMailHtml(conf)
		#print '------------------------------html start----------------------------------'
		print html
		#print '-------------------------------html end ----------------------------------'
		print 'sendMail'
		self.sendMail(conf, html)

	def cleanup(self):
		conf = Config();
		if conf.getConf('cleanuptmpdir', 'Clean up the temp dir <yes|no>', 'yes') == 'yes':
			chdir('/')
			docmd('rm -rf %s' % conf.getConf('tempdir','temp dir'))
		print ''

	def initSomeConf(self, conf):
		##print 'interface utils init some conf'
		self.mailSubject(conf)
		pmDict = readFile('#','/local/int_jenkins/mini/conf/common.conf')
		##info = UserInfo()
		if pmDict.keys().__contains__('fullname'):
			conf.getConf('fullname', 'full name', pmDict['fullname'])
		if pmDict.keys().__contains__('defultmail'):
			conf.getConf('defultmail', 'defult mail', pmDict['defultmail'])
		if pmDict.keys().__contains__('tell'):
			conf.getConf('tell', 'Tell', pmDict['tell'])
		if pmDict.keys().__contains__('smtpserver'):
			conf.getConf('smtpserver', 'smtp server', pmDict['smtpserver'])
			conf.getConf('tell', 'Tell', pmDict['tell'])
		if pmDict.keys().__contains__('dirverlist'):
			conf.getConf('dirverlist', 'dirverlist', pmDict['dirverlist'])

		print pmDict


	## get Mail Subject
	def mailSubject(self, conf):
		version = conf.getConf('version', 'Version number {^\w\w\w-\w$}')
		BAND = conf.getConf('BAND', 'which BAND version to deliver? <CN|EU|EU1|US0|US1|US2|US3|US|2G|LATAM3G|LATAM2G>')
		project = conf.getConf('project', 'project name')
		mailTitle = '%s MINISW %s v%s test request' %(project,BAND,version)
		##print "mail subject mailTitle %s" %mailTitle test request
		return conf.getConf('mailsubject', 'Mail subject', mailTitle)

	def isMiniVersion(self, version):
		if version[2] >= 'U' :  #and version.__contains__('_')
			return 'yes'
		#else:
		#	return 'no'




