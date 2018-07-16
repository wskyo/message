#!/usr/bin/python
#coding=utf-8

import os
import re
import sys
#import getpass
from commands import *
import commands
from time import *
#import pexpect
#import smtplib
#import MySQLdb
#from email.header import Header
#from email.MIMEText import MIMEText
sys.path.append('/local/int_jenkins/lib')
sys.path.append('/local/int_jenkins/mtk_patch/lib')
import xlrd
import string
from CheckFile import *
from dotProjectDb import *
from checkPatchInfor import *
from Config import *
sys.path.append('/local/int_jenkins/mtk_patch')
from Mangage import *

class PatchMerge(Mangage):
	def __init__(self,conf):
		self.simplex=False
		self.insertDataToPrsm= True
		basedir = conf.getConf('basedir','base dir','/local')
		self.proj = conf.getConf('project','project name','')
		#self.patchowner = conf.getConf('patchowner','patch owner','')
		
		self.eservice_ID = conf.getConf('eservice_ID','eservice ID',-1)
		self.force = conf.getConf('force','re cherry-pick forcely',False)
		self.repopath = '/local/tools/repo/repo'
		print 'change dir ==================>%s\n' % basedir
		os.chdir(basedir)
		self.__baseDir = os.getcwd()		
		self.debug = False
		self.__pushCodeToGit = True
		
		wb = xlrd.open_workbook('/local/int_jenkins/mtk_patch/jb3-mp-import.xls')
		mtkSheet = wb.sheet_by_name(u'ModemInfo')
		print "project name",self.proj
		for row in xrange(0,mtkSheet.nrows):
			#print "project of ALPS",self.proj,ap_st.cell(row,0).value.strip()
			if mtkSheet.cell(row,0).value.strip() == self.proj:
				mp_row = row
		
		if not mp_row:
			print "Cannot find project in the MOLY SHEET OF THE Excel!"
			sys.exit(1)
		
		self.__branch = mtkSheet.cell(mp_row, 1).value.strip()
		self.__project = mtkSheet.cell(mp_row, 2).value.strip()
		
		self.mtkproj = mtkSheet.cell(mp_row, 2).value.strip()
		self.mtkrelease = mtkSheet.cell(mp_row, 3).value.strip()
		self.__DriveOnlyBranch = mtkSheet.cell(mp_row, 12).value.strip().split(',')
		#self.__TelewebDirName = mtkSheet.cell(mp_row, 12).value.strip()
		self.__mak = mtkSheet.cell(mp_row, 14).value.strip()
		self.__modemname = mtkSheet.cell(mp_row, 15).value.strip()
		self.manifestdir = mtkSheet.cell(mp_row, 16).value.strip()
		self.lunchproj = self.mtkproj
		self.platform = mtkSheet.cell(mp_row, 17).value.strip()
		self.sp_modem = mtkSheet.cell(mp_row, 18).value.strip().split(',')
		self.cp_data_dir = mtkSheet.cell(mp_row, 22).value.strip()
		self.old_data_file = mtkSheet.cell(mp_row, 23).value.strip()
		self.new_data_file = mtkSheet.cell(mp_row, 24).value.strip()
		self.prj_MOLY_name = mtkSheet.cell(mp_row, 25).value.strip()
		self.old_mak = mtkSheet.cell(mp_row, 27).value.strip().split(',')
		self.new_mak = mtkSheet.cell(mp_row, 28).value.strip().split(',')
                self.patch_type_str = mtkSheet.cell(mp_row, 29).value.strip()
                if self.patch_type_str == '':
                	self.patch_type_str = conf.getConf('patchtypestr','patch type str','MOLY')
                self.download_type = ''
		assert len(self.old_mak) == len(self.new_mak),"wrong length of mak"
		self.default_band=''
		if self.prj_MOLY_name:
			self.Code = "/local/mtk_patch_import/" + self.__branch +'/'+ self.prj_MOLY_name
		else:
			self.Code = "/local/mtk_patch_import/" + self.__branch + "/modem"
		if not os.path.exists(self.Code + '/.git'):
		        print self.patch_type_str
			tmp = getoutput("find %s -name '.git' | grep '%s' | sed 's/\/\.git//g'" % (self.Code,self.patch_type_str))
			if tmp:
				self.Code = tmp
				print 'tmp',tmp
				#print 'self.Code',self.Code
			else:
				print "no modem found!"
				sys.exit(1)
		print 'self.Code',self.Code
		#self.Code = "/local/mtk_patch_import/" + self.__branch + "/modem"
		self.mergeDone = "/local/mtk_patch_import/mergeDone"
		self.__ignorePatch = "/local/mtk_patch_import/ignorePatch"
		self.ongoingPatch = "/local/mtk_patch_import/TODO"
		self.__mailDir = "/local/mtk_patch_import/Mail"
		self.__start = "/local/mtk_patch_import/start"
		self.__DriveOnlyCode = "/local/mtk_patch_import/"
		self.devCodeBranch = []
		self.devCodeProjectIDList = []
		
		self.importIdDict = {}
		self.projectid_codeBranch_Dict = {}
		self.patch_type = ''
		self.vnum = ''
		self.pnum = ''
		self.eservice_ID_pl = ''
		self.description = ''
		self.untardir = ''
		self.spacelimit = 5
		self.untarstr = "%s/MD-P%s"
		self.gitlog_format = 'git log  --format=%s | grep "%s" | grep "%s"'
		self.gitlog = self.gitlog_format %('%s',self.mtkproj,self.mtkrelease)
		self.porting_format = self.gitlog_format +'| grep "porting P%s_" | sort'
		self.build_dir=''
		print self.Code,self.Code + '/mtk_rel',self.Code + '/mcu/mtk_rel'
		if self.__mak:
			if os.path.isdir(self.Code + '/mcu/mtk_rel'):
				self.build_cmd = './m "%s.mak" new' % self.__mak
				self.build_dir = '/mcu'
			else:
				self.build_cmd = './make.sh "%s.mak" new' % self.__mak
		elif os.path.isdir(self.Code + '/mtk_rel'):
			self.build_cmd = './make.sh "%s(%s)%s.mak" new'
		elif os.path.isdir(self.Code + '/mcu/mtk_rel'):
			self.build_cmd = './m "%s(%s)%s.mak" new'
			self.build_dir = '/mcu'
		else:
			print "no mtk_rel or mcu/mtk_rel detected"
			print "Please check it."
			sys.exit(1)
		print self.build_cmd
		self.get_db_connection()
		self.devCodeProjectIDList = self.getProjectIDFromImportBranch(self.__branch)
		print self.devCodeProjectIDList
		
		
		self.devCodeBranch = self.getDevBranchNameFromIProjectID(self.devCodeProjectIDList,self.projectid_codeBranch_Dict,self.__branch)

		self.checkFileDict = self.getAffectFileDict()
		self.projectList = self.checkProjectName()
		if not os.path.isdir(self.__start):
		    	os.system('mkdir -p %s' % self.__start)

		print "baseDir = %s\nbranch = %s\nmtkproj = %s\nmtkrelease = %s\nongoingPatch = %s\nDriveOnlyBranchName = %s" % (self.__baseDir,self.__branch, self.mtkproj,self.mtkrelease, self.ongoingPatch,self.__DriveOnlyBranch)
		

	def repo_code(self, codedir, BranchName):
		print "Now checking the modem code if exist,"
		if not os.path.isdir(codedir):
			os.system('mkdir -p %s' % codedir)
		print 'change dir ==================>%s\n' % codedir
		os.chdir(codedir)

		if os.path.exists(codedir + "/.git") == False:
			print "no modem found in %s" % codedir
			print "Please check the branch %s code have dowloaded sucessfully!"
			sys.exit(1)
			#print "-----------------------------download modem start-----------------------------\n"
			#os.system('git clone git@10.92.32.10:%s/%s/modem.git -b %s'%(self.manifestdir,self.platform,BranchName))
			#print 'change dir ==================>%s\n' % (codedir+'/modem')
			#os.chdir(codedir)
			#os.system('git checkout %s' % BranchName)
			#print "-----------------------------download modem end-----------------------------\n"
        
	def MergePatch(self,patchtype,patchNo=-1):
		print "Please create file(start) on /local/mtk_patch_import directory. If not exist, the script will stop and exit."
		self.repo_code(self.Code, self.__branch)
		if (os.path.exists("/local/mtk_patch_import/start") == True):
			self.reset(self.Code,self.__branch)
			print "patchNo %s" % patchNo
			patchFilename = self.takePatch(self.Code, patchNo,True,True)
			if 'Nofile' == patchFilename:
				print "No p%s patch. Please copy the correct patch to TODO directory" % patchNo
				sys.exit(1)
			if not self.__mak:
				modemname = self.getmodemname(patchFilename)
				print 'modemname',modemname
				print "self.__modemname",self.__modemname
				if modemname:
					pass
				elif self.__modemname:
					modemname = self.__modemname
				else:
					print "Provide a modem name"
					sys.exit(1)
				print 'modemname',modemname
				self.cpfiletomodem(self.Code)
				self.build_cmd = self.build_cmd % (self.lunchproj,modemname,'')
				if self.cp_data_dir and	self.old_data_file and self.new_data_file:
					print "cp -r %s %s"%(self.Code+'/'+self.cp_data_dir+'/'+self.old_data_file,self.Code+'/'+self.cp_data_dir+'/'+self.new_data_file)
					os.system("cp -r %s %s"%(self.Code+'/'+self.cp_data_dir+'/'+self.old_data_file,self.Code+'/'+self.cp_data_dir+'/'+self.new_data_file))	
			os.chdir(self.Code)
			prevMD5 = getoutput('rm -rf /tmp/tempfile; git add .; git status >> /tmp/tempfile; md5sum /tmp/tempfile').split()[0]
			if 'Success' == self._compile(self.Code+self.build_dir):
				print "Compile success"
				self.reset(self.Code,self.__branch)
				patchFilename = self.takePatch(self.Code, patchNo,True,True)
				self.cpfiletomodem(self.Code)
				self.patch_type,self.vnum,self.pnum,self.eservice_ID_pl = self.getMtkPatchInfor(patchFilename)
				self.description = self.getDescriptionFromPatchListFile(self.Code, self.untardir,self.eservice_ID_pl)
				if self.eservice_ID==-1:
					self.eservice_ID = self.eservice_ID_pl
				if self.cp_data_dir and	self.old_data_file and self.new_data_file:
					print "cp -r %s %s"%(self.Code+'/'+self.cp_data_dir+'/'+self.old_data_file,self.Code+'/'+self.cp_data_dir+'/'+self.new_data_file)
					os.system("cp -r %s %s"%(self.Code+'/'+self.cp_data_dir+'/'+self.old_data_file,self.Code+'/'+self.cp_data_dir+'/'+self.new_data_file))
				os.chdir(self.Code)
				print "description",self.description 	        
				self.insertAllImportInfoTO_importSheet(self.devCodeProjectIDList,self.__branch,self.patch_type,self.vnum,self.pnum,self.eservice_ID,self.description,patchtype)
				comment = 'porting P%s_%s' %(patchNo, patchFilename.replace('(', '_').replace(')', '_'))
				tagname = 'porting_modem_patch_%s' % patchFilename.replace('(', '_').replace(')', '_')
				tagcomment = 'porting modem patch P%s' % patchNo
				print "commit comment is %s" % comment
				print "tagname is %s" % tagname
				print "tagcomment is %s" % tagcomment
				print comment
				if True == self.__pushCodeToGit:
					print 'start merge.....'
				    	os.system('git add .')
				    	nextMD5 = getoutput('rm -rf /tmp/tempfile; git status >> /tmp/tempfile; md5sum /tmp/tempfile').split()[0]
					gitpushlog = '/tmp/%s_gitpush.log'%self.__branch
					os.system(' > %s' % gitpushlog)
				    	if prevMD5 == nextMD5:
				        	#os.system('git commit -m "%s"; git push origin HEAD:refs/heads/%s 2>&1 | tee -a %s; git tag -a %s -m "%s"; git push origin %s 2>&1 | tee -a %s' % (comment,self.__branch,gitpushlog,tagname,tagcomment,tagname,gitpushlog))
						os.system('git commit -m "%s"; git push jgs HEAD:%s 2>&1 | tee -a %s' % (comment,self.__branch,gitpushlog))
						tmp = getoutput("grep 'fatal:' %s" % gitpushlog)
						if tmp:
							print "push fatal error!"
							print "=========logs======"
							print tmp
							print "=========logs======"
							sys.exit(1)
						tmp = getoutput("grep 'error:' %s" % gitpushlog)
						if tmp:
							print "push error!"
							print "=========logs======"
							print tmp
							print "=========logs======"
							sys.exit(1)
						print "finish push to origin master"
				    	print 'finish merge....'
					self.del_todo_tmp_dir()
			else:
				print "The code build failed"
				sys.exit(1)
	def getmodemname(self,patchFilename):
		tmp = patchFilename.replace('(','_').replace(')','_')
		module = re.compile('.*%s_(.*)%s.*' % (self.mtkproj,self.mtkrelease))
		match = re.match(module,tmp)
		if match:
			modemnames = match.group(1)
   			modemname = modemnames.split('__')[0]
			print "patchFilename,modemname",patchFilename,modemname
			if modemname:
				return modemname
			else:
				return ''
		print "no match modem name find in %s" % patchFilename
		sys.exit(1)

	def MergePatchToDriveOnly(self,patchNo=-1):
		for branch in self.__DriveOnlyBranch:
			DriveOnlyCode =  self.__DriveOnlyCode + branch
			DriveCode = DriveOnlyCode + "/modem"
			tmp=''
			if not os.path.exists(DriveCode + '/.git'):
		
				tmp = getoutput("find %s -name '.git' | grep '%s' | sed 's/\/\.git//g'" % (DriveCode,self.patch_type_str))
				if tmp:
					DriveCode = tmp
					#print 'tmp',tmp
					#print 'self.Code',self.Code
				else:
					print "no modem found!"
					sys.exit(1)
			print 'DriveCode',DriveCode
			self.repo_code(DriveCode,branch) 
			self.eachDriveOnlyBranchImport(DriveCode, branch, patchNo)
			DriveOnlyCode = ''
			DriveCode = ''		            	
		#self.movePatchToMergeDone(patchNo)

	def eachDriveOnlyBranchImport(self, DriveCode, eachbranch, patchNo=-1):
		print "Please create file(start) on /local/mtk_patch_import directory. If not exist, the script will stop and exit."  
		if (os.path.exists("/local/mtk_patch_import/start") == True):
			self.reset(DriveCode,eachbranch)
			print "patchNo %s" % patchNo
			patchFilename = self.takePatch(DriveCode,patchNo,False)
			print 'change dir ==================>%s\n' % DriveCode
			os.chdir(DriveCode)
			if not self.__mak:
				modemname = self.getmodemname(patchFilename)
				print 'modemname',modemname
				print "self.__modemname",self.__modemname
				if self.build_cmd.find('%s') != -1:
					if modemname:
						self.build_cmd = self.build_cmd % ( self.lunchproj,modemname,self.sp_modem[0])
					elif self.__modemname:
						self.build_cmd = self.build_cmd % ( self.lunchproj,self.__modemname,self.sp_modem[0])
					else:
						print "Provide a modem name"
						sys.exit(1)
			comment = 'porting P%s_%s for driveonly' %(patchNo, patchFilename.replace('(', '_').replace(')', '_'))
			tagname = 'porting_modem_patch_%s_for_%s' % (patchFilename.replace('(', '_').replace(')', '_'), eachbranch)
			tagcomment = 'porting modem patch P%s' % patchNo
			print "commit comment is %s" % comment
			print "tagname is %s" % tagname
			print "tagcomment is %s" % tagcomment
			cherrypick_current = True
			if not self.force:
				print 'git log jgs/%s --format=%s | grep "%s" | grep "%s" | grep "porting P%s_" | sort' %(eachbranch,'%s^^^^^^%H^^^^^^$PWD', self.mtkproj,self.mtkrelease, patchNo)
				patchList = getoutput('git log jgs/%s --format=%s | grep "%s" | grep "%s" | grep "porting P%s_" | sort' %(eachbranch,'%s^^^^^^%H^^^^^^$PWD', self.mtkproj,self.mtkrelease, patchNo)).split('\n')
				print 'patchList========%s'%patchList
				for patch in patchList:
					if patch:
						cherrypick_current = False
			print 'cherrypick_current',cherrypick_current
			if True == self.__pushCodeToGit and cherrypick_current:
				print 'start merge.....'
				self.takeImportCommitForDriveOnly(DriveCode, self.__branch, eachbranch, patchNo)
				#modemname = self.getmodemname(patchFilename)
				#print 'modemname',modemname
				#if self.build_cmd.find('%s') != -1:
					#if modemname:
						#self.build_cmd = self.build_cmd % ( self.lunchproj,modemname,self.sp_modem[0])
					#elif self.__modemname:
						#self.build_cmd = self.build_cmd % ( self.lunchproj,self.__modemname,self.sp_modem[0])
					#else:
						#print "Provide a modem name"
						#sys.exit(1)
				#self.cpfiletomodem(DriveCode)
				gitpushlog = '/tmp/%s_gitpush.log'%self.__branch
				os.system(' > %s'%gitpushlog)
				#os.system('git push origin HEAD:refs/heads/%s; git tag -a %s -m "%s"; git push origin %s' % (eachbranch,tagname,tagcomment,tagname))
				os.system('git commit -m "%s";git push jgs HEAD:%s 2>&1 | tee -a %s' % (tagcomment,eachbranch,gitpushlog))
				tmp = getoutput("grep 'fatal:' %s" % gitpushlog)
				if tmp:
					print "push fatal error!"
					print "=========logs======"
					print tmp
					print "=========logs======"
					#sys.exit(1)
				tmp = getoutput("grep 'error:' %s" % gitpushlog)
				if tmp:
					print "push error!"
					print "=========logs======"
					print tmp
					print "=========logs======"
					sys.exit(1)
			print 'finish drive only branch merge....'
			print "Now start to build drive only branch modem"
			print 'DriveCode+self.build_dir',DriveCode+self.build_dir
			print 'self.build_cmd',self.build_cmd
			if 'Success' == self._compile(DriveCode+self.build_dir):
				print "Driveonly Branch build successfully"
			else:
				print "Driveonly Branch build failed"
				sys.exit(1)	

    
                
	def reset(self, codedir,branch=''):
        	if False == self.debug:
			print "-----------------------------reset start-----------------------------\n"
			print 'change dir ==================>%s\n' % codedir
		    	os.chdir(codedir)
		    	#sleep(120)
		    	print "reset start... \nClean all, reset to HEAD and git pull"
			if os.path.isdir('./build'):
		    		os.system('rm -rf ./build')
		    	elif os.path.isdir('./mcu/build'):
				os.system('rm -rf ./mcu/build')
			else:
				print "No build was found during reseting the code"
				
			os.system('git reset --hard HEAD')
		    	os.system('git clean -df')
			print 'change dir ==================>%s\n' % '/local/mtk_patch_import/'+branch
			os.chdir('/local/mtk_patch_import/'+branch)
			tmpstrs = getoutput('grep modem .repo/project.list').split('\n')
			sync_modem_str = ''
			if len(tmpstrs) == 1 :
				sync_modem_str = tmpstrs[0]
		    		
			elif len(tmpstrs) >1 :
				for tmpstr in tmpstrs:
					if tmpstr.find(self.patch_type_str) != -1:
						sync_modem_str = tmpstr
					if tmpstr.find(self.prj_MOLY_name) != -1:
						sync_modem_str = tmpstr
					if tmpstr.find(self.prj_MOLY_name.upper()) != -1:
						sync_modem_str = tmpstr
			else:
				print 'modem no found in project!!!'
				sys.exit(1)
			if sync_modem_str:
				os.system('%s sync %s'%(self.repopath,sync_modem_str))	
			else:
				print 'sync_modem_str is NULL!!!'
				print 'modem no found in project!!!'
				sys.exit(1)
		    	print "-----------------------------reset done-----------------------------\n"

    


    

	def checkcompile(self,buildstatus,branchname=''):
		if (buildstatus >> 8) == 0:
                	print buildstatus
                	return 'Success' 
            	else:
                	print buildstatus
                	return 'Fail'

	def cpfiletomodem(self,Code):
		tmp_dir = ''
		print 'self.old_mak',self.old_mak
		print 'self.new_mak',self.new_mak
		for i in xrange(0,len(self.old_mak)):
			if not self.old_mak[i]:
				continue
			ps_dir = getoutput("find %s -name '*%s*.mak'" % (Code,self.new_mak[i]))
			ps_md = os.path.basename(ps_dir)
			print 'ps_md',ps_dir,ps_md
			tmp_dir = getoutput("echo '%s' | sed 's/%s/%s/g'" % (ps_dir,self.new_mak[i],self.old_mak[i]))
			tmp_md = os.path.basename(tmp_dir)
			print 'tmp_md',tmp_dir,tmp_md
			if os.path.isfile(tmp_md):
				print "====cp -f %s %s" % (tmp_dir,ps_dir)
				os.system("cp -f '%s' '%s'" % (tmp_dir,ps_dir))
				print "sed -i 's/%s/%s/g' '%s'" % (tmp_md,ps_md,ps_dir)
				os.system("sed -i 's/%s/%s/g' '%s'" % (tmp_md,ps_md,ps_dir))
				tmp = getoutput("sed -n '/%s/p' '%s'"%(self.mtkrelease,ps_dir)).split('\n')
				if tmp:
					assert len(tmp)==1,"more than one MOLY strings was found"
					if tmp[0].find('\r')==-1:
						print "sed -i 's/%s/%s\r/g' '%s'"%(tmp[0],tmp[0],ps_dir)
						os.system("sed -i 's/%s/%s\r/g' '%s'"%(tmp[0],tmp[0],ps_dir))

			
	

	

    

if __name__ == "__main__":
	print "test for argv"
	print sys.argv
	conf = Config()
	conf.addFromArg(sys.argv[1:])
	patchtype = conf.getConf('patchtype','patch type','')
	patchnum = conf.getConf('patchnum','patch number',-1)#sys.argv[3]
	operation = conf.getConf('operation','operation','')
	pm = PatchMerge(conf)
	#print dir(pm)
	print '====================begin of %s====================\n' % operation
	if operation == 'MergePatch':
		pm.MergePatch(patchtype,patchnum)
	elif operation == 'MergePatchToDriveOnly':  
		pm.MergePatchToDriveOnly(patchnum)
	else:
		print "ERROR eccour in operation!"
	print '====================end of %s====================\n' % operation
	
