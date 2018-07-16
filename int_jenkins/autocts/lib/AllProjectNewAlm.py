#!/usr/bin/python

import os
import sys
import re
import datetime
import tempfile
from Utils import *
from Config import *
from UserInfo import *
from MailUtils import *
from XmlParser import *
from InterfaceUtils import *
from ReleaseStyle import *
from TestCaseReport import *
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

'''
 autocts mail tool allproject 
 this python will auto upload cts/gts test result and sendmail 
 create by xueqin.zhang 2016-03-24
'''

class AllProjectNewAlm(MailUtils, InterfaceUtils):

	def run(self):
		conf = Config();
		conf.addFromArg(sys.argv[1:])
		self.initConfFromXls(conf)
		self.initSomeConf(conf)

		self.tempdir = tempfile.mkdtemp('GoogleTest', 'temp', '/tmp')
		docmd('mkdir %s/image' % self.tempdir)
		docmd('mkdir %s/attach' % self.tempdir)
		docmd('mkdir %s/result' % self.tempdir)
		conf.getConf('tempdir', 'temp dir', self.tempdir)		

		sendTo = conf.getConf('sendto', 'Send mail to <self|all>')

		version = conf.getConf('version', 'current version')
                persoversion = conf.getConf('persoversion', 'Test Type').upper()
		projectName = conf.getConf('project', 'Project name in check list file name')
		testtype = conf.getConf('testtype', 'Test Type').upper()

		resultRootPath = self.getResultRootPath(conf)
		print resultRootPath

		resultDirName = conf.getConf('resultdirname', 'test result dir name')
		xmlpath = '%s%s' %(resultRootPath + 'results/',resultDirName +'/')
		xmlzip = resultRootPath + 'results/' + resultDirName + '.zip'
		logs = resultRootPath + 'logs/' + resultDirName
		if testtype == 'CTS':
			xmlname = xmlpath + 'testResult.xml'
		elif testtype == 'GTS':
			xmlname = xmlpath + 'xtsTestResult.xml'
		print xmlname

		print 'Begin to analyse xml, please waiting...'
		xmlParser = XmlParser(xmlname)
		result_devices_dic = xmlParser.get_result_devices_dic(xmlname,conf)
		result_summary_dic = xmlParser.get_result_summary_dic(xmlname)
		testpackage_result_dic = xmlParser.get_testpackage_result_dic(xmlname)
		total_fail_num = xmlParser.get_total_fail_num()

		workbook = xlwt.Workbook()
		worksheet = workbook.add_sheet('Google_Test_Report')
		create_testcase_report(worksheet,total_fail_num,result_devices_dic,result_summary_dic,testpackage_result_dic)
		workbook.save('%s/attach/Google_%s_TestReport_%s_v%s+%s.xls' %(self.tempdir,testtype,projectName,version,persoversion))

		extAttachFileStr = conf.getConf('extattach', 'External attach files', 'none')
		if  extAttachFileStr != 'none':
			for fileName in extAttachFileStr.split(','):
				docmd('cp %s %s/attach' % (projBuildRoot + 'v' + version + '/' + fileName.strip(), self.tempdir))
		docmd('cp %smisc/SuperSpamReleaseMailFootLogoOneTouch.jpg %s/image/ReleaseMailLogo.jpg' % (getToolPath(), self.tempdir))
		docmd('cp %s %s/result' % (xmlzip, self.tempdir))
		docmd('cp -r %s %s/result' % (logs, self.tempdir))

		os.system('ssh user@10.92.35.20 "(rm -rfv /var/www/data/google_CTS_results/%s/%s/v%s+%s;mkdir -p /var/www/data/google_CTS_results/%s/%s/v%s+%s)"' % (projectName,testtype,version,persoversion,projectName,testtype,version,persoversion))
                docmd('scp -r %s/result/* user@10.92.35.20:/var/www/data/google_CTS_results/%s/%s/v%s+%s' % (self.tempdir,projectName,testtype,version,persoversion))

		self.__sendMail(conf,result_summary_dic,testpackage_result_dic)


    	''' this mothed user to send mail '''
    	def __sendMail(self,conf,summary_dic,testpackage_result_dic):
        	html = ''
        	html += self.getMailHeadHtml(conf)
        	html += self.getMailBodyHtml(conf,summary_dic,testpackage_result_dic)
        	html += self.getFootEMailHtml(conf)
		print '------------------------------html start----------------------------------'
		print html
		print '-------------------------------html end ----------------------------------'
        	self.sendMail(conf, html)


	def cleanup(self):
		conf = Config();
		if conf.getConf('cleanuptmpdir', 'Clean up the temp dir <yes|no>', 'yes') == 'yes':
			print "test over!!!!!"
			docmd('rm -rf %s' % conf.getConf('tempdir','temp dir'))
		


		


