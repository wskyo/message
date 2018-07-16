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
from MailUtils import *
from commands import *
import commands

####################################
# version tool allproject 
# this python will create version and manifest if you chose add version adn manifest
####################################

class AllProject(MailUtils):
	def __init__(self):
		self.conf = Config()
		self.userInfo = UserInfo()
		self.version = ''
		self.base = ''
		self.perso = ''
		self.basePerso = ''
		self.codeDir = ''
		self.workDir = ''
		self.lunch_value = False

	##is application version
	def isBig(self):
		raise "You should implement this method"

	def getVersionBranch(self):
		raise "You should implement this method"

	def getInputManifestFiles(self):
		raise "You should implement this method"

	def getVersion(self):
		raise "You should implement this method"

	def getBase(self):
		raise "You should implement this method"

	def getPerso(self):
		raise "You should implement this method"

	def calculateBaseVersion(self):
		raise "You should implement this method"

	def getBasePerso(self):
		raise "You should implement this method"

	def calculateNextPerso(self):
		raise "You should implement this method"

	def getVersionTag(self):
		raise "You should implement this method"

	def versionToManifestPath(self, version):
		raise "You should implement this method"

	def purgeCurDir(self):
		for fileName in glob.glob('*') + glob.glob('.*'):
			docmd('rm -rf %s' % fileName)

	def getBaseManifestDict(self, manifestFilePath, versionGit):
		manifestDict = {}
		dom = xml.dom.minidom.parse(manifestFilePath)
		projList = dom.getElementsByTagName('project')
		for proj in projList:
			if proj.getAttribute('name') != versionGit.split(':')[1]:
				manifestDict[proj.getAttribute('name')] = (proj.getAttribute('path'), proj.getAttribute('revision'))
		return manifestDict
	
	###version run from here 
	def run(self):
		conf = Config();
		## get all args from commands
		conf.addFromArg(sys.argv[1:])
		## init conf from xls table and check some message
		self.initConfFromXls(conf)
		addVersion = self.conf.getConf('addver', 'Add version info <yes|no|force>', 'yes')
		addManifest = self.conf.getConf('addmani', 'Add manifest file <yes|no|force>', 'yes')

		if addVersion == 'no' and addManifest == 'no':
			sys.exit(0)

		self.version = self.getVersion()
		self.codeDir = os.getcwd()
		self.workDir = tempfile.mkdtemp('VersionTool', 'temp', '/tmp')

		versionGit = self.conf.getConf('versiongit', 'Url address for version git')
		### clone version_babdy
		chdir(self.workDir)
		docmd('git clone %s version' % versionGit)

		manifestGit = self.conf.getConf('manifestgit', 'Url address for manifest file git')
		manifestBranch = self.conf.getConf('manifestbranch', 'Branch for manifest file git', 'master')
		### clone manifest
		chdir('%s' % self.workDir)
		docmd('git clone %s manifest' % manifestGit)

		isNeedCheckPersoIncompatible = False
		isPersoIncompatible = False
		
		if self.isBig():
			tmpPerso = self.getPerso()
			if tmpPerso == 'auto':
				tmpBase = self.getBase()
				if tmpBase == 'auto':
					self.base = self.calculateBaseVersion()
					print 'Base version: %s' % self.base
				else:
					self.base = tmpBase
				baseRevisionDict = self.getBaseManifestDict('%s/manifest/%s' % (self.workDir, self.versionToManifestPath(self.base)), versionGit)
				self.basePerso = self.getBasePerso()
				#sys.exit(1)
				isNeedCheckPersoIncompatible = True
			else:
				self.perso = tmpPerso
		else:
			self.perso = '0'

		if isNeedCheckPersoIncompatible:
			manifestMethod = 'local'
		else:
			manifestMethod = self.conf.getConf('menifestmethod', 'Method to crease manifest file <local|remote>', 'remote')

		destDom = xml.dom.minidom.Document()
		manifestNode = destDom.createElement('manifest')
		destDom.appendChild(manifestNode)

		if manifestMethod == 'local':
			cacheDir = self.conf.getConf('cachedir', 'Cache dir for downrepocode')

		chdir(self.codeDir)

		manifestRemoteDict = {}
		manifestDefaultDict = {}
		manifestVersionPath = ''
		copyVersionList = []

		if manifestMethod == 'local':
			self.purgeCurDir()

		for oneManifest in self.getInputManifestFiles():
			###download manifest
			if manifestMethod == 'local':
				docmd('rm -rf %s/%s' % (self.codeDir, oneManifest.replace('/', '_')))
				docmd('mkdir %s/%s' % (self.codeDir, oneManifest.replace('/', '_')))
				chdir('%s/%s' % (self.codeDir, oneManifest.replace('/', '_')))
				docmd('%s/bin/downrepocode -n -repoaddress %s -manifest %s -cachedir %s' % (getToolPath(), manifestGit, oneManifest, cacheDir))
				dom = xml.dom.minidom.parse('.repo/manifests/%s' % oneManifest)
			else:
				dom = xml.dom.minidom.parse('%s/manifest/%s' % (self.workDir, oneManifest))
			
			##get manifest remote
			remoteList = dom.getElementsByTagName('remote')
			if len(remoteList) == 1:
				remoteNode = remoteList[0]
				if not manifestRemoteDict:
					manifestRemoteDict['fetch'] = remoteNode.getAttribute('fetch')
					manifestRemoteDict['name'] = remoteNode.getAttribute('name')
					manifestRemoteDict['review'] = remoteNode.getAttribute('review')
					newNode = destDom.importNode(remoteNode, True)
					manifestNode.appendChild(newNode)
				else:
					if manifestRemoteDict['fetch'] != remoteNode.getAttribute('fetch') or \
							manifestRemoteDict['name'] != remoteNode.getAttribute('name') or \
							manifestRemoteDict['review'] != remoteNode.getAttribute('review'):
						print "Error: 'remote' mismatch in manifest files"
						sys.exit(1)
			else:
				print "Error: more than one 'remote' in %s" % oneManifest
				sys.exit(1)

			##get manifest default
			defaultList = dom.getElementsByTagName('default')
			if len(remoteList) == 1:
				defaultNode = defaultList[0]
				if not manifestDefaultDict:
					manifestDefaultDict['remote'] = defaultNode.getAttribute('remote')
					curManifestDefaultRevision = defaultNode.getAttribute('revision')
					newNode = destDom.importNode(defaultNode, True)
					newNode.removeAttribute('revision')
					manifestNode.appendChild(newNode)
				else:
					if manifestDefaultDict['remote'] != defaultNode.getAttribute('remote'):
						print "Error: 'default' mismatch in manifest files"
						sys.exit(1)
			else:
				print "Error: more than one 'default' in %s" % oneManifest
				sys.exit(1)

			if manifestMethod == 'local':
				gitServerAlias = defaultNode.getAttribute('remote')

			##get manifest project 
			projList = dom.getElementsByTagName('project')
			for proj in projList:
				projName = proj.getAttribute('name')
				projPath = proj.getAttribute('path')
				projRevision = proj.getAttribute('revision')
				if not projRevision:
					projRevision = curManifestDefaultRevision
				if not projRevision:
					print "Error: no revision in %s" % proj
					sys.exit(1)
				if projName == versionGit.split(':')[1]:
					if not manifestVersionPath:
						manifestVersionPath = projPath
					else:
						if manifestVersionPath != projPath:
							print "Error: version path mismatch in manifest files"
							sys.exit(1)
					copyFileList = proj.getElementsByTagName('copyfile')
					for oneCopyFile in copyFileList:
						tmpCopyFileDict = {}
						tmpCopyFileDict['dest'] = oneCopyFile.getAttribute('dest')
						tmpCopyFileDict['src'] = oneCopyFile.getAttribute('src')
						copyVersionList.append(tmpCopyFileDict)
					continue
				if manifestMethod == 'local':
					chdir('%s/%s/%s' % (self.codeDir, oneManifest.replace('/', '_'), projPath))
					resHeadList = commands.getstatusoutput('git show-ref -s refs/remotes/%s/%s' % (gitServerAlias, projRevision))
					if resHeadList[0] >> 8 != 0:
						print 'Error getting head ref in git %s' % projPath
						sys.exit(1)
					headRef = resHeadList[1]
					resAllTagList = commands.getstatusoutput('git show-ref --dereference --tags')
					if resAllTagList[0] >> 8 != 0:
						print 'Warning: getting tag in git %s fail' % projPath
						#sys.exit(1)
					isTagFound = False
					matchTagList = []
					for line in resAllTagList[1].split('\n'):
						line = line.strip()
						match = re.match('([0-9a-fA-F]{40})\s+(refs/tags/?[^^]+)\^\{\}$', line)
						if match:
							if headRef == match.group(1):
								matchTagList.append(match.group(2))
								isTagFound = True
					if isTagFound:
						resDateTagList = commands.getstatusoutput('git for-each-ref --sort=-creatordate --format="%(refname)" refs/tags')
						if resDateTagList[0] >> 8 != 0:
							print 'Error getting tag as date sequence in git %s' % projPath
							sys.exit(1)
						for line in resDateTagList[1].split('\n'):
							line = line.strip()
							if line in matchTagList:
								headRef = line
								break

					if isNeedCheckPersoIncompatible:
						if projName in baseRevisionDict:
							lastRef = baseRevisionDict[projName][1]
							if headRef != lastRef:
								cmdOutPut = commands.getoutput('git diff --name-only %s %s' % (lastRef, headRef))
								if cmdOutPut:
									changedFileList = cmdOutPut.split('\n')
									docmd('mkdir %s/perso_compare' % self.workDir)
									if docmd_noexit('git archive --prefix=a/ %s %s | tar xf - -C %s/perso_compare' % (lastRef, ' '.join(changedFileList), self.workDir)) != 0:
										docmd('mkdir %s/perso_compare/a' % self.workDir)
									if docmd_noexit('git archive --prefix=b/ %s %s | tar xf - -C %s/perso_compare' % (headRef, ' '.join(changedFileList), self.workDir)) != 0:
										docmd('mkdir %s/perso_compare/b' % self.workDir)
									if checkPersoIncompatible('%s/perso_compare/a' % self.workDir, '%s/perso_compare/b' % self.workDir, projPath):
										isPersoIncompatible = True
									docmd('rm -rf %s/perso_compare' % self.workDir)
							baseRevisionDict.pop(projName)
						else:
							docmd('mkdir %s/perso_compare' % self.workDir)
							docmd('mkdir %s/perso_compare/a' % self.workDir)
							docmd('git archive --prefix=b/ %s | tar xf - -C %s/perso_compare' % (headRef, self.workDir))
							if checkPersoIncompatible('%s/perso_compare/a' % self.workDir, '%s/perso_compare/b' % self.workDir, projPath):
								isPersoIncompatible = True
							docmd('rm -rf %s/perso_compare' % self.workDir)
				else:
					headRef = None
					gitUrl = '%s%s' % (manifestRemoteDict['fetch'], projName)
					remoteRefList = commands.getstatusoutput('git ls-remote %s' % gitUrl)
					if remoteRefList[0] >> 8 != 0:
						print 'Error getting head ref in git %s' % projPath
						sys.exit(1)
					tmpList =  remoteRefList[1].split('\n')
					for oneRef in tmpList:
						match = re.match('([0-9a-fA-F]{40})\s+refs/heads/([^/]+)', oneRef)
						if match:
							if match.group(2) == projRevision:
								headRef = match.group(1)
								break
					if not headRef:
						print 'Error: no branch %s in %s' % (projRevision, gitUrl)
						sys.exit(1)
					for oneRef in tmpList:
						match = re.match('([0-9a-fA-F]{40})\s+(refs/tags/[^^]+)', oneRef)
						if match:
							if match.group(1) == headRef:
								headRef = match.group(2)
								break
					print '%s ==> %s' % (gitUrl, headRef)

				newNode = destDom.importNode(proj, True)
				newNode.setAttribute('revision', headRef)
				manifestNode.appendChild(newNode)

		if isNeedCheckPersoIncompatible:
			if isPersoIncompatible:
				self.perso = self.calculateNextPerso()
			else:
				self.perso = self.basePerso

		if self.conf.getConf('ifpushgitserver', 'Push to git server <yes|no>', 'yes') == 'yes':
			ifPushGitServer = True
		else:
			ifPushGitServer = False


		####git push version 
		if addVersion != 'no':
			chdir('%s/version' % self.workDir)
			#docmd('git pull')
			if self.getVersionBranch() != 'master':
				docmd('git fetch origin %s:%s' % (self.getVersionBranch(), self.getVersionBranch()))
				docmd('git checkout %s' % self.getVersionBranch())
			self.setVersionInfo()
			if addVersion == 'yes':
				docmd('git add .')
				docmd('git commit -am "Release %s"' % self.getVersionTag())
				docmd('git tag %s -am "Release %s"' % (self.getVersionTag(), self.getVersionTag()))
				if ifPushGitServer:
					docmd('git push')
					docmd('git push origin tag %s' % self.getVersionTag())
			if addVersion == 'force':
				docmd('git add .')
				docmd_noexit('git commit -am "Release %s"' % self.getVersionTag())
				docmd_noexit('git tag -d %s' % self.getVersionTag())
				docmd('git tag %s -am "Release %s"' % (self.getVersionTag(), self.getVersionTag()))
				###push version to git 
				if ifPushGitServer:
					docmd_noexit('git push')
					docmd_noexit('git push origin tag %s -f' % self.getVersionTag())

		versionNode = destDom.createElement('project')
		versionNode.setAttribute('name', versionGit.split(':')[1])
		versionNode.setAttribute('path', manifestVersionPath)
		versionNode.setAttribute('revision', 'refs/tags/%s' % self.getVersionTag())
		for oneCopyVersion in copyVersionList:
			copyVersionNode = destDom.createElement('copyfile')
			copyVersionNode.setAttribute('dest', oneCopyVersion['dest'])
			copyVersionNode.setAttribute('src', oneCopyVersion['src'])
			versionNode.appendChild(copyVersionNode)
		manifestNode.appendChild(versionNode)

		##manifest update and push 
		projectName = conf.getConf('releasenoteprojname', 'release note project name')
		branch = conf.getConf('codebranch','codebranch')
		if addManifest != 'no':
			chdir('%s/manifest' % self.workDir)
			docmd('git pull')
			xmlExisting = False
			if addManifest == 'yes':
				if os.path.isfile('%s/manifest/%s' % (self.workDir, self.versionToManifestPath(self.version))):
					print "Error: %s already exists" % self.versionToManifestPath(self.version)
					sys.exit(1)
			if addManifest == 'force':
				if os.path.isfile('%s/manifest/%s' % (self.workDir, self.versionToManifestPath(self.version))):
					xmlExisting =True
				docmd('rm -f %s/manifest/%s' % (self.workDir, self.versionToManifestPath(self.version)))
			checkDir(os.path.dirname(self.versionToManifestPath(self.version)))
			fp = file('%s/manifest/%s' % (self.workDir, self.versionToManifestPath(self.version)), 'w+')
			for line in destDom.toprettyxml(indent='  ', newl='\n', encoding='utf-8').split('\n'):
				if line and not re.match('^\s*$', line):
					fp.write('%s\n' % line)
			fp.close()
			updateInfor = False
			updateResult = commands.getstatusoutput('git diff %s' % self.versionToManifestPath(self.version))
			if updateResult[1] == '':
				updateInfor = False
			else:
				updateInfor = True				
			docmd('git add %s' % self.versionToManifestPath(self.version))
			pathCopyManifestfileTo = self.conf.getConf('cpmanifestfileto', 'Copy manifest file to', 'none')
			if pathCopyManifestfileTo != 'none':
				docmd('cp %s %s' % (self.versionToManifestPath(self.version), pathCopyManifestfileTo))
			docmd_noexit('git commit -m "create %s by int_jenkins versiontool"' % self.versionToManifestPath(self.version))
			##push manifest to git
			if ifPushGitServer:
				docmd_noexit('git push')
				#add for auto email to perso to build perso for appli version.2016-4-7
				if len(self.version) == 4 and self.version[2] < 'N':
					attachDir = '%s/manifest/%s' % (self.workDir, self.versionToManifestPath(self.version))	
					if not xmlExisting or (xmlExisting and updateInfor):
						self.createEmail(conf, projectName, self.version, attachDir, branch,xmlExisting, updateInfor)

		# add for add release infor for weekly report db
		if len(self.version) == 4:
			if "pixi3-5_3g" == projectName:
				if self.version[2] == '6' or self.version[2] == 'T':
                            		projectnameForWr = "Pixi3-5_3G_RPMB"
				else:
					projectnameForWr = projectName
			else:
				projectnameForWr = projectName			
			#docmd_noexit('python /local/int_jenkins/misc/insertReleaseinfoWeeklydb.py %s %s ' % (projectnameForWr,self.version))
			release_type = 'start_build'
			docmd_noexit('python /local/int_jenkins/misc/CreateTaskForRealeaseVersionInPRSM.py "%s" "%s" "%s"' % (branch,self.version,release_type))
					
				#end add

		## exit for test.......
		##sys.exit(1)
		if manifestMethod == 'local':
			chdir(self.codeDir)
			self.purgeCurDir()

        def cleanup(self):
		if self.conf.getConf('cleanuptmpdir', 'Clean up the temp dir <yes|no>', 'yes') == 'yes':
			chdir('/')
			docmd('rm -rf %s' % self.workDir)

