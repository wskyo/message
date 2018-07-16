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
import xml.dom.minidom
import datetime
from Utils import *
from Config import *
from UserInfo import *
import glob
from ReleaseStyle import *
from pyExcelerator import *


class ChangeUtils(ReleaseStyle):
	gitComment = []
	curDict = {}
	lastDict = {}
        dirverPRDict = {}
	isMergeCommit = False
	nChanged = 0
	nCommit = 0 
	defRemote = None
	dateStr = ''
	DirverList = ''
	tempdir = ''
	authorStr = ''
	maxColumn = 5
	curRow = 4

	def createReleaseNote(self, conf=None):
		workbook = Workbook()
		worksheet = workbook.add_sheet(conf.getConf('version', 'project current version'))
		if conf != None:
			### step 1, create xls title
			self.createXlsTitle(conf, worksheet)
			### get current version manifest create time and lase versin manifest creaete time
			#curVerTimeStr,lastVerTimeStr = self.getCurrAndLaseTime(conf)
			### step 2 create PR SW and RESOLVED PR list
			self.createReleaseNotePRCode(worksheet)
		##return worksheet
		else:
			print "conf is None will exit(0)!"
			sys.exit(0)
		#workbook.save('%s/attach/Mini_ReleaseNote_%s_SW%s.xls' % (self.tempdir, conf.getConf('prlistprojname', 'Project name in PR List file name'), conf.getConf('version','current version')))
		workbook.save('%s/attach/MiniSW_ReleaseNote_%s_%s.xls' % (self.tempdir, conf.getConf('prlistprojname', 'Project name in PR List file name'), conf.getConf('version', 'project current version')))
                docmd('cp %s/attach/MiniSW_ReleaseNote_%s_%s.xls /tmp/' % (self.tempdir, conf.getConf('prlistprojname', 'Project name in PR List file name'), conf.getConf('version', 'project current version')))

	## create xls title
	def createXlsTitle(self, conf, worksheet):
		version = conf.getConf('version', 'project current version')
		fullName = conf.getConf('fullname', 'full name')
		baseVersion = conf.getConf('baseversion', 'project base version')
		worksheet.write_merge(0, 0, 0, self.maxColumn, 'MINI RELEASE NOTES' , self.getReleaseNoteTitleStyle(17))
		worksheet.write_merge(1, 2, 0, 1, 'PROJECT-NAME:' , self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(1, 2, 2, 3, conf.getConf('releasenoteprojname', 'Project name in release note'), self.getHeadTitleItemInfoStyle(True, True, True))
		worksheet.write(1, 4, 'RELEASER:', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write(1, 5, fullName, self.getHeadTitleItemInfoStyle())
		worksheet.write(2, 4, 'RELEASE-DATE:', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write(2, 5, datetime.date.today().strftime('%Y-%m-%d'), self.getHeadTitleItemInfoStyle())
		worksheet.write_merge(3, 3, 0, 1, 'MINI-VERSION:' , self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(3, 3, 2, 3, int(version) if version.isdigit() else version, self.getHeadTitleItemInfoStyle(True, True, True))
		worksheet.write(3, 4, 'BASE:', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write(3, 5,int(baseVersion) if baseVersion.isdigit() else baseVersion, self.getHeadTitleItemInfoStyle())
		worksheet.write_merge(4, 4, 0, 1, 'NOTE:', self.getHeadTitleItemInfoStyle(bold=True))
		worksheet.write_merge(4, 4, 2, self.maxColumn, '', self.getHeadTitleItemInfoStyle())

	## create PR(include release, sw_verifier, deliver PR) code xls
	def createReleaseNotePRCode(self, worksheet):
		styleBodyInfoStyle = self.getBodyInfoStyle()
		styleBodyInfoStyleMan = self.getBodyInfoStyle(20)
		styleBodyTitleStyle = self.getBodyTitleStyle()
		styleReleaseNoteTitleStyle5 = self.getReleaseNoteTitleStyle(5)
		if self.dirverPRDict:
			self.createReleaseMiniList(worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5)
		self.createReleaseWidthXls(worksheet)

	## create dirverDict xls table
	def createReleaseMiniList(self, worksheet, styleBodyTitleStyle, styleBodyInfoStyle, styleReleaseNoteTitleStyle5):
		self.curRow = 5  #must 5,otherwire there are some blank row,
		worksheet.write_merge(self.curRow, self.curRow, 0, self.maxColumn, 'Mini Change LIST', styleReleaseNoteTitleStyle5)
		self.curRow += 1
		worksheet.write(self.curRow, 0, 'NO', styleBodyTitleStyle)
		worksheet.write(self.curRow, 1, 'Content', styleBodyTitleStyle)
		worksheet.write(self.curRow, 2, 'Author', styleBodyTitleStyle)
		worksheet.write(self.curRow, 3, 'Project', styleBodyTitleStyle)
		worksheet.write(self.curRow, 4, 'TAG-Number', styleBodyTitleStyle)
		worksheet.write(self.curRow, 5, 'Date', styleBodyTitleStyle)         
		nCountFixedPR = 0
		for tProject in sorted(self.dirverPRDict.keys()):
			nCountFixedPR += 1
			self.curRow += 1
			worksheet.write(self.curRow, 0, nCountFixedPR, styleBodyInfoStyle)
			worksheet.write(self.curRow, 1, self.dirverPRDict[tProject]['commit'].decode('utf8'), styleBodyInfoStyle)
			worksheet.write(self.curRow, 2, self.dirverPRDict[tProject]['author'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 3, self.dirverPRDict[tProject]['project'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 4, self.dirverPRDict[tProject]['tag'], styleBodyInfoStyle)
			worksheet.write(self.curRow, 5, self.dirverPRDict[tProject]['date'], styleBodyInfoStyle)



	## defination worksheet width
	def createReleaseWidthXls(self, worksheet):
		worksheet.col(0).width = 3000
		worksheet.col(1).width = 13000
		worksheet.col(2).width = 5000
		worksheet.col(3).width = 8000
		worksheet.col(4).width = 9000
		worksheet.col(5).width = 8000
		worksheet.col(6).width = 6800
		worksheet.col(7).width = 6800
		worksheet.col(8).width = 5000
		worksheet.col(9).width = 5000
		worksheet.col(10).width = 5000
		worksheet.col(11).width = 5000
		worksheet.col(12).width = 6800
		worksheet.set_normal_magn(90)

	#### get changelite from this method
	def getChangeList(self, conf):

		html = ''
		html += '<p>Mini Change List:</p>'
		html += '<p>'

		self.DirverList = conf.getConf('dirverlist', 'dirverlist mail')
                #print self.dirverlist 
		self.tempdir = conf.getConf('tempdir','tmp path')
		self.initGitDic(conf)
		html += self.getChangeMessage(conf)
                self.createReleaseNote(conf)
		


		popdir()
		## must check before build code 
		if self.nChanged == 0 and conf.getConf('version','curret version') != conf.getConf('baseversion','base version') and conf.getConf('exitnonewchange', 'Exit if no new change from last version <yes|no>', 'yes') == 'yes':
			print '========================================'
			print '!!! NO NEW CHANGE SINCE LAST VERSION !!!'
			print '========================================'

			sys.exit(1)
		return html


	####get manifest version git and revision
	def initGitDic(self, conf):
		maniPrefix = conf.getConf('manifestprefix', 'Prefix dir for manifest files')
		#print "maniPref=" + maniPrefix
		curManifest = conf.getConf('curmanifest', 'Current manifest file', '.repo/manifests/'+maniPrefix+'v'+conf.getConf('version', 'project current version')+'.xml')
		lstmanifest = '.repo/manifests/'+maniPrefix+'v'+conf.getConf('baseversion', 'project base version')+'.xml'
		if (not os.path.isfile(lstmanifest)):
			lstmanifest = '.repo/manifests/'+maniPrefix+'v'+conf.getConf('baseversion', 'project base version')[0:4]+'.xml'
			print 'baseversion is ' + (conf.getConf('baseversion', 'project base version')[0:4])
		lastManifest = conf.getConf('lastmanifest', 'Base manifest file', lstmanifest)
		for line in file(curManifest).readlines():
			match = re.search('<default\s+remote\s*=\s*\"([^\"]+)\"/>', line)
			if match:
				self.defRemote = match.group(1)
		for line in file(curManifest).readlines():
			match = re.search('<project\s+name=\"([^\"]+)\"\s+path=\"([^\"]+)\"\s+revision=\"([^\"]+)\"', line)
			if match:
				self.curDict[match.group(2).strip()] = [match.group(1).strip(), match.group(3).strip()]
		for line in file(lastManifest).readlines():
			match = re.search('<project\s+name=\"([^\"]+)\"\s+path=\"([^\"]+)\"\s+revision=\"([^\"]+)\"', line)
			if match:
				self.lastDict[match.group(2).strip()] = [match.group(1).strip(), match.group(3).strip()]
	
	####get sdm change, apk change, update patch 
	def getChangeMessage(self, conf):
		html = ''
		#print "cur dict"
		#print self.curDict
		for key in sorted(self.curDict.keys()):
			if key in self.lastDict.keys():
				curVal = self.curDict.pop(key)
				lastVal = self.lastDict.pop(key)
				if key[:8] in ['version', 'version-', 'version_']:
					continue
				if os.path.basename(curVal[0])[:8] in ['version', 'version-', 'version_']:
					continue
				if curVal[1] != lastVal[1]:
					pushdir(key) ###cd git path
					revListStr = commands.getoutput('git rev-list %s..%s' % (lastVal[1], curVal[1])).strip()
					tagListStr = commands.getoutput('git show-ref --dereference --tags').strip()
					reviewChangesDict = {} ###user to get remote review change
					if self.defRemote: ### if git is remote
						for changeLine in commands.getoutput('git ls-remote %s refs/changes/*' % self.defRemote).split('\n'):
							match = re.search('([0-9a-f]{40})\s+refs/changes/\d+/(\d+)/\d+', changeLine)
							if match:
								reviewChangesDict[match.group(1)] = match.group(2)
					if revListStr:
						self.nChanged += 1
						#html += '%d) %s<br />' % (self.nChanged, key) ##number and git name
						self.sdmChangedInCommitsBool = False
						for commit in revListStr.split('\n'):
							commit = commit.strip()
							if re.match('^qaep/*',curVal[0]):
								curVal[0]=curVal[0][5:]
							if re.match('^sdd1/*',curVal[0]):
								temcurVal=curVal[0][5:]
								commitUrl = 'http://10.92.32.10/sdd1/gitweb-sdd1-all/?p=%s.git;a=commit;h=%s' % (temcurVal, commit)
							else:
								commitUrl = 'http://10.92.32.10/gitweb.cgi?p=%s.git;a=commit;h=%s' % (curVal[0], commit)  #modify by zhaoshie 20150320
							if commit in reviewChangesDict.keys():
								reviewUrl = 'http://10.92.32.10:8081/#change,%s' % reviewChangesDict[commit]
							else:
								reviewUrl = ''
							if not re.match('[0-9a-f]{40}', commit):
								continue
							firstComment = ''
							##########git dirver method 

							self.getDirverLog(commit, firstComment, curVal, reviewUrl, tagListStr, commitUrl,key)
					popdir()
		return html
	####get DirverCommit        
	def getDirverLog(self,commit, firstComment,curVal, reviewUrl, tagListStr, commitUrl, key):
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
                                #print self.dirverlist
				match = re.match('(.*)\s(<.*>$)',self.authorStr)
				if match:
					if match.group(2) in self.DirverList:
						author = match.group(2)
                                                #print self.dirverlist
                                                #print author
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
			self.dirverPRDict[self.nCommit]['review'] = reviewUrl
			self.dirverPRDict[self.nCommit]['date'] = self.dateStr
			self.dirverPRDict[self.nCommit]['author'] = author
			self.dirverPRDict[self.nCommit]['url'] = commitUrl
			self.dirverPRDict[self.nCommit]['tag'] = tagName
