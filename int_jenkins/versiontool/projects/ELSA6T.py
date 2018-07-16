#!/usr/bin/python

import os
import sys
import re
import glob
import commands
from Utils import *
from UserInfo import *
from Config import *
from AllProject import *

class project(AllProject):
	def __init__(self):
		AllProject.__init__(self)

	def initConfFromXls(self, conf):
		print "init conf from xls"
		versionStr = conf.getConf('version', 'Version number {([0-9A-Z]{3,4}|[0-9A-Z]{3,4}-[0-9A-Z]{1}-[A-Z]{2})$}')
		self.ProjectConfig = commands.getoutput('/local/int_jenkins/bin/MT6750_X_GetVerInfo '+ versionStr[0:3]+'X -All').split('\n')
		if len(self.ProjectConfig)>22:
			self.lunch_value = True
		argvList = []
		argvList.extend(['-officelist', self.ProjectConfig[4].strip()])
		argvList.extend(['-manifestprefix', 'int/%s/'%self.ProjectConfig[1].strip().lower()])
		argvList.extend(['-releasenoteprojname', self.ProjectConfig[1].strip()])
		argvList.extend(['-codebranch',self.ProjectConfig[2].strip()])
		argvList.extend(['-Spmlist',self.ProjectConfig[21].strip()])
		argvList.extend(['-UserLaunch',self.ProjectConfig[22].strip()])
		argvList.extend(['-EngLaunch',self.ProjectConfig[23].strip()])
		argvList.extend(['-Variant',self.ProjectConfig[24].strip()])
		argvList.extend(['-perso','<xiaoling.luo@tcl.com>'])
		conf.addFromArg(argvList)
		print conf.dumpConfPretty()

	def isBig(self):
		return len(self.version) == 3

	def getVersionBranch(self):
		return self.conf.getConf('versionbranch', 'branch in manifest git to use')

        def getInputManifestFiles(self):
		return re.split('\s*,\s*', self.conf.getConf('manifestfilenames', 'manifest file names'))

	def getVersion(self):
		return self.conf.getConf('version', 'Version number {([0-9A-Z]{3}|[0-9A-Z]{3}-[1-9A-Z])$}')

	def getBase(self):
		return self.conf.getConf('base', 'Version number {([0-9A-Z]{3}|auto)$}', 'auto')

	def calculateBaseVersion(self):
		versionSequence = self.conf.getConf('versionseq', 'Version number sequence')
		return '%s%s' % (self.version[:2], versionSequence[versionSequence.index(self.version[2])-1])

	def getPerso(self):
		return self.conf.getConf('perso', 'Perso number {([0-9A-Z]|auto)$}', 'auto')

	def getBasePerso(self):
		pushdir('%s/version' % self.workDir)
		match = re.match('\w+\s+blob\s+([0-9a-fA-F]{40})', commands.getoutput('git ls-tree BRANDY-V%s version.inc' % self.base).strip())
		if match:
			commit = match.group(1)
		else:
			print 'Error: Can not get perso from version'
			sys.exit(1)
		for line in commands.getoutput('git cat-file blob %s' % commit).split('\n'):
			line = line.strip()
			match = re.search('PY[0-9A-Z]{4}([0-9A-Z])[0-9A-Z]', line)
			if match:
				persoNum = match.group(1)
				break
		popdir()
		return persoNum

	def calculateNextPerso(self):
		persoSequence = self.conf.getConf('persoseq', 'Perso number sequence')
		return persoSequence[persoSequence.index(self.basePerso)+1]

	def getVersionTag(self):
		versionPrefix = self.conf.getConf('versionprefix', 'string added before version tag')
		return '%s%s' % (versionPrefix, self.version)

	def setVersionInfo(self):
		tempVersionIncFile = self.conf.getConf('inputversionincfile', 'location of input version inc file')
		docmd('cp %s %s/version/version.inc' % (tempVersionIncFile, self.workDir))

	def versionToManifestPath(self, version):
		manifestFilePath = self.conf.getConf('manifestfilepath', 'path of manifestfest file in manifest file git')
		return '%s/v%s.xml' % (manifestFilePath, version)

	def getProjectName(self):
		manifestFilePath = self.conf.getConf('manifestfilepath', 'path of manifestfest file in manifest file git')
		intProjectSplitList = manifestFilePath.split('/')
		return intProjectSplitList[1]
