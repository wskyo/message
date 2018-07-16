#!/usr/bin/python
#coding=utf-8
#for send MTK patch mail
#
import sys
import MySQLdb
sys.path.append('/local/int_jenkins/lib')
sys.path.append('/local/int_jenkins/mtk_patch/lib')
from checkPatchInfor import *
from dotProjectDb import *
from CheckFile import *
import xlrd
from Config import *
import smtplib
from email.header import Header
from email.MIMEText import MIMEText
import time
import re

class patchmail(checkPatchInfor,dotProjectDb,CheckFile):
	
	def __init__(self,conf):
		self.proj = conf.getConf("project","project name")
		self.patchNo = []
		self.str_patchNo = ''
		self.simplex=False
		self.insertDataToPrsm= True
		self.patchtype = conf.getConf("patchtype","List of patch type",['ALPS','MOLY','SIXTH'])
		self.__mailDir = conf.getConf("mailDir","mail dir","/local/mtk_patch_import/Mail")
		self.__ongoingPatch = conf.getConf("ongoingPatch","on going patch","/local/mtk_patch_import/TODO")
		self.sendmail = conf.getConf("sendmail","send mail",True)
		self.patch_type = ''
		self.vnum = ''
		self.pnum = ''
		self.eservice_ID = conf.getConf("eservice_ID","eservice ID",False)
		self.repopath = '/local/tools/repo/repo'
		self.__mailServer = u'mailsz.tct.tcl.com'
		self.__mailSender = u'xiaodan.cheng@tcl.com'
		self.__mailAccount = u'tct-hq\\xiaodan.cheng'
		#self.__mailccList = u'xiaodan.cheng@tcl.com'
		self.__git_remote_name_dict = {}
		self.patchowner = unicode(conf.getConf("patchowner","patch owner"))
		#self.sharefoldname = self.proj
		self.importIdDict = {}
		self.importIdDictSimplex = {}
		for str_type in self.patchtype:
			self.importIdDict[str_type] = {}
			self.importIdDictSimplex[str_type] = {}
		wb = xlrd.open_workbook('/local/int_jenkins/mtk_patch/jb3-mp-import.xls')
		ap_st = wb.sheet_by_name(u'MTKInfo')
		mp_st = wb.sheet_by_name(u'ModemInfo')
		ap_row = ''
		mp_row = ''
		print "project name",self.proj
		for row in xrange(0,ap_st.nrows):
			#print "project of ALPS",self.proj,ap_st.cell(row,0).value.strip()
			if ap_st.cell(row,0).value.strip() == self.proj:
				ap_row = row
		for row in xrange(0,mp_st.nrows):
			#print "project of MOLY",self.proj,mp_st.cell(row,0).value.strip()
			if mp_st.cell(row,0).value.strip() == self.proj:
				mp_row = row
		if not ap_row:
			print "Cannot find project in the ALPS SHEET OF THE Excel!"
			sys.exit(1)
		if not mp_row:
			print "Cannot find project in the MOLY OF THE Excel!"
			sys.exit(1)
		self.__branch = ap_st.cell(ap_row,1).value.strip()
		self.platform = ap_st.cell(ap_row,16).value.strip()
		self.dept = ap_st.cell(ap_row,13).value.strip()
		self.__SPMList = ap_st.cell(ap_row,10).value.strip().split(',')
		
		self.__CodeDir = conf.getConf("CodeDir","code dir","/local/mtk_patch_import/"+self.__branch)
		self.__mtkproj = ['','','']
		self.__mtkrelease = ['','','']
		#ALPS
		self.__mtkproj[0] = ap_st.cell(ap_row,2).value.strip().split(',')[0]
		self.__mtkrelease[0] = ap_st.cell(ap_row,3).value.strip()
		#MOLY
		self.__mtkproj[1] = mp_st.cell(mp_row,2).value.strip()
		self.__mtkrelease[1] = mp_st.cell(mp_row,3).value.strip()
		#SIXTH
		self.__mtkproj[2] = mp_st.cell(mp_row,2).value.strip()
		self.__mtkrelease[2] = mp_st.cell(mp_row,4).value.strip()
		self.__mailToList = ap_st.cell(ap_row,8).value.strip().split(',')
		self.__mailccList = ap_st.cell(ap_row,9).value.strip().split(',')
		self.sharefoldname = ap_st.cell(ap_row,18).value.strip()
		self.lastpatchnum = str(ap_st.cell(row,23).value)[:-2] 
		self.care_git_folder = ap_st.cell(ap_row, 25).value.strip().split(';')
		self.care_files = ap_st.cell(ap_row, 26).value.strip().split(';')
		self.download_type = ap_st.cell(ap_row,27).value.strip()   
		self.mtkrelease = ap_st.cell(ap_row, 28).value.strip() 
		self.mtkversion = ap_st.cell(ap_row, 29).value.strip()
		self.chpbf_gitname_list = ap_st.cell(ap_row, 32).value.strip().split(';')
		self.chpbt_branch_list = ap_st.cell(ap_row, 33).value.strip().split(';')
		self.chplf_gitname_list = ap_st.cell(ap_row, 34).value.strip().split(';')
		self.chplt_gitname_list = ap_st.cell(ap_row, 35).value.strip().split(';')
		print self.chpbf_gitname_list
		print self.chpbt_branch_list
		print self.chplf_gitname_list
		print self.chplt_gitname_list
		self.is_mailed = False
		if not self.sharefoldname:
			self.sharefoldname = self.proj
		for str_type in self.patchtype:
			no = conf.getConf(str_type,"Patch number of %s"%str_type,-1)
			self.patchNo.append(no)
			
		title=''
		for i in xrange(0,len(self.patchtype)):
			if self.patchNo[i] != -1:
				self.str_patchNo = self.str_patchNo + "_%s"%self.patchtype[i]+str(self.patchNo[i])
				title = title + "[%s]["%self.patchtype[i] + self.__mtkproj[i] + "][" + self.__mtkrelease[i] + "][P" + str(self.patchNo[i]) + "]"
		
		self.__mailTitle = '[MTK Patch merge][%s]%s' % (self.proj,title)
		self.__Code = conf.getConf("codeDir","code dir","/local/mtk_patch_import/" + self.__branch)
		self.gitlog_format = '%s forall -c \'git log --format=%s\' | grep "%s" | grep "%s" | grep "P%s_.tar.gz" | sort '
		
		self.get_db_connection()
		self.checkFileDict = self.getAffectFileDict()
		self.projectList = self.checkProjectName()
		self.devCodeProjectIDList = []
		if self.insertDataToPrsm:
			self.devCodeProjectIDList = self.getProjectIDFromImportBranch(self.__branch)
		#for simplex data start
		self.devCodeProjectIDListSimplex = self.getProjectIDFromImportBranchSimplex(self.__branch)
		#for simplex data end
		if self.insertDataToPrsm:
			self.devCodeAllProjectIDList = []
			self.devCodeAllProjectIDList = self.getAllProjectIDFromImportBranch(self.__branch)
		else:
			self.devCodeAllProjectIDListSimplex = []
			self.devCodeAllProjectIDListSimplex = self.getAllProjectIDFromImportBranchFromSimplex(self.__branch)
		print "test devCodeAllProjectIDList,devCodeProjectIDList",self.devCodeAllProjectIDList,self.devCodeProjectIDList
		self.projectid_codeBranch_Dict = {}
		self.projectid_codeBranch_DictSimplex = {}
		self.devCodeBranch = []
		self.devCodeBranchSimplex = []
		if self.insertDataToPrsm:
			self.devCodeBranch = self.getDevBranchNameFromIProjectID(self.devCodeProjectIDList,self.projectid_codeBranch_Dict,self.__branch)
		#for simplex data start
		self.devCodeBranchSimplex = self.getDevBranchNameFromIProjectIDSimplex(self.devCodeProjectIDListSimplex,self.projectid_codeBranch_DictSimplex)
		#for simplex data end
		if self.insertDataToPrsm:
			self.SPMIDList = self.getContactIDList(self.devCodeAllProjectIDList)
		else:
			self.SPMIDList = self.getContactIDList(self.devCodeAllProjectIDListSimplex)
		print "self.SPMIDList",self.SPMIDList,type(self.SPMIDList)
		self.SPMEmailList = self.getSpmEmailList(self.SPMIDList)
		self.__getremotegitname()
		#self.SPMEmailList = '908762503@qq.com'
		#print "SPMEmailList",self.SPMEmailList
		#self.SPMEmailList = ['xiaodan.cheng@tcl.com','908762503@qq.com']
		#self.mtktag = "t-" + self.mtkrelease + "." + str(self.patchNo[0])
		self.mtktag = "t-" + self.mtkrelease + str(self.patchNo[0])
		#self.mtkversionNO = self.mtkversion  + "." + str(self.patchNo[0])
		self.mtkversionNO = self.mtkversion  +  str(self.patchNo[0])
		if not self.dept:
			self.gLink='http://10.92.32.10%s/gitweb-%s/?p=%s.git;a=commit;h=%s'
		else:
			self.gLink='http://10.92.32.10/%s/gitweb-%s/?p=%s.git;a=commit;h=%s'
		print "========start========"
		print "agv:"
		print "project name",self.proj
		print "patchNo",self.patchNo
		print "mtk project",self.__mtkproj
		print "mtk MR release vesion",self.__mtkrelease
		print "patchowner",self.patchowner
		print "SPMEmailList",self.SPMEmailList
		print "mailccList",self.__mailccList
		#print "git_remote_name_dict",self.__git_remote_name_dict
		print "mtk tag ",self.mtktag
		print "========end========"
	def getEmailHead(self,owner,bugInfo,mailBody):
		self.mailBodyHEAD.append('<p align=\'Left\'><b>Dear %s,</b></p>' % owner)
		#mailBody.append('<p align=\'Left\'><font color="#FF0000">请留意邮件下文是否有要求执行modem下的update_modem.py脚本并check是否需要对vendor/mediatek/proprietary/modem发patch</font></p>')
		__bugInfor = ''
		comment = ''
		branch_openst_owner = {}
		branch_mail = []
		alps=bugInfo['ALPS']['mtkdefect']
		sixth=bugInfo['SIXTH']['mtkdefect']
		moly=bugInfo['MOLY']['mtkdefect']	
		for str_type in self.patchtype:
			branch_openst_owner[str_type] = {}
		print "bugInfo",bugInfo
		for str_type in self.patchtype:
			#print "======str_type========",str_type
			
			if bugInfo[str_type].has_key('patchID') and bugInfo[str_type]['patchID'] == str_type:
				__bugInfor = __bugInfor + bugInfo[str_type]['bugID'] + ' '
				comment = comment + bugInfo[str_type]['comment'] + '#'
		
		self.mailBodyHEAD.append('<p align=\'Left\'>%s Platform %s Patch %s <br/></p>' %(self.platform,self.proj,__bugInfor))
		if alps or moly or sixth:
			mailBody.append('<p align=\'Left\'>mtk defect:<a href="https://alm.tclcom.com:7003/im/issues?selection=%s">%s</a> <a href="https://alm.tclcom.com:7003/im/issues?selection=%s">%s</a> <a href="https://alm.tclcom.com:7003/im/issues?selection=%s">%s</a><br/></p>' %(alps,alps,moly,moly,sixth,sixth))		
		for i in xrange(0,len(self.patchtype)):
			if self.patchNo[i] == -1:
				continue
			if int(self.patchNo[i])-1 <= 0:
				continue
			for eachCodeBranchName in self.devCodeBranch:
				owner,status=self.getownerstatus(eachCodeBranchName,str(int(self.patchNo[i])-1),self.patchtype[i])
				print owner,type(owner),status,type(status)
				if status == 0:
					branch_openst_owner[self.patchtype[i]][eachCodeBranchName] = owner
				
		print branch_openst_owner
		self.mailBodyHEAD.append('<p align=\'Left\'><b>Please help to merge patch to below branch(contact with the owner showed below if any about the last patch merging status):</b><br/></p>')
		for eachCodeBranchName in self.devCodeBranch:
			for i in xrange(0,len(self.patchtype)):
				if self.patchNo[i] == -1:
					continue
				if branch_openst_owner[self.patchtype[i]].has_key(eachCodeBranchName):
					tmp = '<p align=\'Left\'><b><font color="#FF0000">%s(Last patch %s P%s;status is </font></b><b><font color=blue>open</font></b><b><font color="#FF0000">;owner is %s.)</font></b></p>' % (eachCodeBranchName,self.patchtype[i],str(int(self.patchNo[i])-1),branch_openst_owner[self.patchtype[i]][eachCodeBranchName])
					if tmp not in branch_mail:
						branch_mail.append(tmp)
					
				else:	
					tmp = '<p align=\'Left\'><b><font color="#FF0000">%s(Last patch %s P%s;status is closed.)</font></b></p>' % (eachCodeBranchName,self.patchtype[i],str(int(self.patchNo[i])-1))
					if tmp not in branch_mail:
						branch_mail.append(tmp)
		for branch_name in branch_mail:
			self.mailBodyHEAD.append(branch_name)
		mailBody.append('<p align=\'Left\'>Please kindly give a feedback in 24h.</b><br/><br/></p>')

		mailBody.append('<p align=\'Left\'>The comment same as:</b><br/></p>' )
		if self.download_type == 'git':
			download_str = 'repo init -u http://git01.mediatek.com/alps_release/platform/manifest -b tcthz -m %s.xml --no-repo-verify && repo sync' % (self.mtktag)	
			mailBody.append('<p align=\'Left\'><font color="#FF0000">    %s</b></font><br/></p>' %download_str)
			mailBody.append('<p align=\'Left\'>Please find all commit from import branch: %s</p>' %self.__branch)
		else:		
			for comment_str in comment.split('#'):
				if comment_str:
					mailBody.append('<p align=\'Left\'>    %s</b><br/></p>' % comment_str)	
			mailBody.append('<p align=\'Left\'>Patch Link in import branch:</p>')

	def getEmailTail(self,mailBody):
		if self.download_type == 'git':
			a = u"\\\\10.92.32.12\\RDhzKM\\5-SWD\\I-Patch\\MTKPatch\\%s\\%s" % (self.sharefoldname,self.mtktag)
			mailBody.append('<p align=\'Left\'><b>You can find this patch%s %s in:<font color="#FF0000">%s</font></b></p>' % (self.str_patchNo.replace('_',' '), self.mtktag,a))
		else:
			a = u"\\\\10.92.32.12\\RDhzKM\\5-SWD\\I-Patch\\MTKPatch\\%s" % self.sharefoldname	
			mailBody.append('<p align=\'Left\'><b>You can also find this patch%s in:<font color="#FF0000">%s</font></b></p>' % (self.str_patchNo.replace('_',' '), a))
		mailBody.append('<p align=\'Left\'><b>After you complete to merge the %s %s patch %s,</b></p>' % (self.platform,self.proj,self.str_patchNo.replace('_',' ')))
		mailBody.append('<p align=\'Left\'><b>please make sure the related issues of this MTK Patch you merged are fixed, and</b></p>')
		mailBody.append('<p align=\'Left\'><font color="#FF0000"><b>please send a remind email to us!!!</b></font></p>')

	def makePatchMail(self):
		mailBody = []
		self.mailBodyHEAD = []
		self.mailBody_remind=[]
		comment_list = []
		file_link = {}
		for str_type in self.patchtype:
			file_link[str_type] = {}
		patchfile_list = []
		self.getCommentLink(comment_list,file_link,patchfile_list)
		if self.download_type != 'git':
			assert len(comment_list) == 3,"========something wrong happened========\n"
			filenum = self.getpatchfilenumbers(patchfile_list)
			if not comment_list[0] and not comment_list[1] and not comment_list[2]:
				print "Parameter patchNo(%s) is error." % self.patchNo
				return
		bugInfo = self.__getBugzillaInfo( comment_list )
		
		dearName = self.patchowner.split('@')[0]
		self.getEmailHead(dearName,bugInfo,mailBody)
		itemnum = self.getEmailContent(mailBody,self.str_patchNo,file_link)
		#assert filenum <= itemnum,"file number must be smaller than item number."
		self.getEmailTail(mailBody)
		mailtitle = '%s Patch merge' %(self.__mailTitle)                           
		#print 'self.importIdDict',self.importIdDict
		#print 'self.projectid_codeBranch_Dict',self.projectid_codeBranch_Dict	
		#for projectID1 in self.importIdDict.keys():
			#for projectID2 in self.projectid_codeBranch_Dict.keys():
				#if projectID1 == projectID2:
					#pass
					#self.insertImportId_And_DevBranch_To_dotp_mtk_merge(self.importIdDict[projectID1],self.projectid_codeBranch_Dict[projectID2],self.patchowner)			             
		#os.system('python /local/int_jenkins/mtk_patch/lib/insertdbToWr.py %s %s %s %s' % (self.__branch,self.vnum,self.pnum,self.eservice_ID) )
		#os.system('python /local/int_jenkins/mtk_patch/lib/insertInforToManpower.py %s %s %s %s %s' % (self.__branch,self.vnum,self.pnum,self.eservice_ID,'yan.xiong') )			             
		mailBody = self.mailBodyHEAD + self.mailBody_remind + mailBody
		self.__sendMail(self.str_patchNo, mailtitle, mailBody, [bugInfo['assigned']])
		for i in xrange(0,len(self.patchtype)):
			if self.patchNo[i]!=-1:
				self.setmailed(self.importIdDict,self.patchNo[i],self.patchtype[i])
	def getpatchfilenumbers(self,patchfile_list=[]):
		file_sum = 0
		file_list = []
		if patchfile_list[0]:
			tmpfiles = getoutput("tar %s/'%s' | sed 's/\// /g' | awk '{print $2}'"%(self.__ongoingPatch,patchfile_list[0])).split('\n')
			for tmpfile in tmpfiles:
				if not tmpfile:
					continue
				if tmpfile not in file_list:
					file_list.append(tmpfile)
			file_sum = file_sum + len(file_list)
		if patchfile_list[1]:
			file_sum = file_sum + 1
		if patchfile_list[2]:
			file_sum = file_sum + 1
		return file_sum

	def getCommentLink(self,comment_list=[],file_link={"ALPS":{},"MOLY":{},"SIXTH":{}},patchfile_list=[]):
		'''parameter patchNo is 0,1,2,3...'''
		numtotype = {}
		for i in xrange(0,len(self.patchtype)):
			numtotype[i] = self.patchtype[i]
		for i in xrange(0,len(self.patchNo)):
			if int(self.patchNo[i]) == -1:
				comment_list.append('')
				patchfile_list.append('')
			    	continue
			if not os.path.isdir(self.__mailDir):
			    	os.system('mkdir -p %s' % self.__mailDir)
			print '========ongoingPatch=%s,mtkproject=%s,mtkrelease=%s,patchNo=%s========' %(self.__ongoingPatch, self.__mtkproj[i],self.__mtkrelease[i], self.patchNo[i])
			if self.download_type == 'git':
                                releasenotetag = self.mtktag
				patchFilename = getoutput("ls %s | grep 'ReleaseNote' | grep '%s' | grep 'xls'" % (self.__ongoingPatch, self.mtkversionNO))
				print '========patchFilename========',patchFilename
				if not os.path.isdir('/local/mtk_patch_import/mtkpatch/%s/%s' %(self.sharefoldname,self.mtktag)):
					os.system('cd /local/mtk_patch_import/mtkpatch/%s; mkdir -p %s' % (self.sharefoldname,self.mtktag))
				for releasefile in patchFilename.split('\n'):
					if not os.path.isfile('/local/mtk_patch_import/mtkpatch/%s/%s/%s'% (self.sharefoldname,self.mtktag,releasefile)):
						print "cp '/local/mtk_patch_import/TODO/%s'  '/local/mtk_patch_import/mtkpatch/%s/%s/'" %(releasefile,self.sharefoldname,self.mtktag)
						print getoutput("cp '/local/mtk_patch_import/TODO/%s'  '/local/mtk_patch_import/mtkpatch/%s/%s/'" %(releasefile,self.sharefoldname,self.mtktag))
				self.patch_type = 'ALPS'
				self.vnum = self.mtkversion
				self.pnum = "P" + self.patchNo[i]
				self.eservice_ID = self.mtktag
				print "========patch_type,vnum,pnum,eservice_ID========\n"
				print self.patch_type,self.vnum,self.pnum,self.eservice_ID
				print "========"
				JRDimportDir = "/local/mtk_patch_import/"+"JRD_"+self.__branch
				print 'change dir ==================>%s\n' % JRDimportDir 
				os.chdir(JRDimportDir)
				
				#begin to get checklist for git
				GetChangeListDir = '/local/tools/GetChangeList'				 
				if not os.path.isdir(GetChangeListDir):
					os.system('cd /local/tools; git clone git@10.92.32.10:tools_int_sdd1/GetChangeList.git')
				else:
					os.system('cd %s; git reset --hard HEAD && git clean -df && git pull' %GetChangeListDir)
				if not os.path.isdir('%s/.repo/manifests/int/%s' %(JRDimportDir,self.proj)):
					os.system('cd .repo/manifests; mkdir -p int/%s' %self.proj)
				os.system('cp .repo/manifests/%s.xml .repo/manifests/int/%s/v%s.xml' %(self.mtktag,self.proj,self.mtktag))
				lastpathtag =  "t-" + self.mtkrelease + "." + str(self.lastpatchnum)
				os.system('cp .repo/manifests/%s.xml .repo/manifests/int/%s/v%s.xml' %(lastpathtag,self.proj,lastpathtag))
				os.chdir(GetChangeListDir)
				print 'python GetChangeList.py -project %s -version %s -baseversion %s -builddir %s -bugzilla no -getfile no -updatecode no' %(self.proj,self.mtktag,lastpathtag,JRDimportDir)
				os.system('python GetChangeList.py -project %s -version %s -baseversion %s -builddir %s -bugzilla no -getfile no -updatecode no' %(self.proj,self.mtktag,lastpathtag,JRDimportDir))	
				if os.path.isfile('/local/build/GetChanglist_Code/result/diffResult_%s_to_%s.html' %(lastpathtag,self.mtktag)) and os.path.isfile('/local/build/GetChanglist_Code/result/%s_to_%s_changelist.xls' %(lastpathtag,self.mtktag) ):
					print "=================Getchangelist success ======================="
					print getoutput("cp '/local/build/GetChanglist_Code/result/diffResult_%s_to_%s.html' '/local/mtk_patch_import/mtkpatch/%s/%s/'" %(lastpathtag,self.mtktag,self.sharefoldname,self.mtktag))
					print getoutput("cp '/local/build/GetChanglist_Code/result/%s_to_%s_changelist.xls' '/local/mtk_patch_import/mtkpatch/%s/%s/'" %(lastpathtag,self.mtktag,self.sharefoldname,self.mtktag))
				os.chdir(JRDimportDir)
				gitLink = u"\\\\10.92.32.12\\RDhzKM\\5-SWD\\I-Patch\\MTKPatch\\%s\\%s" % (self.sharefoldname,self.mtktag)
				gitNamefilder = gitLink

				print "========"
				print "importIdDict",self.importIdDict
				print "devCodeProjectIDList",self.devCodeProjectIDList
				#for simplex data start
				print "importIdDictSimplex",self.importIdDictSimplex
				print "devCodeProjectIDListSimplex",self.devCodeProjectIDListSimplex
				#for simplex data end
				print "branch",self.__branch
				print "patch_type",self.patch_type
				print "vnum",self.vnum
				print "pnum",self.pnum
				print "eservice_ID",self.eservice_ID
				print "gitLink",gitLink
				print "gitNamefilder",gitNamefilder
				print "========"
				if self.insertDataToPrsm:
					self.insertImportCommitInfoTO_dotp_mtk_commit(self.importIdDict,self.devCodeProjectIDList,self.__branch,self.patch_type,self.vnum,self.pnum,self.eservice_ID,'',gitLink,gitNamefilder)
					#for simplex data start
				self.insertImportCommitInfoTO_simplex_mtk_commit(self.importIdDictSimplex,self.devCodeProjectIDListSimplex,self.__branch,self.patch_type,self.vnum,self.pnum,self.eservice_ID,'',gitLink,gitNamefilder)
					#for simplex data end


			else:
				
				patchFilename = getoutput("ls %s | grep '%s' | grep '%s' | grep P%s\).tar.gz" % (self.__ongoingPatch, self.__mtkproj[i],self.__mtkrelease[i], self.patchNo[i]))
				print '========patchFilename========',patchFilename
				if not os.path.isfile('/local/mtk_patch_import/mtkpatch/%s/%s'% (self.sharefoldname,patchFilename)):
					print "cp '/local/mtk_patch_import/TODO/%s'  '/local/mtk_patch_import/mtkpatch/%s'" %(patchFilename,self.sharefoldname)
					print getoutput("cp '/local/mtk_patch_import/TODO/%s'  '/local/mtk_patch_import/mtkpatch/%s'" %(patchFilename,self.sharefoldname))
				patchfile_list.append(patchFilename)
				self.patch_type,self.vnum,self.pnum,self.eservice_ID = self.getMtkPatchInfor(patchFilename)
				#else:
					#self.patch_type,self.vnum,self.pnum,eservice_ID = self.getMtkPatchInfor(patchFilename)
				print "========patch_type,vnum,pnum,eservice_ID========\n"
				print self.patch_type,self.vnum,self.pnum,self.eservice_ID
				print "========"
				print 'change dir ==================>%s\n' % self.__CodeDir 
				os.chdir(self.__CodeDir)

				#porting P27_ALPS02813031_For_jhz6755_66_cn_m_alps-mp-m0.mp7-V1_P27_.tar.gz^^^^^^1fe186680fcb8b6332079ba88ad00fdf860daec3^^^^^^/home/swd3/project/shine-plus
				#porting MOLY00217132_eServiceID_For_JHZ6755_66_CN_M_LWCTG__MOLY.LR11.W1539.MD.MP.V9.P14_.tar.gz^^^^^^0ea7fdd0657309505949f686c31226373ff31f7b^^^^^^/home/swd3/project/shine-plus
				#porting SIXTH00014477_ALPS02988853_For_JHZ6755_66_CN_M_C2K__SIXTH.CBP.MD.MP3.V8_P5_.tar.gz^^^^^^40f305e4143c228647cab09c4f126d0616d23c70^^^^^^/home/swd3/project/shine-plus
				#porting P27_ALPS02813031_For_jhz6755_66_cn_m_alps-mp-m0.mp7-V1_P27_.tar.gz^^^^^^88c9d5fd6d39ee3af2646da57bd219b750688664^^^^^^/home/swd3/project/shine-plus
				print self.gitlog_format % (self.repopath, '%s^^^^^^%H^^^^^^$PWD', self.__mtkproj[i],self.__mtkrelease[i], self.patchNo[i])
				patchList = getoutput(self.gitlog_format % (self.repopath, '%s^^^^^^%H^^^^^^$PWD', self.__mtkproj[i],self.__mtkrelease[i], self.patchNo[i])).split('\n')
			
				for item in xrange(len(patchList)):
			    		itemInfo = patchList[item].split('^^^^^^')
			    		if 3 != len(itemInfo):
						print "patchList have problems. patchList = %s" % patchList
						print "The pacth has no modification"
						sys.exit(1)
				comment_list.append( patchList[0].split('^^^^^^')[0] )
				print "========patchList=======",patchList
				for item in xrange(len(patchList)):
					itemInfo = patchList[item].split('^^^^^^')
					gitName = itemInfo[2].split(self.__branch)[1]
					match = re.match("^/(.*)",gitName)
					gitName = match.group(1)
					gitLink = itemInfo[1]
					file_link[numtotype[i]][gitName] = gitLink
				for (gitName,link) in file_link[numtotype[i]].items():
					gitNamefilder = gitName
					#if gitName.find("kernel-")!=-1:
						#gitName = 'kernel'
					if gitName.find("modem")!=-1:
						if gitName.find("SIXTH")!=-1:
							gitName = "modem/C2K"
						if gitName.find("MOLY")!=-1:
							modemdir=os.path.dirname(getoutput('find %s/modem -name *.git | grep MOLY' % self.__CodeDir))
							print modemdir
							os.chdir(modemdir)
							tmpstr = getoutput("git remote -v | grep fetch | awk '{print $2}'")
							print tmpstr
							match = re.match(r'.*(modem.*)\.git',tmpstr)
							if match:
								gitName=match.group(1)
							else:
								gitName = "modem"
							os.chdir(self.__CodeDir)
					if gitName in self.__git_remote_name_dict and gitName != self.__git_remote_name_dict[gitName]:
						gitLink = self.gLink % (self.dept,self.platform,self.__git_remote_name_dict[gitName], link)
					else:	
						gitLink = self.gLink % (self.dept,self.platform,gitName, link)


					print "========"
					print "importIdDict",self.importIdDict
					print "devCodeProjectIDList",self.devCodeProjectIDList
					#for simplex data start
					print "importIdDictSimplex",self.importIdDictSimplex
					print "devCodeProjectIDListSimplex",self.devCodeProjectIDListSimplex
					#for simplex data end
					print "branch",self.__branch
					print "patch_type",self.patch_type
					print "vnum",self.vnum
					print "pnum",self.pnum
					print "eservice_ID",self.eservice_ID
					print "gitLink",gitLink
					print "gitNamefilder",gitNamefilder
					print "========"
					if self.insertDataToPrsm:
						self.insertImportCommitInfoTO_dotp_mtk_commit(self.importIdDict,self.devCodeProjectIDList,self.__branch,self.patch_type,self.vnum,self.pnum,self.eservice_ID,link,gitLink,gitNamefilder)
					#for simplex data start
					self.insertImportCommitInfoTO_simplex_mtk_commit(self.importIdDictSimplex,self.devCodeProjectIDListSimplex,self.__branch,self.patch_type,self.vnum,self.pnum,self.eservice_ID,link,gitLink,gitNamefilder)
					#for simplex data end
			print "start to get ismailed value"
			self.is_mailed = False
			if self.ismailed(self.importIdDict,self.patchNo[i],self.patchtype[i]):
				print "get ismailed value"
				self.is_mailed = True

			if self.is_mailed:
				print "Have send mail to the owner,send mail to vers"
				self.__sendtovers()
				sys.exit(0)
			print 'self.importIdDict',self.importIdDict
			print 'self.projectid_codeBranch_Dict',self.projectid_codeBranch_Dict
			#for simplex data start
			print 'self.importIdDictSimplex',self.importIdDictSimplex
			print 'self.projectid_codeBranch_DictSimplex',self.projectid_codeBranch_DictSimplex
			#for simplex data end
			if self.insertDataToPrsm:
				for projectID1 in self.importIdDict[self.patch_type].keys():
					for projectID2 in self.projectid_codeBranch_Dict.keys():
						if projectID1 == projectID2:
							#pass
							self.insertImportId_And_DevBranch_To_dotp_mtk_merge(self.importIdDict[self.patch_type][projectID1],self.projectid_codeBranch_Dict[projectID2],self.patchowner)			             
			#os.system('python /local/int_jenkins/mtk_patch/lib/insertdbToWr.py %s %s %s %s' % (self.__branch,self.vnum,self.pnum,self.eservice_ID) )

			#for simplex data start
			for projectID1 in self.importIdDictSimplex[self.patch_type].keys():
				for projectID2 in self.projectid_codeBranch_DictSimplex.keys():
					if projectID1 == projectID2:
						#pass
						self.insertImportId_And_DevBranch_To_dotp_mtk_merge_simplex(self.importIdDictSimplex[self.patch_type][projectID1],self.projectid_codeBranch_DictSimplex[projectID2],self.patchowner)			             
			#os.system('python /local/int_jenkins/mtk_patch/lib/insertInforToManpower.py %s %s %s %s %s' % (self.__branch,self.vnum,self.pnum,self.eservice_ID,'yan.xiong'))
			#for simplex data end
	#def insertImportCommitInfoTO_dotp_mtk_commit(self,importIdDict,devCodeProjectIDList,importBranchName,patch_type,vnum,pnum,eservice_ID,commit_id,import_patch_link,git_name):
		#for eachProjectID in devCodeProjectIDList:			
			#import_id = self.getImportIDAfterInsert(eachProjectID,importBranchName,vnum,pnum,patch_type,eservice_ID)
			#print "the import id is %s" % import_id
			#if eachProjectID not in importIdDict[patch_type].keys():
				#importIdDict[patch_type][eachProjectID] = import_id 
			#self.insertImportCommitIDInfo(import_id,commit_id,import_patch_link,git_name)
		#return importIdDict	
	def ismailed(self,importIdDict,patchnum,patchtype):
		mailed_status = False
		for importid in importIdDict[patchtype].values():
			if len(str(importIdDict[patchtype]))==0:
				continue
			mysql='SELECT ismailed FROM dotp_mtk_import WHERE id="%s" and pnum="P%s" and patch_type="%s"' % (importid,str(patchnum),patchtype)
			print 'mysql',mysql
			print importid,str(patchnum),patchtype
			try:
				_mailed_status = self.query(mysql,True)
				print '_mailed_status',_mailed_status
			except Exception,e:
				print e
				print "connect to prsm failed"
			if _mailed_status and len(_mailed_status)==1 and _mailed_status[0]==1:
				mailed_status = True
		return mailed_status
	def setmailed(self,importIdDict,patchnum,patchtype):
		for importid in importIdDict[patchtype].values():
			if len(str(importIdDict[patchtype]))==0:
				continue
			mysql='UPDATE dotp_mtk_import SET ismailed=1 WHERE id="%s" and pnum="P%s" and patch_type="%s"' % (importid,str(patchnum),patchtype)
			print 'mysql',mysql
			print importid,str(patchnum),patchtype
			try:			
				self.db_cursor.execute(mysql)
				self.db_conn.commit()		
			except Exception, e:
				print e
				

	def getownerstatus(self,branch,patchnum,patchtype):
		mysql='SELECT mm.owner,mm.merge_status FROM dotp_mtk_merge as mm LEFT JOIN dotp_mtk_import as mi on mm.import_id=mi.id WHERE mm.merge_patch="%s" and mi.pnum="P%s" and mi.patch_type="%s"' % (branch,str(patchnum),patchtype)
		print 'mysql',mysql
		print branch,str(patchnum),patchtype
		try:
			owner,status = self.query(mysql,True)
			print 'owner',owner,'status',status
			if status==1:
				print "status is closed"
			elif owner:
				print "find last patch owner:",owner
			else:
				print "cannot find last patch owner"
				sys.exit(1)
			
		except Exception,e:
			print e
			print "connect to prsm failed"
		return owner,status

	def getmtkdefect(self,eserverid):
		mtk_defect = ''
		mysql='SELECT mtk_defect FROM dotp_mtk_import WHERE eservice_ID=%s'% eserverid
		print 'mysql',mysql
		try:
			mtk_defect = self.query(mysql,True)
			print 'mtk_defect',mtk_defect
		except Exception,e:
			print e
			print "connect to prsm failed"
		return mtk_defect
			
	def getEmailContent(self,mailBody,str_patchNo,file_link):
		item = 0
		if len(self.delgit.keys()) != 0:
			mailBody.append('<p align\'Left\'><fontcolor="#FF0000"><b>Note: Please contact int to delete these gits in dint xml:')
			mailBody.append('<p align\'Left\'><fontcolor="#FF0000"><b>Gits need detele in xml: %s' % ';'.join(self.delgit.keys()))
		for str_type in self.patchtype:
			for (gitName,link) in file_link[str_type].items():
			    	gitNamefilder = gitName
			    	#if gitName.find("kernel-")!=-1:
					#gitName = 'kernel'
				if gitName.find("modem")!=-1:
					if gitName.find("SIXTH")!=-1:
						gitName = "modem/C2K"
					if gitName.find("MOLY")!=-1:
						modemdir=os.path.dirname(getoutput('find %s/modem -name *.git | grep MOLY' % self.__CodeDir))
						print modemdir
						os.chdir(modemdir)
						tmpstr = getoutput("git remote -v | grep fetch | awk '{print $2}'")
						print tmpstr
						match = re.match(r'.*(modem.*)\.git',tmpstr)
						if match:
							gitName=match.group(1)
						else:
							gitName = "modem"
						os.chdir(self.__CodeDir)
				if gitName in self.__git_remote_name_dict and gitName!=self.__git_remote_name_dict[gitName]:
					gitLink = self.gLink % (self.dept,self.platform,self.__git_remote_name_dict[gitName], link)
				else:
			    		gitLink = self.gLink % (self.dept,self.platform,gitName, link)
			    	#self.insertImportCommitInfoTO_dotp_mtk_commit(self.importIdDict,self.devCodeProjectIDList,self.__branch,self.patch_type,self.vnum,self.pnum,self.eservice_ID,link,gitLink,gitNamefilder)
				item = item + 1
			    	mailBody.append('<p align=\'Left\'>%s) %s<br/></p><p align=\'Left\'><a href="%s">%s</a></p>' % (item,gitName,gitLink,gitLink))
				if len(self.chpbf_gitname_list)>0 and len(self.chpbt_branch_list)>0:
					assert len(self.chpbf_gitname_list)==len(self.chpbt_branch_list),"wrong length of chpbf_gitname or chpbt_branch,please check it"
					if gitName in self.chpbf_gitname_list:
						chpbt_branch = self.chpbt_branch_list[self.chpbf_gitname_list.index(gitName)]
						mailBody.append('<p align\'Left\'><fontcolor="#FF0000"><b>Note: You must modify the branch of %s at the same time."' % chpbt_branch)
				if len(self.chplf_gitname_list)>0 and  len(self.chplt_gitname_list)>0:
					for i in xrange(len(self.chplf_gitname_list)):
						if gitName in self.chplf_gitname_list[i]:
							chplt_g = self.chplt_gitname_list[i]
							mailBody.append('<p align\'Left\'><fontcolor="#FF0000"><b>Note: You must modify the git name of %s at the same time."' % chplt_g)			
				if self.care_git_folder and len(self.care_git_folder)>0 and self.care_files and len(self.care_files)>0 and gitName in self.care_git_folder:
					assert len(self.care_git_folder)==len(self.care_files),"wrong length of care_git_folder or care_files,please check it."
					grep_care_branch_files_b,grep_care_branch_files = self.grep_care_branch_files(gitName,self.care_files[self.care_git_folder.index(gitName)])
					if grep_care_branch_files_b:
						modem_remind='''1，运行过程中要求输入NDK本地存放路径，如果本地没有NDK包，请将NDK copy至本地存放，NDK获取路径：\\\\rd-filebackup\RDhzKM\5-SWD\I-Patch\MTKPatch\NDK
2,解压NDK并在modem/LWTG/apps下执行./build.sh clean,build,pack all GEN93_USER编译
3,对A3A, U3A ,U5A_PLUS三个项目依次执行：
	a,清除vendor/mediatek/proprietary/modem下的内容；
	b,将2在modem/LWTG/apps/build/GEN93_USER/rel/下的所有生成文件copy至vendor/mediatek/proprietary/modem对应的项目文件夹下；
	c,执行modem/compile_modem.py编译并copy modem镜像至vendor/mediatek/proprietary/modem下'''
						self.mailBody_remind.append('<p align\'Left\'><b>    注意: 有修改到modem/LWTG/app下文件: </b></p>')
						self.mailBody_remind.append('<p align\'Left\'>        %s<br/></p>' % grep_care_branch_files.replace('\n','<br/>'))
						oprate_remind='''由于该mtk pacth有修改到modem/LWTG/apps/下的文件，mtk要求使用NDK编译APP，并将生成文件copy至vendor/mediatek/proprietary/modem下指定路径。
请工程师执行以下操作：'''
						self.mailBody_remind.append('<p align\'Left\'><font color="#FF0000"><b>%s</b></font></p>' % oprate_remind.replace('\n','<br/>'))
						self.mailBody_remind.append('<p align\'Left\'><font color="#FF0000">    操作一：请在merge完该patch至modem/LWTG库并验证merge没有问题之后，在modem下执行python update_modem.py脚本，该脚本会自动执行以下操作：</font></p>')
						self.mailBody_remind.append('<p align\'Left\'>%s<br/></p>' % modem_remind.replace('\n','<br/>'))
						self.mailBody_remind.append('<p align\'Left\'><font color="#FF0000">    操作二：update_modem.py执行完后，请工程师check下vendor/mediatek/proprietary/modem的db文件的版本号跟该modem patch版本号是否一致，并对modem/LWTG以及vendor/mediatek/proprietary/modem发patch。</font></p>')
						
			    	gitnameDir = self.__CodeDir + "/"+ gitNamefilder
			    	for keyname in self.checkFileDict.keys():
					filename = self.checkFileDict[keyname]['filename']
					if self.checkFileDict[keyname]['gitname'] == gitName:
						if True == self.getFileLibNvram(gitnameDir,filename):
							mailBody.append('<p align=\'Left\'><font color="#FF0000"><b>Note: The file of %s has been changed in patch %s.</font></b></p>' % (filename,str_patchNo.replace('_',' ')))
							mailBody.append('<p align=\'Left\'><font color="#FF0000"><b>Please contact System team to check whether to merge this modification to project code</font></b></p>')
							mailBody.append('<br/>')  
			    	projectnamestr = '' 
			    	for projectname in self.projectList:
					if True == self.getFileLibNvram(gitnameDir,projectname):
						projectnamestr = projectname + ',' + projectnamestr
						projectnamestr = projectnamestr.strip(',')
			    	if projectnamestr:
			    		project_str = 'Please merge the files' + projectnamestr + 'to project by the link'
			    		mailBody.append('<p align=\'Left\'><b><font color=green>%s:%s</font></b></p>' % (gitName,project_str))		
			    	if gitName == "vendor":
					sofilename = "libnvram.so"
					if 'sochanged' == self.getFileLibNvram(gitnameDir,sofilename):
						mailBody.append('<p align=\'Left\'><font color="#FF0000">Note: The file of libnvram.os has been changed.Please check the link</font></p>')	          
			    	if gitNamefilder == 'build':
					platform_security_value = self.checkBuildCore(gitnameDir)
					if platform_security_value:
						mailBody.append('<p align=\'Left\'><b><font color=green>Note: The file of build/core/version_defaults.mk has been changed.Please check the modification from the above link.</font></b></p>')
						mailBody.append('<p align=\'Left\'><b><font color=green>The current value of %s </font></b></p>' % platform_security_value)
		return item	

	def getPatchLink(self, mailBody, patchNo=-1):
		for eachbranch in self.__DriveOnlyBranch:
			DriveOnlyCode = ''
			DriveOnlyCode = self.__DriveOnlyCode + eachbranch
			print 'change dir ==================>%s\n' % DriveOnlyCode
			os.chdir(DriveOnlyCode)
			patchList = getoutput(self.gitlog_format % (self.repopath, '%s^^^^^^%H^^^^^^$PWD', self.__patchname_ap,self.__MPRelease_ap, patchNo)).split('\n')
			for item in range(len(patchList)):
		    		itemInfo = patchList[item].split('^^^^^^')
		    		if 3 != len(itemInfo):
		        		print "patchList have problems. patchList = %s" % patchList
					print "The pacth has no modification"
		        		sys.exit(1) 
		
		    	mailBody.append('<p align=\'Left\'>Patch Link in driveonly import branch %s:</p>' % eachbranch)
		    	for item in range(len(patchList)):
		        	itemInfo = patchList[item].split('^^^^^^')
		        	gitName = itemInfo[2].split(eachbranch)[1]
		        	match = re.match("^/(.*)",gitName)
		        	gitName = match.group(1)
		        	#if gitName.find("kernel-")!=-1:
					#gitName = 'kernel'
				if gitName.find("modem")!=-1:
					if gitName.find("SIXTH")!=-1:
						gitName = "modem/C2K"
					if gitName.find("MOLY")!=-1:
						modemdir=os.path.dirname(getoutput('find %s/modem -name *.git | grep MOLY' % self.__CodeDir))
						print modemdir
						os.chdir(modemdir)
						tmpstr = getoutput("git remote -v | grep fetch | awk '{print $2}'")
						print tmpstr
						match = re.match(r'.*(modem.*)\.git',tmpstr)
						if match:
							gitName=match.group(1)
						else:
							gitName = "modem"
						os.chdir(self.__CodeDir)
					
				if gitName in self.__git_remote_name_dict and gitName!=self.__git_remote_name_dict[gitName]:
					gitLink = gitLink % (self.dept,self.platform,self.__git_remote_name_dict[gitName], itemInfo[1])
				else:				
		        		gitLink = gitLink % (self.dept,self.platform,gitName, itemInfo[1])
		        	mailBody.append('<p align=\'Left\'>%s) %s</p><p align=\'Left\'><a href="%s">%s</a></p>' % (item+1,gitName,gitLink,gitLink))
		return mailBody

	def __getremotegitname(self):	
		f = open("%s/.repo/project.list"%self.__CodeDir)
		gitname_list = f.readlines()
		f.close()
		self.delgit={}
		print "git@10\.92\.32\.10:(/%s)?(/mtk6753)?(/%s)?/?(\S+?)\.git|git@hz\.gerrit\.tclcom\.com:(/%s)?/?%s/?(\S+?)\.git"%(self.dept,self.platform,self.dept,self.platform)
		for _gitname in gitname_list:
			gitname = _gitname.strip('\n')
			print 'change dir ==================>%s\n' % self.__CodeDir+'/'+gitname
			if os.path.exists(self.__CodeDir+'/'+gitname):
				os.chdir(self.__CodeDir+'/'+gitname)
				#self.delgit[gitname] = False
			else:
				self.delgit[gitname] = True
				repo_gitname=self.__CodeDir+'/'+'.repo/projects/'+gitname+'.git'
				os.system('rm -rf %s' % repo_gitname)		
			tmp = commands.getoutput("git remote -v | grep 'fetch' ")
			print "git remote -v | grep 'fetch' ",tmp
			if tmp:
				match=re.findall(r"git@10\.92\.32\.10:(/mtk6753)?(/%s)+/?(\S+?)\.git|git@10\.92\.32\.10:(/%s)?(/mtk6753)?(/%s)+/?(\S+?)\.git|git@hz\.gerrit\.tclcom\.com:(/%s)?(/%s)+/?(\S+?)\.git"%(self.platform,self.dept,self.platform,self.dept,self.platform),tmp)
				if match:
					#print "match=:=",match,match[0][1] 
					self.__git_remote_name_dict[gitname] = match[0][2] if match[0][2] else match[0][6] if match[0][6] else match[0][9]
				else:
					print "cannot find git remote -v to get gitname"
					sys.exit(1)
			else:
				print "cannot find git remote -v to get gitname"
				sys.exit(1)
		
	def __getBugzillaInfo(self, comment_list=['','',''],result={'ALPS':{'mtkdefect':''},'MOLY':{'mtkdefect':''},'SIXTH':{'mtkdefect':''}}):
		#porting P36_ALPS03057833_For_jhz6755_66_cn_m_alps-mp-m0.mp7-V1_P36_.tar.gz
		#porting MOLY00217132_eServiceID_For_JHZ6755_66_CN_M_LWCTG__MOLY.LR11.W1539.MD.MP.V9.P14_.tar.gz
		#porting SIXTH00015434_ALPS03057833_For_JHZ6755_66_CN_M_C2K__SIXTH.CBP.MD.MP3.V8_P6_.tar.gz
		reciever = 'renzhi.yang.hz@tcl.com'
		if reciever.endswith('.com'):
			result['assigned'] = reciever
			result['assigned'] = result['assigned'].encode('gb2312')
		for comment in comment_list:
			if not comment:
				continue
				
			match =re.match(r'porting (P\d+_+)?ALPS(\d+)_.+', comment)
			if match:
			    	while True:
					InputString = "Summary:"              
					if len(InputString) > 0:
				    		result['ALPS']['shortDesc'] = InputString
				    		break
					else:
				    		continue
			    	result['ALPS']['bugID'] = 'ALPS'+match.group(2)
			    	result['ALPS']['comment'] = comment
			    	result['ALPS']['patchID'] = 'ALPS'
			    	result['ALPS']['mtkdefect'] = self.getmtkdefect(match.group(2))
			    	#return result
			match =re.match(r'porting (P\d+_+)?MOLY(\d+)_.+', comment)
			if match:
			    	while True:
					InputString = "Summary:"              
					if len(InputString) > 0:
				    		result['MOLY']['shortDesc'] = InputString
				    		break
					else:
				    		continue
			    	result['MOLY']['bugID'] = 'MOLY'+match.group(2)
			    	result['MOLY']['comment'] = comment
			    	result['MOLY']['patchID'] = 'MOLY'
			    	result['MOLY']['mtkdefect'] = self.getmtkdefect(match.group(2))
			    	#return result
			match =re.match(r'porting (P\d+_+)?SIXTH(\d+)_.+', comment)
			if match:
			    	while True:
					InputString = "Summary:"              
					if len(InputString) > 0:
				    		result['SIXTH']['shortDesc'] = InputString
				    		break
					else:
				    		continue
			    	result['SIXTH']['bugID'] = 'SIXTH'+match.group(2)
			    	result['SIXTH']['comment'] = comment
			    	result['SIXTH']['patchID'] = 'SIXTH'
			    	result['SIXTH']['mtkdefect'] = self.getmtkdefect(match.group(2))
			    	#return result
			#match =re.match(r'porting P\d+_.+?(\d+)_.+', comment)
			#if match:
				#while True:
					#InputString = "Summary:"              
					#if len(InputString) > 0:
				    		#result['JRD']['shortDesc'] = InputString
				    		#break
					#else:
				    		#continue
				#result['JRD']['bugID'] = 'JRD' + match.group(1)
				#result['JRD']['comment'] = comment
				#result['JRD']['bugLink'] = "https://alm.tclcom.com:7003/im/issues?selection=%s" % match.group(1)
				#result['JRD']['patchID'] = 'JRD'
		return result


	def makeDriveOnlyPatchMail(self,patchNo=-1):
		'''parameter patchNo is 0,1,2,3...'''
		if int(patchNo) == -1:
			print "Parameter patchNo(%s) is error." % patchNo
			return
		if not os.path.isdir(self.__mailDir):
			os.system('mkdir -p %s' % self.__mailDir)
		mailBody = []
		dearName = 'Integrators'
		mailBody.append('<p align=\'Left\'><b>Dear %s,</b></p>' % dearName)
		allDriveOnlyBranch = ','.join(self.__DriveOnlyBranch)
		mailBody.append('<p align=\'Left\'>MTK Patch <b><font color="#FF0000">P%s</font></b> has been merged to driveonly branch(%s)<br/></p>' % (patchNo, allDriveOnlyBranch))
		mailBody.append('<p align=\'Left\'>You can check the merge result.</b></p>')
		mailBody = self.getPatchLink(mailBody,patchNo)
		a = u"\\\\10.92.32.12\\RDhzKM\\5-SWD\\I-Patch\\MTKPatch\\%s"%self.sharefoldname
		mailBody.append('<p align=\'Left\'><b>You can find this patch (P%s) in:<font color="#FF0000">%s</font></b></p>' % (patchNo, a))
		mailBody.append('<p align=\'Left\'><b>please check the modification.</b></p>') 
		mailtitle = '%s P%s Patch import to driveonly branch' %(self.__mailTitle, patchNo)
		self.__sendMail(patchNo, mailtitle, mailBody, '')


    	def checkDriveOnlyBuildResult(self,patchNo=-1):
		'''parameter patchNo is 0,1,2,3...'''
		if int(patchNo) == -1:
		    	print "Parameter patchNo(%s) is error." % patchNo
		    	return
		if not os.path.isdir(self.__mailDir):
		    	os.system('mkdir -p %s' % self.__mailDir)
		mailBody = []
		dearName = 'Integrators'
		mailBody.append('<p align=\'Left\'><b>Dear %s,</b></p>' % dearName)
		allDriveOnlyBranch = ','.join(self.__DriveOnlyBranch)
		mailBody.append('<p align=\'Left\'>MTK Patch <b><font color="#FF0000">P%s</font></b> has been merged to driveonly branch(%s)<br/></p>' % (patchNo, allDriveOnlyBranch))
		mailBody.append('<p align=\'Left\'>It has been built and been uploaded to teleweb.</b></p>')
		mailBody.append('<p align=\'Left\'>Build eng version, mtk project: %s.</b></p>' % self.__project )
		for eachbranch in self.__DriveOnlyBranch:
			DriveOnlyCode = ''
			DriveOnlyCode = self.__DriveOnlyCode + eachbranch
			mailBody.append('<p align=\'Left\'>You can find %s bins at teleweb:<b><font color="#FF0000">%s/driveonly/P%s_%s</font></b></p>' % (self.branchDict[eachbranch],self.branchDict[eachbranch], patchNo,eachbranch))
		mailBody = self.getPatchLink(mailBody,patchNo)
		mailtitle = '%s P%s Patch driveonly branch build done' %(self.__mailTitle, patchNo)
		self.__sendMail(patchNo, mailtitle, mailBody, '')

	def __sendtovers(self,tolist=[u'xiaodan.cheng@tcl.com',u'shie.zhao@tcl.com',u'renzhi.yang.hz@tcl.com']):
		mailtitle = 'MAIL RESEND!!!CHECK THE DETAILS %s' % self.__mailTitle
		mailBody=[]
		mailBody.append('<p align=\'Left\'><b>Dear %s,</b></p>' % tolist[0].split('@')[0])
		mailBody.append('<p align=\'Left\'><b>   %s,the patch mail have been send.But want to send again,Check it out.</b></p>'%self.__mailTitle)
		print "========begin of send mail to vers========"
		smtpServer = smtplib.SMTP(self.__mailServer)
		reload(sys)
		sys.setdefaultencoding('gbk')	
		msg = MIMEText(''.join(mailBody), 'html','utf-16')
		msg.set_charset('gb2312')   
		msg['From'] = self.__mailSender
		msg['Subject'] = mailtitle
		msg['To'] = tolist[0]
		msg['Cc'] = ','.join(tolist)
		domainAccount = self.__mailAccount
		domainPassword = "cxd@6235"
		smtpServer.login(self.__mailAccount, domainPassword)
		smtpServer.sendmail(self.__mailSender, tolist , msg.as_string())
		smtpServer.quit()
		print "========end of send mail to vers========"

	def __sendMail(self,str_patchNo, mailtitle, mailBody=[], to=[]):
		'''parameter toList: the PR owner(assigned) or interface or leader'''
		print "========begin of send mail========"
		smtpServer = smtplib.SMTP(self.__mailServer)
		#reload(sys)
		#sys.setdefaultencoding('gbk')	
		msg = MIMEText(''.join(mailBody), 'html','utf-16')
		msg.set_charset('gb2312')   
		msg['From'] = self.__mailSender
		msg['Subject'] = mailtitle
		#msg['Subject'] = '%s P%s Patch Merge' %(self.__mailTitle, patchNo)
		domainAccount = self.__mailAccount
		domainPassword = "cxd@6235"
		smtpServer.login(self.__mailAccount, domainPassword)
		sendTo = "all"
		tolist = []
		if sendTo == "self":
		    	msg['To'] = self.__mailSender
		    	tolist.append(self.__mailSender)
		elif sendTo == "all":
		    	if self.sendmail == True:		
		    		msg['To'] = ','.join(self.SPMEmailList) + ',' + self.patchowner
		    		msg['Cc'] = ','.join(self.__mailToList ) + ',' + ','.join(self.__mailccList)
				tolist = self.__mailToList + self.__mailccList + self.__SPMList + self.SPMEmailList + [ self.patchowner ]
				#tolist = self.__mailToList + self.__mailccList + self.__SPMList  + [ self.patchowner ]
		    		#smtpServer.sendmail(self.__mailSender, list(set(self.__mailToList + self.__mailccList + self.__SPMList + self.SPMEmailList + self.patchowner)), msg.as_string())
		    	else:
		    		msg['To'] = ','.join(self.__mailToList)
		    		msg['Cc'] = ','.join(self.__mailccList + self.__SPMList )
				tolist = self.__mailToList + self.__mailccList + self.__SPMList
				#smtpServer.sendmail(self.__mailSender, list(set(self.__mailToList + self.__mailccList + self.__SPMList)), msg.as_string())
		else:
		    	print "Send Mail to (%s) Error: %s" % (sendTo, msg.as_string())
		print "sender",self.__mailSender
		print "tolist",tolist
		print "message",msg.as_string()
		smtpServer.sendmail(self.__mailSender, tolist , msg.as_string())
		fp = open(self.__mailDir + "/%s.eml" % str_patchNo, 'wb')
		fp.write(msg.as_string())
		fp.close()
		smtpServer.quit()
		print "========end of send mail========"
	def grep_care_branch_files(self,care_git_folder,care_files):
		pwdcd = os.getcwd()
		print 'change dir ==================>%s\n' % self.__CodeDir+'/'+care_git_folder
		os.chdir(self.__CodeDir+'/'+care_git_folder)
		care_files_str = care_files.replace(',','|')
		tmp = getoutput("git log -1 --name-only | grep -E '%s'" % care_files_str)
		if tmp:
			print 'care files detected!!!'
			print tmp
			self.care_str = "git log -1 --name-only and find all these files are modify but these files need to check by bsp :\n" + tmp + "\n Thanks"
			print 'change dir ==================>%s\n' % pwdcd
			os.chdir(pwdcd)
			return True,tmp
		
		return False,tmp
if __name__ == '__main__':
	print "========test for argv========"
	print sys.argv
	print "========test for argv========"
	conf = Config()
	conf.addFromArg(sys.argv[1:])
	mail = patchmail(conf)
	mail.makePatchMail()

