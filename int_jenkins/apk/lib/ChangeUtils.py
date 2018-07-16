#!/usr/bin/python
#coding=utf-8

############################################################################
## Change Utils for get changelist message.
## add by jianbo.deng for superspam create 2013-08-27
###########################################################################

import sys
import os
import re
import commands
import MySQLdb
import xml.dom.minidom
import datetime
from Utils import *
from Config import *
from UserInfo import *
from DBUtils import *
from DBUtilsALM import *
import glob
from ReleaseStyle import *
from pyExcelerator import *
import string
from commands import *
import time
import copy
#import chardet



class ChangeUtils(ReleaseStyle):
	gitComment = []
	curDict = {}
	lastDict = {}
        dirverPRDict = {}
	allAppPrDict = {}
	prFromCodeDict = {}
	prNotGenericApkFromCodeDict = {}
	isMergeCommit = False
	nChanged = 0
	nCommit = 0 
	defRemote = None
	dateStr = ''
	DirverList = ''
	tempdir = ''
	authorStr = ''
	build_path = "/local/build/genericapp/"
	app_path = ''
	curversion = ''
	lasversion = ''
	web_path = ''
	appname = ''
	bugzillaAppName = ''
	bugzillaAppNameTwo = ''	
	relatedApkUrlDict = {}	
	#related_apk_change = True
	related_apk_change_dict = {}

	#### get changelite from this method
	def getChangeList(self, conf):
		html = ''
		html += '<p>Change List:</p>'
		html += '<p>'		
		changedFileInfoList = [] 
		if re.search("YES",self.test):
			self.initGitDic(conf)
		else:
			
			self.initGitDicAll(conf)		
		html += self.getChangeMessage(changedFileInfoList, conf)		
		#if len(self.curDict):
		#	html += 'Project added:<br />'
		#	nCount = 0 
		#	for key in sorted(self.curDict.keys()):
		#		nCount += 1
		#		html += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%d) %s<br />' % (nCount, key)
		#html += '<br />'
		#if len(self.lastDict):
		#	html += 'Project removed:<br />'
		#	nCount = 0 
		#	for key in sorted(self.lastDict.keys()):
		#		nCount += 1
		#		html += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%d) %s<br />' % (nCount, key)
		html += '</p>'	

		## must check before build code 
		if self.nChanged == 0 and conf.getConf('exitnonewchange', 'Exit if no new change from last version <yes|no>', 'yes') == 'yes':
			print '========================================'
			print '!!! NO NEW CHANGE SINCE LAST VERSION !!!****'
			print '========================================'

			sys.exit(1)
		return html


	####get manifest version git and revision
	def initGitDicAll(self, conf):	 
		versionnameInit = self.gitNameVersion.copy()	
		for gitname in sorted(versionnameInit.keys()):
			DownCodeDir = self.AlmCheckDict[gitname]['apkDowncodeGitDir']
			DownCodeBranch = self.AlmCheckDict[gitname]['apkCodeBranch']
			#self.getApkCode(gitname, DownCodeDir, DownCodeBranch)
			versions = versionnameInit.pop(gitname)
			print "the current and base version is %s" % versions
			self.appname = gitname
			self.curversion = versions[0]
			self.lasversion = versions[1]
			self.web_path = ("genericapp/" + "%s") % self.appname	 
			if self.appname == "JrdMusic":
				self.web_path = "genericapp/JrdMusicKK"  
			if self.appname == "JrdMusicL":
				self.web_path = "genericapp/JrdMusicL"     
			self.tagcurversion = ("INT-" + "%s" + "-%s" + "-RELEASE") % (self.appname,self.curversion)
			print self.tagcurversion 
			self.taglastversion = ("INT-" + "%s" + "-%s" + "-RELEASE") % (self.appname,self.lasversion)
			self.tagDict[gitname] = [self.tagcurversion,self.taglastversion]
			#if self.appname not in self.curDict.keys():
			#	self.curDict[self.appname] = [self.web_path, self.tagcurversion]
			#	self.lastDict[self.appname] = [self.web_path, self.taglastversion]
				
			DownCodeDir_list = DownCodeDir.split(',')
			DownCodeBranch_list = self.AlmCheckDict[gitname]['apkGitWebLink'].split('\n')
			igit = 0
			OneApkGitDict = {}
			OneApkcurDict = {}
			OneApklastDict = {}
			for itemDownCodeDir in DownCodeDir_list:
				includegitname = self.getgitNamefromgitpath(itemDownCodeDir)
				if includegitname != "":
					if includegitname not in OneApkGitDict.keys():
						OneApkGitDict[includegitname]=[includegitname,DownCodeBranch_list[igit]]
						self.getApkCode(includegitname, itemDownCodeDir, DownCodeBranch)
					if includegitname not in OneApkcurDict.keys():
						OneApkcurDict[includegitname] = [itemDownCodeDir,self.tagcurversion]
						OneApklastDict[includegitname] = [itemDownCodeDir,self.taglastversion]
				igit = igit +1 
			
			self.AlmCheckDict[self.appname]['gitlist'] = OneApkGitDict
			self.curDict[self.appname] = OneApkcurDict
			self.lastDict[self.appname] = OneApklastDict
		
			print self.tagDict
			print self.curDict
			print self.lastDict
			
			if self.AlmCheckDict[self.appname]['related_apk_name']:
				for eachRelatedApk in self.AlmCheckDict[self.appname]['related_apk_name'].strip().split(','):
					if not eachRelatedApk:
						continue
					if self.AlmCheckDict[eachRelatedApk]['apkCodeBranch'] == self.AlmCheckDict[self.appname]['apkCodeBranch']:
						self.curDict[eachRelatedApk] = self.curDict[self.appname]
						self.lastDict[eachRelatedApk] = self.lastDict[self.appname]	


	def initGitDic(self, conf):
		self.appname = conf.getConf('appname','the app name')
		self.curversion = conf.getConf('version','Current version of this app')
		self.lasversion = conf.getConf('baseversion','last version of this app')
		DownCodeDir = self.AlmCheckDict[self.appname]['apkDowncodeGitDir']
		DownCodeBranch = self.AlmCheckDict[self.appname]['apkCodeBranch']
		#self.getApkCode(self.appname, DownCodeDir, DownCodeBranch)
		related_apk_name = self.AlmCheckDict[self.appname]['related_apk_name']
		self.app_path = self.build_path + self.appname
		self.web_path = ("genericapp/" + "%s") % self.appname
		tagcurversion = ("INT-" + "%s" + "-%s" + "-RELEASE") % (self.appname,self.curversion)
		taglastversion = ("INT-" + "%s" + "-%s" + "-RELEASE") % (self.appname,self.lasversion)
		self.tagDict[self.appname] = [tagcurversion,taglastversion]
		#self.curDict[self.appname] = [self.web_path, tagcurversion]
		#self.lastDict[self.appname] = [self.web_path, taglastversion]
		VersionsMail = self.gitNameVersion.copy()
		
		DownCodeDir_list = self.AlmCheckDict[self.appname]['apkDowncodeGitDir'].split(',')
		DownCodeBranch_list = self.AlmCheckDict[self.appname]['apkGitWebLink'].split('\n')
		igit = 0
		OneApkGitDict = {}
		OneApkcurDict = {}
		OneApklastDict = {}
		for itemDownCodeDir in DownCodeDir_list:
			includegitname = self.getgitNamefromgitpath(itemDownCodeDir)
			if includegitname != "":
				if includegitname not in OneApkGitDict.keys():
					OneApkGitDict[includegitname]=[includegitname,DownCodeBranch_list[igit]]
					self.getApkCode(includegitname, itemDownCodeDir, DownCodeBranch)
				if includegitname not in OneApkcurDict.keys():
					OneApkcurDict[includegitname] = [itemDownCodeDir,tagcurversion]
					OneApklastDict[includegitname] = [itemDownCodeDir,taglastversion]
			igit = igit +1 
			
		self.AlmCheckDict[self.appname]['gitlist'] = OneApkGitDict
		self.curDict[self.appname] = OneApkcurDict
		self.lastDict[self.appname] = OneApklastDict
		
		print self.tagDict
		print self.curDict
		print self.lastDict
		
		for eachRelatedApk in self.AlmCheckDict[self.appname]['related_apk_name'].strip().split(','):
			if not eachRelatedApk:
				continue
			if self.AlmCheckDict[eachRelatedApk]['apkCodeBranch'] == self.AlmCheckDict[self.appname]['apkCodeBranch']:
				self.curDict[eachRelatedApk] = self.curDict[self.appname]
				self.lastDict[eachRelatedApk] = self.lastDict[self.appname]
				continue
			self.app_path = self.build_path + eachRelatedApk
			print "The app dir is %s" % self.app_path
			self.web_path = ("genericapp/" + "%s") % eachRelatedApk
			versions = VersionsMail.pop(eachRelatedApk)
			self.curversion = versions[0]
			self.lasversion = versions[1]
			tagcurversion = ("INT-" + "%s" + "-%s" + "-RELEASE") % (eachRelatedApk,self.curversion)
			taglastversion = ("INT-" + "%s" + "-%s" + "-RELEASE") % (eachRelatedApk,self.lasversion)
			self.curDict[eachRelatedApk] = [self.web_path, tagcurversion]
			self.lastDict[eachRelatedApk] = [self.web_path, taglastversion]
			self.tagDict[eachRelatedApk] = [tagcurversion,taglastversion]

	def checkLastVersionTag(self, lastVersionTag):
		checkResult = commands.getoutput('git tag | grep "%s"' % lastVersionTag)		
		if re.match(lastVersionTag,checkResult):
			print "The last tag is existing"
			return lastVersionTag
		else:
			lastTenLog = commands.getoutput('git log --pretty=oneline -10')
			lastTenLogList = lastTenLog.split("\n")
			lastCommit = lastTenLogList[len(lastTenLogList) -1]
			match = re.match('^([0-9a-f]{40}).*',lastCommit)
			if match:
				return match.group(1)		


	####get sdm change, apk change, update patch 
	def getChangeMessage(self, changedFileInfoList,conf):		
		html = ''
		numapk = 0 
		for fkey in sorted(self.curDict.keys()):
			ischange = 0
			isgitNum = 0
			githtml = ''
			tmpcurDict =self.curDict[fkey]
			tmplastDict =self.lastDict[fkey]
			for key in sorted(tmpcurDict.keys()):
				isgitNum += 1	
				if fkey not in self.related_apk_change_dict.keys():
					self.related_apk_change_dict[fkey] = True	
				if key in tmplastDict.keys():					
					curVal = tmpcurDict.pop(key)
					lastVal = tmplastDict.pop(key)
					if key[:8] in ['version', 'version-', 'version_']:
						continue
					if os.path.basename(curVal[0])[:8] in ['version', 'version-', 'version_']:
						continue
					if curVal[1] != lastVal[1]:
						print "The key is %s" % key
						dir_t = self.buildDir + key
						print "dir_t",dir_t
						pushdir(dir_t) ###cd git path
						os.system('git pull')
						os.system('git fetch --tags')
						lastVal[1] = self.checkLastVersionTag(lastVal[1])
						revListStr = commands.getoutput('git rev-list %s..%s' % (lastVal[1], curVal[1])).strip()
						
						#add by lyf for adjust is change or not,ignore version commit
						i_versionchange = 0
						for commit in revListStr.split('\n'):
							if (not self.adjustVersionCommint(commit)):
								i_versionchange += 1 
						if i_versionchange <=0: 
							print '========================================'
							print '!!! NO NEW CHANGE SINCE LAST VERSION !!!'
							print '========================================'
					
							#self.related_apk_change_dict[fkey] = False
							if ischange ==0:
								githtml += '&nbsp;&nbsp;%s) %s<br />' % (isgitNum,key) 
								continue
						#end by lyf	
						tagListStr = commands.getoutput('git show-ref --dereference --tags').strip()
						reviewChangesDict = {} ###user to get remote review change
						reviewChangesDict = self.getReviewDict()
						self.defRemote = "origin"
						if self.defRemote: ### if git is remote
							for changeLine in commands.getoutput('git ls-remote %s refs/changes/*' % self.defRemote).split('\n'):
								match = re.search('([0-9a-f]{40})\s+refs/changes/\d+/(\d+)/\d+', changeLine)
								if match:
									reviewChangesDict[match.group(1)] = match.group(2)


						if revListStr:
							self.nChanged += 1
							ischange += 1
							#html += '%d) %s<br />' % (self.nChanged, key) ##number and git name
							githtml += '&nbsp;&nbsp;%d) %s<br />' % (isgitNum, key) ##number and git name
							self.sdmChangedInCommitsBool = False
							sdmChangeToPRDict = {}						
							sdmChangeInfoDict = {}
							sdmauthor = {}
							for commit in revListStr.split('\n'):
								commit = commit.strip()
								if re.match('^qaep/*',curVal[0]):
									curVal[0]=curVal[0][5:]

								#if key in self.AlmCheckDict.keys() and 'apkGitWebLink' in self.AlmCheckDict[key].keys():
								tmpgitLnk = self.getgitwebLink(key,self.AlmCheckDict[self.appname]['gitlist'].values())
								if tmpgitLnk !='' and 'apkGitWebLink' in self.AlmCheckDict[fkey].keys():
									#gitLink = self.AlmCheckDict[key]['apkGitWebLink']
									gitLink = tmpgitLnk
									
									if gitLink:
										commitUrl = '%s%s' % (gitLink, commit)
									else:
										commitUrl = 'http://10.92.32.10/sdd1/gitweb-genericapp/?p=%s.git;a=commit;h=%s' % (key, commit)
								else:
									commitUrl = 'http://10.92.32.10/sdd1/gitweb-genericapp/?p=%s.git;a=commit;h=%s' % (key, commit)
								if commit in reviewChangesDict.keys():
									reviewUrl = 'http://10.92.32.10:8081/#change,%s' % reviewChangesDict[commit]
								else:
									reviewUrl = ''
								if not re.match('[0-9a-f]{40}', commit):
									continue
								firstComment = ''
								self.gitComment = []
							
								firstComment = self.getGitLog(changedFileInfoList, commit, firstComment)
								githtml += self.getGitCreateChangeMes(changedFileInfoList, curVal,firstComment,reviewUrl, tagListStr, commitUrl, commit, conf, fkey, sdmChangeToPRDict,sdmauthor)
								self.getDirverLog(changedFileInfoList,commit, firstComment, curVal, tagListStr,key,commitUrl)
							print "key is %s" % key
						
							if self.sdmChangedInCommitsBool:
								self.getSdmInfoCommandsBool(curVal, lastVal,sdmChangeToPRDict,sdmChangeInfoDict)
							if sdmChangeInfoDict and key not in self.sdmChangeInfoDict.keys():
								self.sdmChangeInfoDict[key] = sdmChangeInfoDict	
							if sdmauthor and key not in self.sdmauthor.keys():
								self.sdmauthor[key] = sdmauthor					
							#if not re.search("YES",self.test):	
							self.allAppPrDict[key] = self.dirverPRDict
							self.dirverPRDict = {}
							self.nCommit = 0
						#if self.AlmCheckDict[key]['related_apk_name']:
							#html += self.getRelatedChangelist(key,self.AlmCheckDict[key]['related_apk_name'],self.nChanged)

							githtml += '<br />'
						popdir()
					
			if ischange ==0 and fkey in self.gitNameVersion.keys() and conf.getConf('exitnonewchange', 'Exit if no new change from last version <yes|no>', 'yes') == 'yes':
				del self.gitNameVersion[fkey]
				self.AlmCheckDict[fkey]['ischange'] = False
			else:
				numapk += 1
				html += '<b>%d: %s: </b><br />' %(numapk,fkey)+ githtml
				self.AlmCheckDict[fkey]['ischange'] = True
				
		
		return html
	####get DirverCommit  , commitUrl   reviewUrl,  
	def getDirverLog(self,changedFileInfoList,commit, firstComment,curVal,tagListStr, key,commitUrl):
		bugNumber = ''
		prStrFixedList = []
		goodComment = ''
		moduleImpact = ''
		tagName = ''
		commitDesc= ''
		tagList = []
		tagInDescStr = ''
		author = ''
		isMergeCommit = False

		gitLog = commands.getoutput('git log -n1 --raw %s' % commit.strip())
		for line in gitLog.split('\n'):
			match = re.match('^\s\s\s\s(.*)', line)
			if match:
				if not firstComment:
					firstComment = match.group(1)
			match = re.match('^Author:\s(.+)', line)
			if match:
				self.authorStr = match.group(1).strip()
				match = re.match('(.*)\s(<.*>$)',self.authorStr)
				if match:					
					author = match.group(2)  
			match = re.match('^Date:\s(.+)', line)
			if match:
				self.dateStr = match.group(1).strip()
			match = re.match('^Merge:\s', line)
			if match:
				isMergeCommit = True
			match = re.search('###%%%bug\snumber:(.+)', line)
			if match:
				bugNumber = match.group(1).strip()
				if bugNumber.__contains__("###%%%"):
					bugNumber = (bugNumber.split('###%%%')[0]).strip()
			
			match = re.match(':(\w{6})\s(\w{6})\s(\w{7})\.\.\.\s(\w{7})\.\.\.\s([AMD])\s+(.+)', line)
			if match:
				if match.group(5) == 'M':
					tmpActStr = 'Modify'
				if match.group(5) == 'A':
					tmpActStr = 'Add'
				if match.group(5) == 'D':
					tmpActStr = 'Delete'
				#changedFileInfoList.append({'filename':match.group(6), 'action':tmpActStr, 'last_commit':match.group(3), 'current_commit':match.group(4),'commit':str(commit),'author':self.authorStr})
			match = re.search('###%%%comment:(.+)', line)
			if match:
				goodComment = match.group(1).strip()
				if goodComment.__contains__("###%%%"):
					goodComment = (goodComment.split('###%%%')[0]).strip()
			if bugNumber and goodComment:
				commitDesc = 'PR %s: %s' % (bugNumber, goodComment)
			else:
				commitDesc = firstComment



			for line in tagListStr.split('\n'):
				match = re.match('^([0-9a-f]{40})\s+refs/tags/([^^]+)', line.strip())
				if match:
					if match.group(1) == commit:
						tagList.append(match.group(2).strip())
						tagName = '(%s)' % match.group(2)
		if author and (not isMergeCommit):
			self.nCommit += 1
			self.dirverPRDict[self.nCommit]={}
			self.dirverPRDict[self.nCommit]['project'] = key
			self.dirverPRDict[self.nCommit]['commit'] = commitDesc
			self.dirverPRDict[self.nCommit]['date'] = self.dateStr
			self.dirverPRDict[self.nCommit]['author'] = author
			self.dirverPRDict[self.nCommit]['tag'] = tagName
			self.dirverPRDict[self.nCommit]['url'] = commitUrl


	##get command message
	def getGitCreateChangeMes(self,changedFileInfoList, curVal, firstComment, reviewUrl, tagListStr, commitUrl, commit, conf, key,sdmChangeToPRDict,sdmauthor):
		bugNumber = ''
		prStrFixedList = []
		goodComment = ''
		moduleImpact = ''
		testSuggestion = ''
		commitDesc= ''
		tagList = []
		tagInDescStr = ''
		for line in self.gitComment:
			match = re.search('###%%%bug\snumber:(.+)', line)
			if match:
				bugNumber = match.group(1).strip()
				if bugNumber.__contains__("###%%%"):
					bugNumber = (bugNumber.split('###%%%')[0]).strip()
			match = re.search('###%%%comment:(.+)', line)
			if match:
				goodComment = match.group(1).strip()
				if goodComment.__contains__("###%%%"):
					goodComment = (goodComment.split('###%%%')[0]).strip()
			match = re.search('###%%%Module_Impact:(.+)', line)
			if match:
				moduleImpact = match.group(1).strip()
				if moduleImpact.__contains__("###%%%"):
					moduleImpact = (moduleImpact.split('###%%%')[0]).strip()
			match = re.search('###%%%Test_Suggestion:(.+)', line)
			if match:
				testSuggestion = match.group(1).strip()
				if testSuggestion.__contains__("###%%%"):
					testSuggestion = (testSuggestion.split('###%%%')[0]).strip()
		#add by lyf,fixed no PR list
		if bugNumber in ['0','00','000','0000','00000','000000']:
			bugNumber = ''
		if bugNumber:
			for bugId in map(lambda x: int(x), re.findall('\d+', bugNumber)):
				if 'ALM' in self.AlmCheckDict[key].values() and self.getPrFromCodeListForOneApkALM(conf,bugId,key):
					if key not in self.prFromCodeDict.keys():
						self.prFromCodeDict[key] = {}							
					if bugId not in self.prFromCodeDict[key].keys():					
						self.prFromCodeDict[key][bugId] = {'moduleImpact': moduleImpact, 'testSuggestion': testSuggestion, 'localPath': set([key])}
					else:
						if self.prFromCodeDict[key][bugId]['moduleImpact'] and self.prFromCodeDict[key][bugId]['moduleImpact'] != moduleImpact:
							self.prFromCodeDict[key][bugId]['moduleImpact'] += '\n%s' % moduleImpact
						if self.prFromCodeDict[key][bugId]['testSuggestion'] and self.prFromCodeDict[key][bugId]['testSuggestion'] != testSuggestion:
							self.prFromCodeDict[key][bugId]['testSuggestion'] += '\n%s' % testSuggestion
					self.prFromCodeDict[key][bugId]['localPath'].add(key)

				elif 'Bugzilla' in self.AlmCheckDict[key].values() and self.getPrFromCodeListForOneApk(bugId,key):
					if key not in self.prFromCodeDict.keys():
						self.prFromCodeDict[key] = {}							
					if bugId not in self.prFromCodeDict[key].keys():					
						self.prFromCodeDict[key][bugId] = {'moduleImpact': moduleImpact, 'testSuggestion': testSuggestion, 'localPath': set([key])}
					else:
						if self.prFromCodeDict[key][bugId]['moduleImpact'] and self.prFromCodeDict[key][bugId]['moduleImpact'] != moduleImpact:
							self.prFromCodeDict[key][bugId]['moduleImpact'] += '\n%s' % moduleImpact
						if self.prFromCodeDict[key][bugId]['testSuggestion'] and self.prFromCodeDict[key][bugId]['testSuggestion'] != testSuggestion:
							self.prFromCodeDict[key][bugId]['testSuggestion'] += '\n%s' % testSuggestion
					self.prFromCodeDict[key][bugId]['localPath'].add(key)
				else:
					if key not in self.prNotGenericApkFromCodeDict.keys():
						self.prNotGenericApkFromCodeDict[key] = []
					prNotGenericApkFromCodeDict = {}					
					if bugId not in self.notClonedBugs:
						self.notClonedBugs.append(bugId)
						prNotGenericApkFromCodeDict[bugId] = {'moduleImpact': moduleImpact, 'testSuggestion': testSuggestion, 'localPath': set([key])}					
						if prNotGenericApkFromCodeDict[bugId]['moduleImpact'] and prNotGenericApkFromCodeDict[bugId]['moduleImpact'] != moduleImpact:
							prNotGenericApkFromCodeDict[bugId]['moduleImpact'] += '\n%s' % moduleImpact
						if prNotGenericApkFromCodeDict[bugId]['testSuggestion'] and prNotGenericApkFromCodeDict[bugId]['testSuggestion'] != testSuggestion:
							prNotGenericApkFromCodeDict[bugId]['testSuggestion'] += '\n%s' % testSuggestion
						prNotGenericApkFromCodeDict[bugId]['localPath'].add(key)
						if 'ALM' in self.AlmCheckDict[key].values():							
							self.getBugInforFromCodeButNotOfGenericappALm(conf,bugId,key,prNotGenericApkFromCodeDict)
							self.bugzillaUrlBase = 'https://alm.tclcom.com:7003/im/issues?selection=%s'

						elif 'Bugzilla' in self.AlmCheckDict[key].values():
							self.getBugInforFromCodeButNotOfGenericapp(bugId,key,prNotGenericApkFromCodeDict)
							self.bugzillaUrlBase = 'http://bugzilla.tcl-ta.com/show_bug.cgi?id=%s'
						self.prNotGenericApkFromCodeDict[key].append(prNotGenericApkFromCodeDict)

		if bugNumber and goodComment:
			#print chardet.detect(goodComment)
			commitDesc = 'Fix PR %s: %s' % (bugNumber, goodComment.decode('utf-8'))
		elif (not goodComment):
			commitDesc = firstComment
		else:
			commitDesc = goodComment
		if (not bugNumber) and (not self.isMergeCommit):
			self.patchWithoutPRList.append([self.authorStr, commitDesc, commitUrl])

		for line in tagListStr.split('\n'):
			match = re.match('^([0-9a-f]{40})\s+refs/tags/([^^]+)', line.strip())
			if match:
				if match.group(1) == commit:
					tagList.append(match.group(2).strip())
		if reviewUrl:
			reviewHtmlCont = '&nbsp;[<a href="%s">review</a>]' % reviewUrl
		else:
			reviewHtmlCont = ''
		if tagList:
			tmpList = []
			tagInDescStr = '&nbsp;('
			for line in tagList:
				tmpList.append(line)
			tagInDescStr += ', '.join(tmpList)
			tagInDescStr += ')'

		html = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="%s">%s</a>%s%s------%s<br />' % (commitUrl, commitDesc, reviewHtmlCont, tagInDescStr,self.authorStr)

		strCustStorePath = conf.getConf('custstorepath', 'Custsore path', 'none')
		#add by lyf,fixed no apk list
		strCustStorePath = '%swcustores' %strCustStorePath
		if strCustStorePath != 'none' and key == strCustStorePath:
			for fileInfoDict in changedFileInfoList:
				match = re.search('\.[aA][pP][kK]', fileInfoDict['filename'])
				if not match:
					continue
				if fileInfoDict['filename'] not in self.apkChangeInfoDict.keys():
					self.apkChangeInfoDict[fileInfoDict['filename']] = []
				self.apkChangeInfoDict[fileInfoDict['filename']].insert(0, {'action':fileInfoDict['action'], 'url':commitUrl, 'date':self.dateStr, 'author':self.authorStr})
		for fileInfoDict in changedFileInfoList:
			if str(fileInfoDict['commit']) == str(commit):
				match = re.search('\.[pP][lL][fF]', fileInfoDict['filename'])
				if match:
					self.sdmChangedInCommitsBool = True
					if bugNumber:
						if bugNumber.find(','):
							allplfBugs=bugNumber.split(',')
							for eachPlfBug in allplfBugs:
								if eachPlfBug not in prStrFixedList:
									prStrFixedList.append(str(eachPlfBug))
						else:
							prStrFixedList.append(str(bugNumber))
					else:
						prStrFixedList.append("")	
					lastPlfDomPass1 = None
					curPlfDomPass1 = None
					try:
						if fileInfoDict['action'] == 'Add':
							curPlfDomPass1 = xml.dom.minidom.parseString(commands.getoutput('git cat-file blob %s' % fileInfoDict['current_commit']).strip())
						if fileInfoDict['action'] == 'Delete':
							lastPlfDomPass1 = xml.dom.minidom.parseString(commands.getoutput('git cat-file blob %s' % fileInfoDict['last_commit']).strip())
						if fileInfoDict['action'] == 'Update':
							lastPlfDomPass1 = xml.dom.minidom.parseString(commands.getoutput('git cat-file blob %s' % fileInfoDict['last_commit']).strip())
							curPlfDomPass1 = xml.dom.minidom.parseString(commands.getoutput('git cat-file blob %s' % fileInfoDict['current_commit']).strip())
					except xml.parsers.expat.ExpatError:
						continue	
					for oneChangeSdm in self.getSdmChangeList(lastPlfDomPass1, curPlfDomPass1):
						tmpKeyName = fileInfoDict['filename']+'/'+oneChangeSdm
						if tmpKeyName not in sdmChangeToPRDict.keys():
							sdmChangeToPRDict[tmpKeyName] = []
						for onePR in prStrFixedList:
							if not onePR in sdmChangeToPRDict[tmpKeyName]:
								sdmChangeToPRDict[tmpKeyName].append(str(onePR))
						if tmpKeyName not in sdmauthor.keys():
							sdmauthor[tmpKeyName] = []
							sdmauthor[tmpKeyName].append(str(fileInfoDict['author']))
		return html

	####get git log
	####the method will init gitComment, changedFileInfoList, firstComment, isMergeCommit
	def getGitLog(self, changedFileInfoList, commit, firstComment):
		self.changeApkAndSmdInfoList=[]
		gitLog = commands.getoutput('git log -n1 --raw %s' % commit.strip())
		for line in gitLog.split('\n'):
			match = re.match('^\s\s\s\s(.*)', line)
			if match:
				if not firstComment:
					firstComment = match.group(1)
				self.gitComment.append(match.group(1))
			match = re.match('^Author:\s(.+)', line)
			if match:
				self.authorStr = match.group(1).strip()
			match = re.match('^Date:\s(.+)', line)
			if match:
				self.dateStr = match.group(1).strip()
			match = re.match('^Merge:\s', line)
			if match:
				self.isMergeCommit = True
			match = re.match(':(\w{6})\s(\w{6})\s(\w{7})\.\.\.\s(\w{7})\.\.\.\s([AMD])\s+(.+)', line)
			if match:
				if match.group(5) == 'M':
					tmpActStr = 'Modify'
				if match.group(5) == 'A':
					tmpActStr = 'Add'
				if match.group(5) == 'D':
					tmpActStr = 'Delete'
				changedFileInfoList.append({'filename':match.group(6), 'action':tmpActStr, 'last_commit':match.group(3), 'current_commit':match.group(4), 'commit':str(commit),'author':self.authorStr})
				self.changeApkAndSmdInfoList.append({'filename':match.group(6), 'action':tmpActStr,'date':self.dateStr,'commit':str(commit),'author':self.authorStr})
		return firstComment

	## this method have some error
	def getSdmChangeList(self, lastDom, curDom):
		if lastDom:
			lastDict = self.getPlfSdmValDict(lastDom)
		if curDom:
			curDict = self.getPlfSdmValDict(curDom)
		if lastDom and curDom:
			for key in lastDict.keys():
				if key in curDict.keys():
					if curDict[key] == lastDict[key]:
						curDict.pop(key)
					lastDict.pop(key)
			resList = list(set(lastDict.keys() + curDict.keys()))
		elif not lastDom and not curDom:
			resList = []
			return resList
		elif not lastDom:
			resList = list(set(curDict.keys()))
		elif not curDom:
			resList = list(set(lastDict.keys()))
		else:
			resList = []
		resList.sort()
		return resList


	def getVerNumber(self,conf,appname):
		if appname == "JrdGallery2" or appname == "JrdLauncherM" or appname == "JrdSetupWizard":
			appname = "%s_SDD1" %appname
		TelewebApk = getoutput("ssh sl_hz_hran@10.92.32.26 ls /mfs/teleweb/genericapp/%s | grep '0' | sort | tail -1" % appname)
		match = re.match('.*\.(\d+)\.(\d+)$',TelewebApk)
		if match:
			lastversion = match.group(1)
			if re.match('^000(\d)',lastversion):
				match = re.match('^000(\d)',lastversion)
				num = (int(match.group(1))+1)
				if num==10:
					curversion = "0010"
				else:
					curversion = ("000"+ "%s") % num

			elif re.match('^00(\d\d)',lastversion):
				match = re.match('^00(\d\d)',lastversion)
				num = (int(match.group(1))+1)
				if num==100:
					curversion = "0100"
				else:
					curversion = ("00"+ "%s") % num

			elif re.match('^0(\d\d\d)',lastversion):
				match = re.match('^0(\d\d\d)',lastversion)
				num = (int(match.group(1))+1)
				if num==1000:
					curversion = "1000"
				else:
					curversion = ("0" + "%s")  % num
			elif re.match('^(\d+)',lastversion):
				match = re.match('^(\d+)',lastversion)
				num = (int(match.group(1))+1)
				curversion = "%s" % num

			NextTelewebApk = TelewebApk.replace(lastversion,curversion)
			print "The lastversion is %s" % TelewebApk
			print "The current version is %s" % NextTelewebApk

			match = re.match('v(.*)',TelewebApk)
			if match:
				TelewebApk = match.group(1)

			match = re.match('v(.*)',NextTelewebApk)
			if match:
				NextTelewebApk = match.group(1)
			print [NextTelewebApk,TelewebApk]		
			return [NextTelewebApk,TelewebApk]
		else:
			print "cannot get the apk version from teleweb"
			sys.exit(1)



	def gitVersionFromArg(self,conf):
		line = conf.getConf('apkname', 'each apk name seperate with @')
		curversion = conf.getConf('version','Current version of this app','no')
		lasversion = conf.getConf('baseversion','last version of this app','no')
		if line == '':			
			print "The apk name is none,please enter the right apk name in arg"
                        sys.exit(1)
		gitlist = string.split(line,"@")
		for apkname in gitlist:
			if curversion != 'no':
			    [version, lastversion] = [curversion,lasversion]
			else:
			    [version, lastversion] = self.getVerNumber(conf,apkname)
			#self.gitNameVersion[apkname]=['5.1.6.1.0004.0', '5.1.6.1.0003.0']
			self.gitNameVersion[apkname] = [version,lastversion]
		return self.gitNameVersion


	def getCurrAndLaseTime(self,conf,tagcurversion,taglastversion):		
		curVerTimeStr = ''
		lastVerTimeStr = ''			
		gitLog = commands.getoutput('git log -n1 --raw %s' % tagcurversion.strip())
		for line in gitLog.split('\n'):			
			match = re.match('^Date:\s(.+)', line)
			if match:
				curVerTimeStr = match.group(1).strip()
				curVerTimeStr = self.getTime(curVerTimeStr)
		gitLog = commands.getoutput('git log -n1 --raw %s' % taglastversion.strip())

		for line in gitLog.split('\n'):			
			match = re.match('^Date:\s(.+)', line)
			if match:
				lastVerTimeStr = match.group(1).strip()
				lastVerTimeStr = self.getTime(lastVerTimeStr)
		return lastVerTimeStr,curVerTimeStr


	def getTime(self,timeFormat):
		match = re.match('(.+)\+\d+',timeFormat)
		if match:
			timeFormat = match.group(1).strip()
			timeFormat = time.strptime(timeFormat, "%a %b %d %H:%M:%S %Y")
			timeFormat = time.strftime("%Y-%m-%d %H:%M:%S",timeFormat)
		return timeFormat


	#get code
	def getApkCode(self, appname, gitDir, gitBranch):
		app_path = self.buildDir + appname
		if not os.path.isdir(app_path):
			os.chdir(self.buildDir)
			docmd('git clone git@10.92.32.10:%s -b %s %s' % (gitDir, gitBranch, appname))
					
		else:	
			os.chdir(app_path)		
			os.system('git reset --hard HEAD; git clean -df')
			os.system('git pull')
			os.chdir(self.buildDir)


	def copyPlfToTestDir(self, appname, version):
		plfDirName = "/local/build/genericapp/%s/plf" % appname
		print "Now start to copy plf feldors to dir"
		if os.path.exists(plfDirName):
			docmd('scp -r %s user@10.92.35.20:/var/www/data/genericapp/%s/v%s/' % (plfDirName,appname,version))
		else:
			print "No plf files to be copied"


	def getSdmInfoCommandsBool(self, curVal, lastVal,sdmChangeToPRDict,sdmChangeInfoDict):
		sdmTempDir = self.tempdir+'/sdmchange'
                if not os.path.exists(sdmTempDir):
			docmd('mkdir %s' % sdmTempDir)
		if commands.getoutput('git ls-tree %s' % lastVal[1]):
			docmd('git archive --prefix=last/ %s | tar xf - -C %s' % (lastVal[1], sdmTempDir))
		elif not os.path.exists('%s/last' % (sdmTempDir)):
			docmd('mkdir %s/last' % sdmTempDir)
		if commands.getoutput('git ls-tree %s' % curVal[1]):
			docmd('git archive --prefix=cur/ %s | tar xf - -C %s' % (curVal[1], sdmTempDir))
		elif not os.path.exists('%s/cur' % (sdmTempDir)):
			docmd('mkdir %s/cur' % sdmTempDir)
		pushdir(sdmTempDir)
		lastPlfInfoInGitDict = {}
		curPlfInfoInGitDict = {}
		for plfFileName in commands.getoutput('find last/ -iname "*.plf"').split('\n'):
			self.addPlfInfoToDict(plfFileName, lastPlfInfoInGitDict)
		for plfFileName in commands.getoutput('find cur/ -iname "*.plf"').split('\n'):
			self.addPlfInfoToDict(plfFileName, curPlfInfoInGitDict)
		for keySdmName in lastPlfInfoInGitDict.keys():
			updateinfor = ''
			supdate = False
			if keySdmName in curPlfInfoInGitDict.keys():
				if not lastPlfInfoInGitDict[keySdmName]['value'] == curPlfInfoInGitDict[keySdmName]['value']:
					updateinfor = updateinfor+ "\n" + u'Value:' + lastPlfInfoInGitDict[keySdmName]['value'] + '->' + curPlfInfoInGitDict[keySdmName]['value']
					supdate = True
				if not lastPlfInfoInGitDict[keySdmName]['desc'] == curPlfInfoInGitDict[keySdmName]['desc']:
					updateinfor = updateinfor+ "\n" + u'Desc:' + lastPlfInfoInGitDict[keySdmName]['desc'] + '->' + curPlfInfoInGitDict[keySdmName]['desc']
					supdate = True
				if not lastPlfInfoInGitDict[keySdmName]['cname'] == curPlfInfoInGitDict[keySdmName]['cname']:
					updateinfor = updateinfor+ "\n" + u'Cname:' + lastPlfInfoInGitDict[keySdmName]['cname'] + '->' + curPlfInfoInGitDict[keySdmName]['cname']
					supdate = True
				if not lastPlfInfoInGitDict[keySdmName]['ctype'] == curPlfInfoInGitDict[keySdmName]['ctype']:
					updateinfor = updateinfor+ "\n" + u'Ctype:' + lastPlfInfoInGitDict[keySdmName]['ctype'] + '->' + curPlfInfoInGitDict[keySdmName]['ctype']
					supdate = True
				if not lastPlfInfoInGitDict[keySdmName]['array'] == curPlfInfoInGitDict[keySdmName]['array']:
					updateinfor = updateinfor+ "\n" + u'Array:' + lastPlfInfoInGitDict[keySdmName]['array'] + '->' + curPlfInfoInGitDict[keySdmName]['array']
					supdate = True
				if not lastPlfInfoInGitDict[keySdmName]['metatype'] == curPlfInfoInGitDict[keySdmName]['metatype']:
					updateinfor = updateinfor+ "\n" + u'Metatype:' + lastPlfInfoInGitDict[keySdmName]['metatype'] + '->' + curPlfInfoInGitDict[keySdmName]['metatype']
					supdate = True
				if not lastPlfInfoInGitDict[keySdmName]['iscusto'] == curPlfInfoInGitDict[keySdmName]['iscusto']:
					updateinfor = updateinfor+ "\n" + u'Iscusto:' + lastPlfInfoInGitDict[keySdmName]['iscusto'] + '->' + curPlfInfoInGitDict[keySdmName]['iscusto']
					supdate = True
				if not lastPlfInfoInGitDict[keySdmName]['feture'] == curPlfInfoInGitDict[keySdmName]['feture']:
					updateinfor = updateinfor+ "\n" + u'Feture:' + lastPlfInfoInGitDict[keySdmName]['feture'] + '->' + curPlfInfoInGitDict[keySdmName]['feture']
					supdate = True
				if supdate is True:				
					sdmChangeInfoDict[keySdmName] = {'custo':curPlfInfoInGitDict[keySdmName]['iscusto'],'value':curPlfInfoInGitDict[keySdmName]['value'], 'desc':curPlfInfoInGitDict[keySdmName]['desc'], 'comment':updateinfor, 'action':'Update', 'pr': [] if not keySdmName in sdmChangeToPRDict.keys() else sdmChangeToPRDict[keySdmName]}
				lastPlfInfoInGitDict.pop(keySdmName)
				curPlfInfoInGitDict.pop(keySdmName)
		for keySdmName in lastPlfInfoInGitDict.keys():
			sdmChangeInfoDict[keySdmName] = {'custo':lastPlfInfoInGitDict[keySdmName]['iscusto'],'value':lastPlfInfoInGitDict[keySdmName]['value'], 'desc':lastPlfInfoInGitDict[keySdmName]['desc'], 'action':'Delete', 'pr': [] if not keySdmName in sdmChangeToPRDict.keys() else sdmChangeToPRDict[keySdmName]}
		for keySdmName in curPlfInfoInGitDict.keys():
			sdmChangeInfoDict[keySdmName] = {'custo':curPlfInfoInGitDict[keySdmName]['iscusto'], 'value':curPlfInfoInGitDict[keySdmName]['value'], 'desc':curPlfInfoInGitDict[keySdmName]['desc'], 'action':'Add', 'pr': [] if not keySdmName in sdmChangeToPRDict.keys() else sdmChangeToPRDict[keySdmName]}
		popdir()
		docmd('rm -rf %s' % sdmTempDir)


	def getPlfSdmValDict(self, dom):
		resDict = {}
		simpleList = dom.getElementsByTagName("SIMPLE_VAR")
		for simple in simpleList:
			sdmItemList = simple.getElementsByTagName('SDMID')
			if not sdmItemList[0].childNodes:
				continue
			else:
				sdm = sdmItemList[0].childNodes[0].data
			resDict[str(sdm)] = {}
			valItemList = simple.getElementsByTagName('VALUE')
			if not valItemList[0].childNodes:
				val = ''
			else:
				val = valItemList[0].childNodes[0].data
			resDict[str(sdm)]['val'] = val
			desItemList = simple.getElementsByTagName('DESC')
			if not desItemList[0].childNodes:
				des = ''
			else:
				des = desItemList[0].childNodes[0].data
			resDict[str(sdm)]['des'] = des

			cnameItemList = simple.getElementsByTagName('C_NAME')
			if not cnameItemList[0].childNodes:
				cname = ''
			else:
				cname = cnameItemList[0].childNodes[0].data
			resDict[str(sdm)]['cname']  = cname

			ctypeItemList = simple.getElementsByTagName('C_TYPE')
			if not ctypeItemList[0].childNodes:
				ctype = ''
			else:
				ctype = ctypeItemList[0].childNodes[0].data
			resDict[str(sdm)]['ctype']  = ctype


			arrayItemList = simple.getElementsByTagName('ARRAY')
			if not arrayItemList[0].childNodes:
				array = ''
			else:
				array = arrayItemList[0].childNodes[0].data
			resDict[str(sdm)]['array']  = array


			metaItemList = simple.getElementsByTagName('METATYPE')
			if not metaItemList[0].childNodes:
				meta = ''
			else:
				meta = metaItemList[0].childNodes[0].data
			resDict[str(sdm)]['meta']  = meta


			custoItemList = simple.getElementsByTagName('IS_CUSTO')
			if not custoItemList[0].childNodes:
				custor = ''
			else:
				custor = custoItemList[0].childNodes[0].data
			resDict[str(sdm)]['custor']  = custor
			featureItemList = simple.getElementsByTagName('FEATURE')
			if not featureItemList[0].childNodes:
				feature = ''
			else:
				feature = featureItemList[0].childNodes[0].data
			resDict[str(sdm)]['feature']  = feature
		return resDict
	def addPlfInfoToDict(self, plfFileName, sdmDict):
		if not os.path.isfile(plfFileName):
			return
                #print plfFileName
                
	def getWeblinkPath(self,gitname,gitpath):
		substring = '(.*)/%s(/?$)'%gitname
		print substring
		#match = re.match('(.*)Mms(/?$)',gitpath)
		print "==============================="
		match = re.match(substring,gitpath)
		if match:
			return match.group(1)
		else:
			return ""
		
	def getgitNamefromgitpath(self,gitpath):
		tmpgitName=gitpath.split('/')
		tmpgitName.sort()
		for item in tmpgitName:
			if item == "":
				continue
			else:
				return item
		return ""
		dom = xml.dom.minidom.parse(plfFileName)
		simpleList = dom.getElementsByTagName("SIMPLE_VAR")
		for simple in simpleList:
			sdm = simple.getElementsByTagName('SDMID')[0].childNodes[0].data if simple.getElementsByTagName('SDMID')[0].childNodes else ''
			val = simple.getElementsByTagName('VALUE')[0].childNodes[0].data if simple.getElementsByTagName('VALUE')[0].childNodes else ''
			desc = simple.getElementsByTagName('DESC')[0].childNodes[0].data if simple.getElementsByTagName('DESC')[0].childNodes else ''
			cname = simple.getElementsByTagName('C_NAME')[0].childNodes[0].data if simple.getElementsByTagName('C_NAME')[0].childNodes else ''
			ctype = simple.getElementsByTagName('C_TYPE')[0].childNodes[0].data if simple.getElementsByTagName('C_TYPE')[0].childNodes else ''
			array = simple.getElementsByTagName('ARRAY')[0].childNodes[0].data if simple.getElementsByTagName('ARRAY')[0].childNodes else ''
			metatype = simple.getElementsByTagName('METATYPE')[0].childNodes[0].data if simple.getElementsByTagName('METATYPE')[0].childNodes else ''
			iscusto = simple.getElementsByTagName('IS_CUSTO')[0].childNodes[0].data if simple.getElementsByTagName('IS_CUSTO')[0].childNodes else ''
			if simple.getElementsByTagName('FEATURE'):
				feture = simple.getElementsByTagName('FEATURE')[0].childNodes[0].data if simple.getElementsByTagName('FEATURE')[0].childNodes else ''
			else:
				feture = ''
			
			if 'last' in plfFileName:
				lastfullname = plfFileName.split('last/')[1]+'/'+str(sdm) 
				fullname = lastfullname
			elif 'cur' in plfFileName:
				curfullname = plfFileName.split('cur/')[1]+'/'+str(sdm)
				fullname = curfullname
			else:
				fullname = ''
			if fullname not in sdmDict.keys():
				sdmDict[fullname] = {'value': val, 'desc': desc, 'cname':cname, 'ctype':ctype, 'array':array, 'metatype':metatype, 'iscusto':iscusto, 'feture':feture}

	def getRelatedChangelist(self, apkname,related_apk_name, changenub):
		html = '<br />'
		changenub = changenub + 1
		html += '%d) %s<br />' % (changenub, related_apk_name) 
		currentVersion = self.gitNameVersion[apkname][0]
		lastVersion = self.gitNameVersion[apkname][1]
		tagcurversion = ("INT-" + "%s" + "-%s" + "-RELEASE") % (related_apk_name,currentVersion)
		taglastversion = ("INT-" + "%s" + "-%s" + "-RELEASE") % (related_apk_name,lastVersion)
		print "tagcurversion is %s" % tagcurversion
		print "taglastversion is %s" % taglastversion
		revListStr = commands.getoutput('git rev-list %s..%s' % (taglastversion, tagcurversion)).strip()

		reviewChangesDict = {}
		reviewChangesDict = self.getReviewDict()
		for commit in revListStr.split('\n'):
			if apkname in self.AlmCheckDict.keys() and 'apkGitWebLink' in self.AlmCheckDict[apkname].keys():
				gitLink = self.AlmCheckDict[apkname]['apkGitWebLink']
				if gitLink:
					commitUrl = '%s%s' % (gitLink, commit)
				else:
					commitUrl = 'http://10.92.32.10/sdd1/gitweb-genericapp/?p=%s.git;a=commit;h=%s' % (apkname, commit)
			else:
				commitUrl = 'http://10.92.32.10/sdd1/gitweb-genericapp/?p=%s.git;a=commit;h=%s' % (apkname, commit)
			if commit not in self.relatedApkUrlDict.keys():
				self.relatedApkUrlDict[commit] = {}
			self.relatedApkUrlDict[commit]['url'] = commitUrl
			tagListStr = commands.getoutput('git show-ref --dereference --tags').strip()
			tagName = ''
			firstComment = ''
			authorStr = ''
			dateStr = ''
			bugNumber = ''
			goodComment = ''
			tagInDescStr = ''
			for line in tagListStr.split('\n'):				
				match = re.match('^([0-9a-f]{40})\s+refs/tags/([^^]+)', line.strip())
				if match:
					if match.group(1) == commit:
						tagName = match.group(2).strip()
						tagInDescStr = '&nbsp;(' + tagName + ')'
				self.relatedApkUrlDict[commit]['tagName'] = tagInDescStr
				self.relatedApkUrlDict[commit]['tag'] = tagName
						
			gitLog = commands.getoutput('git log -n1 --raw %s' % commit.strip())
			for line in gitLog.split('\n'):
				match = re.match('^\s\s\s\s(.*)', line)
				if match:					
					firstComment = match.group(1)				
				match = re.search('###%%%comment:(.+)', line)
				if match:
					goodComment = match.group(1).strip()
					if goodComment.__contains__("###%%%"):
						goodComment = (goodComment.split('###%%%')[0]).strip()
				match = re.match('^Author:\s(.+)', line)
				if match:
					authorStr = match.group(1).strip()
				self.relatedApkUrlDict[commit]['author'] = authorStr

				match = re.match('^Date:\s(.+)', line)
				if match:
					dateStr = match.group(1).strip()
				self.relatedApkUrlDict[commit]['date'] =dateStr

				match = re.search('###%%%bug\snumber:(.+)', line)
				if match:
					bugNumber = match.group(1).strip()
					if bugNumber.__contains__("###%%%"):
						bugNumber = (bugNumber.split('###%%%')[0]).strip()
				if bugNumber and goodComment:
					commitDesc = 'Fix PR %s: %s' % (bugNumber, goodComment.decode('utf-8'))					
				elif (not goodComment):
					commitDesc = firstComment
				else:
					commitDesc = goodComment
				self.relatedApkUrlDict[commit]['commit'] = commitDesc
				self.relatedApkUrlDict[commit]['bugNumber'] =bugNumber
				self.relatedApkUrlDict[commit]['project'] =apkname

			if commit in reviewChangesDict.keys():
				reviewUrl = 'http://10.92.32.10:8081/#change,%s' % reviewChangesDict[commit]
				reviewHtmlCont = '&nbsp;[<a href="%s">review</a>]' % reviewUrl
			else:
				reviewUrl = ''	
				reviewHtmlCont = ''
			self.relatedApkUrlDict[commit]['reviewUrl'] = reviewHtmlCont
			html += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="%s">%s</a>%s%s------%s<br />' % (self.relatedApkUrlDict[commit]['url'], self.relatedApkUrlDict[commit]['commit'], self.relatedApkUrlDict[commit]['reviewUrl'], self.relatedApkUrlDict[commit]['tagName'],self.relatedApkUrlDict[commit]['author'])
		return html

	def getReviewDict(self):
		reviewChangesDict = {}					
		self.defRemote = "origin"
		if self.defRemote: ### if git is remote
			for changeLine in commands.getoutput('git ls-remote %s refs/changes/*' % self.defRemote).split('\n'):
				match = re.search('([0-9a-f]{40})\s+refs/changes/\d+/(\d+)/\d+', changeLine)
				if match:
					reviewChangesDict[match.group(1)] = match.group(2)
		return reviewChangesDict
		
	def getgitwebLink(self,gitname,weblinklist):
		for item in weblinklist:
			if gitname == item[0]:
				return item[1]
			
		return ""	
				 

	def adjustVersionCommint(self, commit):
		self.changeApkAndSmdInfoList=[]
		gitLog = commands.getoutput('git log -n1 --raw %s' % commit.strip())
		for line in gitLog.split('\n'):
			match = re.match('(.*) update NameVersion(.*)int-tools(.*)', line)
			if match:
				return True
		return False			
