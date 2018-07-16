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
from xlrd import xldate_as_tuple

class CheckWifi:
	def getAffectFileDict(self):
		workbook = xlrd.open_workbook('/local/int_jenkins/superspam/conf/wifi_file_check.xls')
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
        		special_word = mtkSheet.cell(j, 3).value.strip()
        		description = mtkSheet.cell(j, 4).value.strip()
			if keyNumber not in fileNameDict.keys():
				fileNameDict[keyNumber] = {}
			fileNameDict[keyNumber]['filename'] = filename
			fileNameDict[keyNumber]['gitname'] = gitname
			fileNameDict[keyNumber]['special_word'] = special_word
			fileNameDict[keyNumber]['description'] = description
		print fileNameDict
		return fileNameDict

	def getGoogleCheck(self):
		workbook = xlrd.open_workbook('/local/int_jenkins/superspam/conf/google_check.xls')
		mtkSheet = workbook.sheet_by_name('check_list')
		nrows = mtkSheet.nrows
		ncols = mtkSheet.ncols
		filename = ''
		fileNameDict = {}
		for j in xrange(1, nrows):
			apkraw_data = mtkSheet.row_values(j)
        		filename = mtkSheet.cell(j, 0).value
        		project = mtkSheet.cell(j, 1).value.strip()
        		#codeBranchName = mtkSheet.cell(j, 2).value.strip()
        		#version = mtkSheet.cell(j, 3).value.strip()
        		androidSecurityBaseTime = mtkSheet.cell(j, 2).value
			if androidSecurityBaseTime:
				Tuple1 = xldate_as_tuple(androidSecurityBaseTime,0)
				androidSecurityBaseTimeStr = str(Tuple1[0])+'-'+str(Tuple1[1])+'-'+str(Tuple1[2])
			else:
				androidSecurityBaseTimeStr = ''
        		#androidSecurityLastversion = mtkSheet.cell(j, 3).value
			#if androidSecurityLastversion:
				#Tuple2 = xldate_as_tuple(androidSecurityLastversion,0)
				#androidSecurityLastversionStr = str(Tuple2[0])+'-'+str(Tuple2[1])+'-'+str(Tuple2[2])
			#else:
				#androidSecurityLastversionStr = ''
			GMSReleasedLastVersion = mtkSheet.cell(j,3).value.strip()
			GMSReleasedLatestVersion = mtkSheet.cell(j,4).value.strip()
        		#GMSBaseVersion = mtkSheet.cell(j, 7).value.strip()
        		GMSDeadlineBase = mtkSheet.cell(j, 5).value
			if GMSDeadlineBase:
				Tuple3 = xldate_as_tuple(GMSDeadlineBase,0)
				GMSDeadlineBaseStr = str(Tuple3[0])+'-'+str(Tuple3[1])+'-'+str(Tuple3[2])
			else:
				GMSDeadlineBaseStr = ''
        		GoogleCTSlastVersion = mtkSheet.cell(j, 6).value.strip()
        		GoogleCTSTestVersion = mtkSheet.cell(j, 7).value.strip()
        		GoogleCTSNewVersionDeadline = mtkSheet.cell(j, 8).value
			if GoogleCTSNewVersionDeadline and GoogleCTSNewVersionDeadline != 'NA':
				Tuple4 = xldate_as_tuple(GoogleCTSNewVersionDeadline,0)
				GoogleCTSNewVersionDeadlineStr = str(Tuple4[0])+'-'+str(Tuple4[1])+'-'+str(Tuple4[2])
			elif GoogleCTSNewVersionDeadline == 'NA':
				GoogleCTSNewVersionDeadlineStr = 'NA'
			else:
				GoogleCTSNewVersionDeadlineStr = ''
        		GoogleGTSlastVersion = mtkSheet.cell(j, 9).value.strip()
        		GoogleGTSTestVersion = mtkSheet.cell(j, 10).value.strip()
        		GoogleGTSNewVersionDeadlineTuple = mtkSheet.cell(j, 11).value
			if GoogleGTSNewVersionDeadlineTuple and GoogleGTSNewVersionDeadlineTuple!= 'NA':				
				Tuple5 = xldate_as_tuple(GoogleGTSNewVersionDeadlineTuple,0)
				GoogleGTSNewVersionDeadlineStr = str(Tuple5[0])+'-'+str(Tuple5[1])+'-'+str(Tuple5[2])
				#GoogleCTSNewVersionDeadlineStr = str(Tuple4[0])+'-'+str(Tuple4[1])+'-'+str(Tuple4[2])
			elif GoogleGTSNewVersionDeadlineTuple == 'NA':
				GoogleGTSNewVersionDeadlineStr = 'NA'
			else:
				GoogleGTSNewVersionDeadlineStr = ''
			if filename not in fileNameDict.keys():
				fileNameDict[filename] = {}
			fileNameDict[filename]['project'] = project
			#fileNameDict[filename]['codeBranchName'] = codeBranchName
			#fileNameDict[filename]['version'] = version
			fileNameDict[filename]['androidSecurityBaseTime'] = androidSecurityBaseTimeStr
			#fileNameDict[filename]['androidSecurityLastversion'] = androidSecurityLastversionStr
			fileNameDict[filename]['GMSReleasedLastVersion'] = GMSReleasedLastVersion
			fileNameDict[filename]['GMSReleasedLatestVersion'] = GMSReleasedLatestVersion
			#fileNameDict[filename]['GMSBaseVersion'] = GMSBaseVersion
			fileNameDict[filename]['GMSDeadlineBase'] = GMSDeadlineBaseStr
			fileNameDict[filename]['GoogleCTSlastVersion'] = GoogleCTSlastVersion
			fileNameDict[filename]['GoogleCTSTestVersion'] = GoogleCTSTestVersion
			fileNameDict[filename]['GoogleCTSNewVersionDeadline'] = GoogleCTSNewVersionDeadlineStr
			fileNameDict[filename]['GoogleGTSlastVersion'] = GoogleGTSlastVersion
			fileNameDict[filename]['GoogleGTSTestVersion'] = GoogleGTSTestVersion
			fileNameDict[filename]['GoogleGTSNewVersionDeadline'] = GoogleGTSNewVersionDeadlineStr
		print fileNameDict		
		return fileNameDict


	def getItemInfo(self,project):
		googleSecuPatchLevel = ''
		GMSVersionReleased = ''
		GMSDeadline = ''
		GoogleCTSVersion = ''
		GoogleCTSNewVersionDeadline = ''
		GoogleGTSVersion = ''
		GoogleGTSNewVersionDeadline = ''
		googlecheckDict = self.getGoogleCheck()
		checkList = []
		for item in googlecheckDict.keys():
			if project == googlecheckDict[item]['project']:
				googleSecuPatchLevel = googlecheckDict[item]['androidSecurityBaseTime']
				GMSlastVersionReleased = googlecheckDict[item]['GMSReleasedLastVersion']
				GMSVersionReleased = googlecheckDict[item]['GMSReleasedLatestVersion']
				GMSDeadline = googlecheckDict[item]['GMSDeadlineBase']
				GoogleCTSlastVersion = googlecheckDict[item]['GoogleCTSlastVersion']
				GoogleCTSVersion = googlecheckDict[item]['GoogleCTSTestVersion']
				GoogleCTSNewVersionDeadline = googlecheckDict[item]['GoogleCTSNewVersionDeadline']
				GoogleGTSlastVersion = googlecheckDict[item]['GoogleGTSlastVersion']
				GoogleGTSVersion = googlecheckDict[item]['GoogleGTSTestVersion']
				GoogleGTSNewVersionDeadline = googlecheckDict[item]['GoogleGTSNewVersionDeadline']
		checkList = [googleSecuPatchLevel,GMSVersionReleased,GMSDeadline,GoogleCTSVersion,GoogleCTSNewVersionDeadline,GoogleGTSVersion,GoogleGTSNewVersionDeadline,GMSlastVersionReleased,GoogleCTSlastVersion,GoogleGTSlastVersion]
		
		return checkList


	def getPlatformSecurityPathchValue(self, codeDir):
		buildDir = codeDir + '/build'
		os.chdir(buildDir)
		PlatformSecurityPathchValue = 'No_value'
		result = commands.getstatusoutput('grep "PLATFORM_SECURITY_PATCH :=" core/version_defaults.mk')
		if result[0] == 0:
			PlatformSecurityPathchValue = result[1].split(':=')[1].strip()
		return PlatformSecurityPathchValue


	def getGmsValue(self, codeDir):
		buildDir = codeDir + '/vendor'
		os.chdir(buildDir)
		GmsValue = 'No_value'
		result = commands.getstatusoutput('grep "ro.com.google.gmsversion=" google/products/gms.mk')
                resultN = commands.getstatusoutput('grep "ro.com.google.gmsversion=" partner_gms/products/gms.mk')
		if result[0] == 0:
			GmsValue = result[1].split('=')[1].strip()
                elif resultN[0] == 0:
                        GmsValue = resultN[1].split('=')[1].strip()
		return GmsValue
	def compare_time_for_email(self,start_t,end_t):
		s_time = time.mktime(time.strptime(start_t,'%Y-%m-%d'))
		e_time = time.mktime(time.strptime(end_t,'%Y-%m-%d'))		
		if (float(s_time) <= float(e_time)):
			return True
		return False
