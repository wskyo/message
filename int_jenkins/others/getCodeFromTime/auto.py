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

from Config import *

#python auto.py  -codedir /local/build/lyf/twin -codedate 2014-02-28 -manifestbranch twin2.8-v1.0-dint -manifestfilenames twin2.8-v1.0-dint.xml -version 2C13-2-EU -newcodedir /local/build/lyf -manifestgit git@10.92.32.10:sdd1/manifest

def getVersion():
	return conf.getConf('version', 'Version number {([0-9A-Z]{3}|[0-9A-Z]{3}-[1-9A-Z])$}')

def getInputManifestFiles():
		return re.split('\s*,\s*', conf.getConf('manifestfilenames', 'manifest file names'))

def docmd(dir):
        os.system(dir)

conf = Config();
conf.addFromArg(sys.argv[1:])
#version = getVersion()

#xmlname='%s.xml' % version

codeDir = conf.getConf('codedir', 'Project dir for you local computer')
newcodesubdir = conf.getConf('newcodedir', 'new code you want to download','/local/build')

#will get before this date commit
codeDate = conf.getConf('codedate', 'date, that you want to get the commit befor this date ')

version=codeDate.replace(' ','-')
version=version.replace(':','-')
xmlname='%s.xml' % version

workDir = os.getcwd()
if os.path.exists('%s' % version):
	docmd('rm -rfI %s' %version)
	docmd('mkdir %s' %version)
else:
        docmd('mkdir %s' %version)

newcodedir = ('%s/%s' % (newcodesubdir,version) )
if os.path.exists('%s' % newcodedir):
	docmd('rm -rfI %s' %newcodedir)
	docmd('mkdir %s' %newcodedir)
else:
	docmd('mkdir %s' %newcodedir)


#versionGit = 'git@10.92.32.10:sdd1/alps/version_babyd'#conf.getConf('versiongit', 'Url address for version git')
#os.chdir(workDir)
#docmd('rm -rf %s/version_babyd' % workDir)
#docmd('git clone %s' % versionGit)

manifestGit =conf.getConf('manifestgit', 'Url address for manifest file git')
#manifestBranch =conf.getConf('manifestbranch', 'Branch for manifest file git', 'master')
### clone manifest
#os.chdir('%s' % workDir)
#docmd('rm -rf %s/manifest' % workDir)
#docmd('git clone %s' % manifestGit)

manifestMethod ='remote' #conf.getConf('menifestmethod', 'Method to crease manifest file <local|remote>', 'remote')

os.chdir('%s' % codeDir)
print codeDir
#docmd('repo sync -c --no-tag')

destDom = xml.dom.minidom.Document()
manifestNode = destDom.createElement('manifest')
destDom.appendChild(manifestNode)

manifestRemoteDict = {}
manifestDefaultDict = {}
manifestVersionPath = ''
copyVersionList = []


manifestxmlname = getInputManifestFiles()
print "manifestxmlname",manifestxmlname

for oneManifest in manifestxmlname:#get twin2.8-v1.0-dint.xml
        dom = xml.dom.minidom.parse('%s/.repo/manifests/%s' % (codeDir, oneManifest))#open defaule xml
       
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
		#if projName == versionGit.split(':')[1]:#git@10.92.32.10:sdd1/alps/version_babyd
		#	if not manifestVersionPath:
		#		manifestVersionPath = projPath #version_yarism
		#	else:
		#		if manifestVersionPath != projPath:
		#			print "Error: version path mismatch in manifest files"
		#			sys.exit(1)
		#	copyFileList = proj.getElementsByTagName('copyfile')
		#	for oneCopyFile in copyFileList:
		#		tmpCopyFileDict = {}
		#		tmpCopyFileDict['dest'] = oneCopyFile.getAttribute('dest')
		#		tmpCopyFileDict['src'] = oneCopyFile.getAttribute('src')
		#		copyVersionList.append(tmpCopyFileDict)
		#	continue
				
		os.chdir('%s/%s' % (codeDir,projPath))
		resHeadList = commands.getstatusoutput('git log -1 --before="%(codeDate)" --pretty=format:"%H %ad" ')
		if resHeadList[0] >> 8 != 0:
			print 'Error getting head ref in git %s' % projPath
			sys.exit(1)

                match = re.match('([0-9a-fA-F]{40})\s+', resHeadList[1])
		if match:
		        headRef = match.group(0)  #-----------get specia commid
			headRef = headRef.split()
                if not headRef:
			print 'Error getting head ref in git %s' % projPath
			sys.exit(1)

		print '%s ==> %s' % (projPath, headRef[0])

	        newNode = destDom.importNode(proj, True)
	        newNode.setAttribute('revision', headRef[0])
	        manifestNode.appendChild(newNode)
                print "success !!"

#versionNode = destDom.createElement('project')
#versionNode.setAttribute('name', versionGit.split(':')[1])
#versionNode.setAttribute('path', manifestVersionPath)
#versionNode.setAttribute('revision', 'twin2.8-v1.0-dint')
#for oneCopyVersion in copyVersionList:
#	copyVersionNode = destDom.createElement('copyfile')
#	copyVersionNode.setAttribute('dest', oneCopyVersion['dest'])
#	copyVersionNode.setAttribute('src', oneCopyVersion['src'])
#	versionNode.appendChild(copyVersionNode)
#manifestNode.appendChild(versionNode)

os.chdir('%s' % workDir)
if not os.path.exists('%s/xml' % workDir):
	docmd('mkdir %s/xml' % workDir)
fp = file('%s/xml/%s.xml' % (workDir,version), 'w+')
for line in destDom.toprettyxml(indent='  ', newl='\n', encoding='utf-8').split('\n'):
	if line and not re.match('^\s*$', line):
	        fp.write('%s\n' % line)
fp.close()


os.chdir('%s' % newcodedir)
manifestBranch=manifestxmlname[0].split('.xml')[0]
docmd('repo init -u %s -m %s --reference=/automount/repo_mirror/mirror' % (manifestGit,oneManifest) )# oneManifest
docmd('cp %s/xml/%s %s/.repo/manifests/%s.xml' %(workDir,xmlname,newcodedir,manifestBranch))
docmd('repo init -m %s.xml ' % manifestBranch)
docmd('repo sync -c --no-tag')







