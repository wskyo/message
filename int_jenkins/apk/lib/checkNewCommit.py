#!/usr/bin/python
import os
import sys
sys.path.append('/local/int_jenkins/lib')
import re
import datetime
import tempfile
from pyExcelerator import *
import os.path
import xlrd
from commands import *
import commands

def getApkCloneDict():
	workbook = xlrd.open_workbook('/local/int_jenkins/apk/conf/generic_apk.xls')
	mtkSheet = workbook.sheet_by_name('apk_info')
	apk_nrows = mtkSheet.nrows
	apk_ncols = mtkSheet.ncols
	apkname = ''
	ApkCloneDict = {}
	for j in xrange(1, apk_nrows):
		apkraw_data = mtkSheet.row_values(j)
        	apkname = mtkSheet.cell(j, 0).value.strip()
        	apkDowncodeGitDir = mtkSheet.cell(j, 5).value.strip()
        	apkCodeBranch = mtkSheet.cell(j, 6).value.strip()
		apkGitWebLink = mtkSheet.cell(j, 8).value.strip()
		creativeApk = mtkSheet.cell(j, 12).value.strip()
		dependGit = mtkSheet.cell(j, 13).value.strip()
		if apkname not in ApkCloneDict.keys():
			ApkCloneDict[apkname] = {}
		ApkCloneDict[apkname]['apkDowncodeGitDir'] = apkDowncodeGitDir
		ApkCloneDict[apkname]['apkCodeBranch'] = apkCodeBranch
		ApkCloneDict[apkname]['apkGitWebLink'] = apkGitWebLink
		ApkCloneDict[apkname]['creativeApk'] = creativeApk
		ApkCloneDict[apkname]['dependGit'] = dependGit
	print ApkCloneDict
	return ApkCloneDict

def repo_code():
	print "Now update the code to lastest"
	CodeDir = "/local/build/genericapp/"
	ApkCloneDict = {}
	NeedUpdateVersionApkList = []
	ApkCloneDict = getApkCloneDict()
	for apkname in ApkCloneDict.keys():
		EachcodeDir = CodeDir + apkname
		gitClone = ApkCloneDict[apkname]['apkDowncodeGitDir']
		code_branch = ApkCloneDict[apkname]['apkCodeBranch']
		print "Now start to clone or update %s code" % apkname
		if ApkCloneDict[apkname]['creativeApk'] == 'yes':
			continue
		if ApkCloneDict[apkname]['dependGit'] == 'yes':
			continue			
		if os.path.exists(EachcodeDir + "/.git") == False:
			os.chdir(CodeDir)
 			os.system('git clone git@10.92.32.10:%s -b %s %s' % (gitClone, code_branch, apkname))			
   			os.chdir(EachcodeDir)
   			os.system('git checkout %s' % code_branch)
		else:
   			os.chdir(EachcodeDir)
            		os.system('git reset --hard HEAD')
            		os.system('git clean -df')
            		os.system('git pull')
		checkNewCommit(apkname, NeedUpdateVersionApkList)		
	print "The all need build apk"
	print NeedUpdateVersionApkList


def checkNewCommit(apkname,NeedUpdateVersionApkList):
	tagFormat = "INT-%s.*-RELEASE$" % apkname
	tagFormat_else = "INT-%s.*-RELEASE-1.*" % apkname	
	tagMatch = commands.getstatusoutput('git describe')
	print "tagMatch is  "
	print  tagMatch
	if tagMatch[0] == 0:
		match = re.match(tagFormat, tagMatch[1]) or re.match(tagFormat_else, tagMatch[1])
		if match:
			print "There is no new commit after last version"
			print "The apk %s no need to buildnew version" % apkname
		else:
			print "There is new commit after last version" 
			startJenkinsToBuild(apkname)
			if apkname not in NeedUpdateVersionApkList:
				NeedUpdateVersionApkList.append(apkname)

def startJenkinsToBuild(appname):	
	jobname = "JrdAPK-%s-release" % appname
	if appname == "JrdGallery2" or appname == "JrdLauncherM" or appname == "JrdSetupWizard":
		appname_version = "%s_SDD1" % appname
	else:
		appname_version = appname		
	version = commands.getstatusoutput('/local/int_jenkins/misc/getApkNumber.py -appname %s' % appname_version)
	baseversion = commands.getstatusoutput('/local/int_jenkins/misc/getLastApkNumber.py -appname %s' % appname_version)
	addVersion = 'yes'
	if version[0] == 0 and baseversion[0] == 0:
		print "The current version is %s" % version[1]
		print "The base version is %s" % baseversion[1]
		if checkCurrentTag(appname,version[1]):
			addVersion = 'force'		
		buildResult = commands.getstatusoutput('/local/int_jenkins/misc/hudson_start_genericapk_build.pl %s version=%s  addversion=%s baseversion=%s' % (jobname,version[1],addVersion,baseversion[1]))
		if buildResult[0] == 0:
			print "The apk %s version %s build successfully" % (appname, version[1])
		else:
			print "The error info is %s " % buildResult[1]
			#sys.exit(1)

def checkCurrentTag(appname, CurrentVersion):
	apkCodeDir = "/local/build/genericapp/%s" % appname
	os.chdir(apkCodeDir)
	currentTag = "INT-%s-%s-RELEASE" % (appname,CurrentVersion)
	tagCheckResult = commands.getstatusoutput('git tag | grep %s' % currentTag)
	if tagCheckResult[0] == 0 and tagCheckResult[1] == currentTag:
		return True
	else:
		return False
	


if __name__ == "__main__":
	repo_code()
