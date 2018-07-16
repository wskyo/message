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
from CheckLunch import *
from InterfaceUtils import *
from MailUtils import *
from ChangeUtils import *

class AllProjectNewAlm(CheckLunch,InterfaceUtils,MailUtils,ChangeUtils):			
	def run(self):
		conf = Config();
		conf.addFromArg(sys.argv[1:])
		self.initConfFromXls(conf)
		self.initSomeConf(conf)

		self.allow_differ_prjconf_dic = {}
		self.host_prjconf_dic = {}
		self.tf_prjconf_dic = {}
		self.samekey_diffvalue_list = []
		self.host_prjconf_samekey_dic = {}
		self.tf_prjconf_samekey_dic = {}
		self.sidekey_set = ''
		self.host_prjconf_sidekey_dic = {}
		self.tf_prjconf_sidekey_dic = {}
		self.flag = ''
		self.allow_delete = {}
		self.host_add = {}
		self.allow_change = {}
		self.host_change = {}

		self.allow_tf_delete = {}
		self.tf_add = {}
		self.allow_tf_change = {}
		self.tf_change = {}

		self.host_result_dic = {}
		self.tf_result_dic = {}
		self.result_delete_dic = {}
		self.prFromCodeDict = {}

		self.tempdir = tempfile.mkdtemp('CheckLunch', 'temp', '/tmp')
		docmd('mkdir %s/image' % self.tempdir)
		docmd('mkdir %s/attach' % self.tempdir)
		docmd('mkdir %s/result' % self.tempdir)
		conf.getConf('tempdir', 'temp dir', self.tempdir)


		self.project = conf.getConf('project', 'project name')
		projBuildRoot = conf.getConf('projbuildroot', 'Project build root')
		version = conf.getConf('version', 'current version')
		buildDir = conf.getConf('builddir', 'Build directory', projBuildRoot+'v'+version)
		print "build dir %s" %buildDir
		self.buildDir = buildDir
		#self.buildDir = conf.getConf('codedir', 'code dir')

		print '------------------------------------------------------------'	
		print 'analysing lunch config in ProjectConfig.mk and device.mk ...'
		print '------------------------------------------------------------'

		self.allow_differ_prjconf_dic = self.getProjectConfigDict()
		#print self.allow_differ_prjconf_dic,type(self.allow_differ_prjconf_dic)

		self.host_prjconf_dic = self.getProjectConfigDic(self.buildDir,'pixi4_4_host')
		#print '---host_prjconf_dic---%s' %self.host_prjconf_dic
		self.tf_prjconf_dic = self.getProjectConfigDic(self.buildDir,'pixi4_4_tf')
		#print '---tf_prjconf_dic---%s' %self.tf_prjconf_dic

		self.samekey_diffvalue_list = self.getSameKeyDiffValueList(self.host_prjconf_dic,self.tf_prjconf_dic)
		#print '---samekey_diffvalue_list---%s' %self.samekey_diffvalue_list
		#print

		self.host_prjconf_samekey_dic = self.createSameKeyDic(self.samekey_diffvalue_list,self.host_prjconf_dic)
		self.tf_prjconf_samekey_dic = self.createSameKeyDic(self.samekey_diffvalue_list,self.tf_prjconf_dic)
		#print '---host_prjconf_samekey_dic---%s' %self.host_prjconf_samekey_dic
		#print '---tf_prjconf_samekey_dic---%s' %self.tf_prjconf_samekey_dic

		self.sidekey_set = self.getSideKeySet(self.host_prjconf_dic,self.tf_prjconf_dic)
		#print '---key only exsit one side---%s' %self.sidekey_set
		#print

		self.host_prjconf_sidekey_dic = self.createSideKeyDic(self.sidekey_set,self.host_prjconf_dic)
		self.tf_prjconf_sidekey_dic = self.createSideKeyDic(self.sidekey_set,self.tf_prjconf_dic)
		#print '---host_prjconf_sidekey_dic---%s' %self.host_prjconf_sidekey_dic
		#print '---tf_prjconf_sidekey_dic---%s' %self.tf_prjconf_sidekey_dic

		dictMerged_host = dict(self.host_prjconf_samekey_dic,**self.host_prjconf_sidekey_dic)
		dictMerged_tf = dict(self.tf_prjconf_samekey_dic,**self.tf_prjconf_sidekey_dic)
		#print '---dictMerged_host---%s' %dictMerged_host
		#print '---dictMerged_tf---%s' %dictMerged_tf

		#print
		#print '---dictMerged_host length---%s' %len(dictMerged_host)
		#print '---dictMerged_tf length---%s' %len(dictMerged_tf)

		self.flag,self.allow_delete,self.host_add,self.allow_change,self.host_change,self.allow_tf_delete,self.tf_add,self.allow_tf_change,self.tf_change = self.isNeedLunchNotice(self.allow_differ_prjconf_dic,dictMerged_host,dictMerged_tf)
		#print self.flag
		#print '---self.allow_delete---%s' %self.allow_delete
		#print '---self.host_add---%s' %self.host_add
		#print '---self.allow_change---%s' %self.allow_change
		#print '---self.host_change---%s' %self.host_change
		#print
		#print '---self.allow_tf_delete---%s' %self.allow_tf_delete
		#print '---self.tf_add---%s' %self.tf_add
		#print '---self.allow_tf_change---%s' %self.allow_tf_change
		#print '---self.tf_change---%s' %self.tf_change

		for dk in self.allow_delete.keys():	
			host_before_value = self.allow_delete[dk]
			if dk in self.host_prjconf_dic.keys():
				host_after_value = self.host_prjconf_dic[dk]
			else:
				host_after_value = 'noexist'
			self.host_result_dic[dk] = {'before':host_before_value,'after':host_after_value}

			tf_before_value = self.allow_tf_delete[dk]
			if dk in self.tf_prjconf_dic.keys():
				tf_after_value = self.tf_prjconf_dic[dk]
			else:
				host_after_value = 'noexist'
			self.tf_result_dic[dk] = {'before':tf_before_value,'after':tf_after_value}

		
		for ak in self.host_add.keys():
			host_before_value = 'noexsist'
			host_after_value = self.host_add[ak]
			self.host_result_dic[ak] = {'before':host_before_value,'after':host_after_value}

			tf_before_value = 'noexsist'
			tf_after_value = self.tf_add[ak]
			self.tf_result_dic[ak] = {'before':tf_before_value,'after':tf_after_value}
		#print '---self.host_result_dic---%s' %self.host_result_dic
		#print
		#print '---self.tf_result_dic---%s' %self.tf_result_dic
	
		pushdir(buildDir)
		
		self.__sendMail(conf)	

    	def __sendMail(self,conf):
        	html = ''
        	html += self.getMailHeadHtml(conf)
        	html += self.getMailBodyHtml(conf,self.host_result_dic,self.tf_result_dic)
		html += self.getChangeList(conf)
        	html += self.getFootEMailHtml(conf)
		print '------------------------------html start----------------------------------'
		print html
		print '-------------------------------html end ----------------------------------'
		if (self.flag == 'false' and len(self.haveChangeCommit) == 0):
			print "There is no change in lunch config files!!!"
		else:        		
			self.sendMail(conf, html)


        def cleanup(self):
		if self.conf.getConf('cleanuptmpdir', 'Clean up the temp dir <yes|no>', 'no') == 'yes':
			chdir('/')
			docmd('rm -rf %s' % self.workDir)

