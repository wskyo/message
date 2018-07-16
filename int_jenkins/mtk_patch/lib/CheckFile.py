#!/usr/bin/python

############################################################################
## check the files that will affect wifi whether have been changed.
## add by renzhi.yang for superspam create 2016-4-20
###########################################################################
import os
import sys
import re
import datetime
import tempfile
sys.path.append('/local/int_jenkins/lib')
from pyExcelerator import *
import os.path
import xlrd
from commands import *
import commands
from Utils import *
from Config import *

class CheckFile:
	def getAffectFileDict(self):
		workbook = xlrd.open_workbook('/local/int_jenkins/mtk_patch/conf/file_check.xls')
		mtkSheet = workbook.sheet_by_name('file_list')
		nrows = mtkSheet.nrows
		ncols = mtkSheet.ncols
		#keyNumber = ''
		fileNameDict = {}
		for j in xrange(1, nrows):
			apkraw_data = mtkSheet.row_values(j)
			keyNumber = str(mtkSheet.cell(j, 0).value).strip()
        		filename = mtkSheet.cell(j, 1).value.strip()
        		gitname = mtkSheet.cell(j, 2).value.strip()
			if keyNumber not in fileNameDict.keys():
				fileNameDict[keyNumber] = {}
			fileNameDict[keyNumber]['filename'] = filename
			fileNameDict[keyNumber]['gitname'] = gitname
		print fileNameDict
		return fileNameDict

	def getFileLibNvram(self, vendorDir,filename):		
		os.chdir(vendorDir)	
		gitLog = getoutput('git log -n1 --raw')
		#print "gitLog is %s" % gitLog
		for line in gitLog.split('\n'):
			match = re.match(':(\w{6})\s(\w{6})\s(\w{7})\.\.\.\s(\w{7})\.\.\.\s([AMD])\s+(.+)', line)
			if match:
				if match.group(5) == 'M':
					tmpActStr = 'Update'
				if match.group(5) == 'A':
					tmpActStr = 'Add'
				if match.group(5) == 'D':
					tmpActStr = 'Delete'
				if filename in match.group(6):
					if filename == 'libnvram.so':
						print "libnvram.so has been changed"
						return 'sochanged'
					else:
						print "%s has been changed" % filename
						return True
		return False

	def checkProjectName(self):
		projectList = []
		conf = "/local/int_jenkins/mtk_patch/conf/mtkProjectName.txt"
		F = open(conf,'r')
		for line in F:
			line = line.strip()
			if line not in projectList:
				projectList.append(line)
		return projectList



    	def getDescriptionFromPatchListFile(self, codedir, untardir,eserviceID):
        	os.chdir(untardir)
        	patchlistFilename = commands.getstatusoutput('ls | grep *.txt')	
		match_start = False
		match_end = False
		description = ''
		match_for_D = ''
		description_start = False
        	if patchlistFilename[0] == 0:
            		gitconf = untardir + "/" + patchlistFilename[1]
            		f = open(gitconf,'r')	
           		os.chdir(codedir)
            		for line in f:
            			match = re.search(eserviceID,line)		
            			if match:
					match_start = True
					continue
				if match_start:
					match_for_D = re.search("^Description:",line)					
					if match_for_D:
						description_start = True
						continue
				match_for_A = re.search('Associated Files:',line)
				if match_for_A:
					match_end = True
				if match_start and description_start and not match_end:
					description = description + line

				if match_end:
					break
		description = description.strip()
		description = description.replace('\'','"')
        	print "The description of %s is %s" % (eserviceID,description)
		os.system('rm -rf %s' % untardir)	
        	return description	

    	def checkBuildCore(self,buildDir):
        	os.chdir('%s' % buildDir)
        	filename = 'core/version_defaults.mk'
        	gitLog = getoutput('git log -n4 --raw')
        	plat_security_value = ''
        	print "gitLog is %s" % gitLog
        	for line in gitLog.split('\n'):
			match = re.match(':(\w{6})\s(\w{6})\s(\w{7})\.\.\.\s(\w{7})\.\.\.\s([AMD])\s+(.+)', line)
			if match:
				if filename in match.group(6):
					plat_security = commands.getstatusoutput('grep "PLATFORM_SECURITY_PATCH :=" core/version_defaults.mk')
					if plat_security[0] == 0:
						plat_security_value = plat_security[1]
        	return plat_security_value



		
