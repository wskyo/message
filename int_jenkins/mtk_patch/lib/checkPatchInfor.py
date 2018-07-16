#!/usr/bin/python
import re
import sys
#ALPS02749511(For_jhz6580_we_m_alps-mp-m0.mp1-V2.34_P27).tar.gz
#MOLY00184784_ALPS02761783(For_JHZ6580_WE_M_GPRS_HSPA_MOLY.WR8.W1449.MD.WG.MP.V57.P5).tar.gz

class checkPatchInfor:
	def getMtkPatchInfor(self, patchName):
		print "patchName",patchName
		patch_type = ''
		vnum = ''
		pnum = ''
		eservice_ID = ''
		match = re.match("(^MOLY\d+).*(V\d+.?\d+?).(P\d*).*",patchName) or re.match("(^MOLY\d+).*(V\d*).(P\d*).*",patchName)
		print "match1",match
		if match:
			patch_type = 'MOLY'
			vnum = match.group(2)
			pnum = match.group(3)
			eservice_ID = match.group(1)
		
		match = re.match("(^SIXTH\d+).*(V\d+.?\d?).(P\d*).*",patchName) or re.match("(^SIXTH\d+).*(V\d*).(P\d*).*",patchName)
		print "match1",match
		if match:
			patch_type = 'SIXTH'
			vnum = match.group(2)
			pnum = match.group(3)
			eservice_ID = match.group(1)
		
		match = re.match("(^ALPS\d+).*(V\d+.?\d*)_(P?\d*).*",patchName) or re.match("(^ALPS\d+).*(V\d+.\d+.\d*)_(P?\d*).*",patchName) or re.match("(^JRD\d+).*(V\d+.?\d*)_(P?\d*).*",patchName)
		print "match2",match
		if match:
			patch_type = 'ALPS'
			vnum = match.group(2)
			pnum = match.group(3)
			eservice_ID = match.group(1)

		if not (patch_type and vnum and pnum and eservice_ID):
			print 'patch_type',patch_type
			print 'vnum',vnum
			print 'pnum',pnum
			print 'eservice_ID',eservice_ID
			print "It should not be null"
			sys.exit(1)
		else:
			return patch_type,vnum,pnum,eservice_ID

			
				
		
		
		
