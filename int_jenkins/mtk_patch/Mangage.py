#!/usr/bin/python
#coding=utf-8

import os
import re
import sys
import getpass
from commands import *
import commands
from time import *
import pexpect
import smtplib
import MySQLdb
from email.header import Header
from email.MIMEText import MIMEText
sys.path.append('/local/int_jenkins/lib')
sys.path.append('/local/int_jenkins/mtk_patch/lib')
import xlrd
import string
from CheckFile import *
from dotProjectDb import *
from checkPatchInfor import *
from Config import *

class Mangage(CheckFile,dotProjectDb,checkPatchInfor):
	def __init__(self,conf):
		self.gitlog_format=''
		self.gitlog = ''
		#self.porting_format = self.gitlog_format +'| grep "porting P%s_" | sort'
		self.untardir = ''
		self.untarstr = "%s/P%s"
		self.spacelimit = 5
		self.build_cmd = ''
		self.patchowner = conf.getConf('patchowner','patch owner','')
		
		self.subbranch = ''
		self.lunchproj = ''
		self.default_band=''
	def MergePatch(self):
		pass
	
	
	def reset(self,codedir):
		pass
	
	def repo_code(self, CodeDir, CodeBranchName):
		pass
	def MergePatchToDriveOnly(self,patchNo=-1):
		pass		
	def getNextPatchNo(self):
        	PatchNo = 0
		print 'change dir ==================>%s\n' % self.Code
        	os.chdir(self.Code)
        	patchList = getoutput(self.gitlog).split('\n')
        	for item in patchList: 
            		match = re.match(r'porting P(\d+).+', item)
            		if match:
                		tmpNo = match.group(1)
            		else:
                		continue
            
            		if int(tmpNo) > int(PatchNo):
                		PatchNo = tmpNo
        	return int(PatchNo) + 1
	
	def takePatch(self,codedir,patchNo='',take_patch=True,rmdatabase=False):
		if '' == patchNo:
            		print "patchNo is none"
            		sys.exit(1)
        	elif '0' == patchNo:
			print 'ls %s | grep "%s" | grep "%s"' % (self.ongoingPatch, self.mtkproj,self.mtkrelease)            
            		patchFilename = getoutput('ls %s | grep "%s" | grep "%s"' % (self.ongoingPatch, self.mtkproj,self.mtkrelease))
       		else:
			print 'ls %s | grep "%s" | grep "%s" | grep P%s\).tar.gz' % (self.ongoingPatch, self.mtkproj,self.mtkrelease, patchNo)
			patchFilename = getoutput('ls %s | grep "%s" | grep "%s" | grep P%s\).tar.gz' % (self.ongoingPatch, self.mtkproj,self.mtkrelease, patchNo))
			if patchFilename == '':
				patchFilename = getoutput('ls %s | grep "%s" | grep "%s" | grep p%s.tar.gz' % (self.ongoingPatch, self.mtkproj,self.mtkrelease, patchNo))
       		if 0 == len(patchFilename):
            		print "Nofile was detected !!!!!!\n"
			print "system exit!!!\n"
			sys.exit(1)
		if take_patch:
			self.untardir = self.untarstr % (self.ongoingPatch,patchNo)
			if not os.path.isdir(self.untardir):
				os.system('mkdir -p %s' % self.untardir)
				os.system('tar zxvf "%s/%s" -C %s' % (self.ongoingPatch,patchFilename,self.untardir))
			if not os.path.isdir(codedir):
		    		#os.system('mkdir -p %s' % codedir)
				print "No code was found on %s \n" % codedir
				print "system exit.Download code and restart the task!"
				sys.exit(1)
			self.deletefile(codedir, self.untardir)
			if rmdatabase:
				self.rmdatabase(codedir,patchNo)
			if os.path.exists(self.untardir+'/alps'):
				print 'cp -dpRv %s/alps/* %s' %(self.untardir,codedir)
				os.system('cp -dpRv %s/alps/* %s' %(self.untardir,codedir))
				if os.path.exists(codedir+'/tools/.git'):
					print 'cp -f %s/patch_list.txt %s/tools/ '%(self.untardir,codedir)
					os.system('cp -f %s/patch_list.txt %s/tools/ '%(self.untardir,codedir))
			else:
				print 'cp -dpRv %s/* %s' %(self.untardir,codedir)
				os.system('cp -dpRv %s/* %s' %(self.untardir,codedir))
			
			#if self.untardir and os.path.exists(self.untardir):
				#os.system('rm -rf %s' % self.untardir)
		
        	return patchFilename
	def del_todo_tmp_dir(self):
		if self.untardir and os.path.exists(self.untardir):
			print 'rm -rf %s' % self.untardir
			os.system('rm -rf %s' % self.untardir)
	def deletefile(self, codedir, untardir):
		print "======== begin of delete file ========\n"
		print 'change dir ==================>%s\n' % untardir
        	os.chdir(untardir)
		#print 'untardir',untardir
		print 'ls %s | grep *.txt' % untardir
        	patchlistFilename = getoutput('ls | grep .txt')
		print 'patchlistFilename',patchlistFilename	
        	if patchlistFilename:
			print "grep '^delete' '%s' | sed 's/delete //g'" % patchlistFilename
			tmps = getoutput("grep '^delete' '%s' | sed 's/delete //g'" % patchlistFilename).split('\n')
			print "the delete files are: \n",tmps
			for tmp in tmps:
				#tmp = tmp.replace('\n',' ')
				print "the delete file is: \n",tmp
				print '\n'
				if not tmp:
					continue
				tmp_basename = os.path.basename(tmp)
				tmp_dirname = os.path.dirname(tmp)
				print 'change dir ==================>%s\n' % codedir
        			os.chdir(codedir)
				if os.path.exists(codedir+'/'+tmp):
					print 'change dir ==================>%s\n' % codedir+'/'+tmp_dirname
        				os.chdir(codedir+'/'+tmp_dirname)
					if not tmp_basename:
						tmp_dirname_f = os.path.dirname(tmp_dirname)
						tmp_basename_f = os.path.basename(tmp_dirname)
						print 'change dir ==================>%s\n' % codedir+'/'+tmp_dirname_f
        					os.chdir(codedir+'/'+tmp_dirname_f)
						print 'git rm -r %s' % tmp
						#deleteResult = os.system('git rm -r "%s"' % tmp_basename_f)
						deleteResult = os.system('rm -rf "%s"' % tmp_basename_f)
					else:
						print 'git rm %s' % tmp
						#deleteResult = os.system('git rm "%s"' % tmp_basename)
						deleteResult = os.system('rm -rf "%s"' % tmp_basename)
					if deleteResult>>8 != 0:
						print "delete file %s failed" % tmp
						print "Please check why the file %s cannot be deleted" % tmp
						sys.exit(1)
					else:
						print "delete file %s successfully" % tmp
			print 'change dir ==================>%s\n' % codedir
        		os.chdir(codedir)
			
		else:
			print "No any patch_list.txt was detected in %s !Check the package of patch_list.txt.\n" % untardir
			#sys.exit(1)
		print 'change dir ==================>%s\n' % codedir
        	os.chdir(codedir)
		print "======== end of delete file ========\n"
	
	def rmdatabase(self,codedir,patchNo):
		print "======== begin of rm data base ========\n"
		tmp = ''
		print 'change dir ==================>%s\n'%codedir
		os.chdir(codedir)
		if os.path.isdir('%s/mtk_rel' % codedir):
			tmp = getoutput("find -name 'BPLGUInfoCustomApp*' | grep -v 'P%s'" % patchNo)
			if tmp :
				tmp = tmp.replace('\n',' ')
				print "rm all this file:\n"
				print tmp
				print '\n'
				os.system('git rm %s' % tmp)
			tmp =  getoutput("find -name '_BPLGUInfoCustomApp*' | grep -v 'P%s'" % patchNo)
			if tmp :
				tmp = tmp.replace('\n',' ')
				print "rm all this file:\n"
				print tmp
				print '\n'
				os.system('git rm %s' % tmp)
		elif os.path.isdir('%s/mcu/mtk_rel' % codedir):
			tmp = getoutput("find -name '*.EDB' | grep -v 'P%s.EDB'" % patchNo)
			if tmp :
				tmp = tmp.replace('\n',' ')
				print "rm all this file:\n"
				print tmp
				print '\n'
				os.system('git rm %s' % tmp)
			tmp = getoutput("find -name '*.check' | grep -v 'P%s.EDB.check'" % patchNo)
			if tmp :
				tmp = tmp.replace('\n',' ')
				print "rm all this file:\n"
				print tmp
				print '\n'
				os.system('git rm %s' % tmp)
			tmp = getoutput("find -name 'DbgInfo_DSP*' | grep -v '_P%s_'" % patchNo)
			if tmp :
				tmp = tmp.replace('\n',' ')
				print "rm all this file:\n"
				print tmp
				print '\n'
				os.system('git rm %s' % tmp)
		else:
			print "========No such dir '%s/mtk_rel' or '%s/mcu/mtk_rel'========\n" % (codedir,codedir)
			
		print "======== end of rm data base ========\n"	

	def _compile(self, CodeDir,branchname=''):		
		space = getoutput('df -h /local/ | awk \'{print $4}\'').split('\n')[1][:-1]
		if (space < self.spacelimit):
			print "**Error: there is no enough space left on device!"
			return "Fail"
		print 'change dir ==================>%s\n' % CodeDir
		os.chdir(CodeDir)
		if os.path.exists('./tools/init/strcmpex_linux.exe'):
			os.system('chmod 777 ./tools/init/strcmpex_linux.exe')
		print "building......"
		if False == self.debug:
			if self.default_band:
				print 'change dir ==================>%s\n' % CodeDir+'/modem'
				os.chdir(CodeDir+'/modem')
				if self.default_build:
					print 'python compile_modem.py -p %s -b %s' % (self.default_build,self.default_band)
					os.system('python compile_modem.py -p %s -b %s' % (self.default_build,self.default_band))
				else:
					print 'python compile_modem.py -b %s' % self.default_band
					os.system('python compile_modem.py -b %s' % self.default_band)
				print 'change dir ==================>%s\n' % CodeDir
				os.chdir(CodeDir)
			if self.download_type == 'git' :
				os.system('echo export JAVA_HOME=`pwd`/prebuilts/jdk/jdk8/linux-x86 > java_jdk8.env; echo export JRE_HOME=`pwd`/prebuilts/jdk/jdk8/linux-x86/jre >> java_jdk8.env;export echo CLASSPATH=.:`pwd`/prebuilts/jdk/jdk8/linux-x86/lib:`pwd`/prebuilts/jdk/jdk8/linux-x86/jre/lib >> java_jdk8.env;echo export PATH=`pwd`/prebuilts/jdk/jdk8/linux-x86/bin:`pwd`/prebuilts/jdk/jdk8/linux-x86/jre/bin:$PATH >> java_jdk8.env')
				buildStatus = os.system('source `pwd`/java_jdk8.env ; java -version; %s' % self.build_cmd)
				java_version_git=getoutput('java -version')
				print "git java_version after source java_jdk8.env",java_version_git

			print "self.build_cmd",self.build_cmd
			java_version=getoutput('java -version')
			print "java_version before",java_version
			if self.download_type != 'git' :
				buildStatus = os.system(self.build_cmd)
			print "java_version after",java_version
			print "========buildStatus is %s========\n" % str(buildStatus)
			return self.checkcompile(buildStatus,branchname)
		else:
			buildInfo = raw_input('[Debug mode] Please input compile result Info "==> [FAIL]" or "other string":') 
			if buildInfo.find("==> [FAIL]") >= 0:
				return "Fail"
			return 'Success'
	def checkcompile(self,buildstatus,branchname=''):
		pass

	def movePatchToMergeDone(self, patchNo):
        	os.system('mkdir -p %s' % self.mergeDone)
		os.system('mv %s/*%s*%s*P%s\).tar.gz %s' % (self.ongoingPatch,self.mtkproj,self.mtkrelease,patchNo,self.mergeDone))

	
	
	
	def gitlogcherrypick(self,codedir,branch,driveonlyBranch,patchNo,folder='modem'):
		print 'change dir ==================>%s\n' % codedir
		os.chdir(codedir)
		print 'git log jgs/%s --format=%s | grep "%s" | grep "%s" | grep "porting P%s_" | sort' %(branch,'%s^^^^^^%H^^^^^^$PWD', self.mtkproj,self.mtkrelease, patchNo)
		patchList = getoutput('git log jgs/%s --format=%s | grep "%s" | grep "%s" | grep "porting P%s_" | sort' %(branch,'%s^^^^^^%H^^^^^^$PWD', self.mtkproj,self.mtkrelease, patchNo)).split('\n')
		print "patchList =====",patchList
		if "fatal: ambiguous argument" in patchList[0]:
			print "fatal: ambiguous argument"
			return
		if len(patchList) != 0:
			for item in range(len(patchList)):
				if patchList[item] == '':
					continue
				itemInfo = patchList[item].split('^^^^^^')
				print "itemInfo====",itemInfo
				if len(itemInfo) == 0:
					continue
				gitName = itemInfo[2].split(driveonlyBranch)[1]
				print "gitName----",gitName
				match = re.match("^/(.*)",gitName)
		        	gitName = match.group(1)
				print "the gitname is %s" % gitName
				if gitName.find(folder) != -1:
					print "git cherry-pick %s" % itemInfo[1]
					cerryPickInfo = getoutput('git cherry-pick %s' % itemInfo[1])		
					if "error:" in cerryPickInfo:
						print "cherry pick failed"
						print "you have to check conflicts"
						sys.exit(1)
					else:
						print "cherry pick successfully"

	def takeImportCommitForDriveOnly(self, codedir, branch, driveonlyBranch, patchNo='',DriveOnlygitDir=''):
		if '' == patchNo:
		    	print "patchNo is none"
		    	sys.exit(1)

		if not os.path.isdir(codedir):
		    	print "The driveonly code download failed"
		    	sys.exit(1)
		if not DriveOnlygitDir:
			self.gitlogcherrypick(codedir,branch,driveonlyBranch,patchNo)
		else:
			for folder in DriveOnlygitDir:
				gitDir = ''
				gitDir = codedir + "/" + folder
				self.gitlogcherrypick(gitDir,branch,driveonlyBranch,patchNo,folder)
	def gitMergeToDriveronly(self, codedir, importBranch, driveonlyBranch, patchNo='',gitpushlog='log.txt'):
		if '' == patchNo:
		    	print "patchNo is none"
		    	sys.exit(1)

		if not os.path.isdir(codedir):
		    	print "The driveonly code download failed"
		    	sys.exit(1)
		os.chdir(codedir)
		remoteImportBranch = "jgs/" + importBranch
		print 'repo forall -c git merge --no-commit %s' %remoteImportBranch
		mergeresult = os.system('%s forall -c "pwd&&git merge --no-commit %s" | tee -a %s' % (self.repopath,remoteImportBranch,gitpushlog))
		print "==========merge result is %s =========" %mergeresult
		if mergeresult == 0 :
			print "merge branch has error ,please check %s,search:not something we can merge " %gitpushlog
                        #sys.exit(1)
		tmp = getoutput("grep 'error:' %s" % gitpushlog)
		if tmp:
			print "Merge error!"
			print "=========logs======"
			print tmp
			print "=========logs======"
			sys.exit(1)
		print "git merge end"
		print '%s status | tee -a Merge_modify_files.txt' %(self.repopath)
		os.system('%s status | tee -a Merge_modify_files.txt' %(self.repopath))
		tmp = getoutput("grep ' Um' Merge_modify_files.txt")
		if tmp:
			print "=========It has merge confict files============================================"
                        print "=========Pease find merge confict files from Merge_modify_files.txt============="
                 
                comment = 'Porting P%s_%s, merge from %s ' %(patchNo,self.mtktag,importBranch)
                print 'repo forall -c "git commit -m %s"' %comment
                os.system('%s forall -c git commit -m "%s"'%(self.repopath,comment))
                print 'repo forall -c "git push jgs HEAD:%s"' %driveonlyBranch
                os.system('%s forall -c "pwd&&git push jgs HEAD:%s" | tee -a %s' %(self.repopath,driveonlyBranch,gitpushlog))
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
		print "finish push to origin %s" %driveonlyBranch
		print 'finish merge....'  
		tmp = getoutput("grep ' Um' Merge_modify_files.txt")
		if tmp:
			print "=========It has merge confict files============================================"
			print "=========Pease find merge confict files from Merge_modify_files.txt============="

			
	def rmbuildfile(self,codedir):
		print 'change dir ==================>%s\n' % codedir
		os.chdir(codedir)
		if os.path.isdir(codedir+'/out'):
			print "rm -rf %s" % codedir+'/out'
			os.system("rm -rf %s" % codedir+'/out')
			print "rm -f /local/release/*Build.txt"
			os.system("rm -f /local/release/*Build.txt") 
				
						
	
	
	
	

	
	





















	
