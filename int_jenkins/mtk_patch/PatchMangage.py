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
sys.path.append('/local/int_jenkins/mtk_patch')
from Mangage import *
import smtplib
from email.header import Header
from email.MIMEText import MIMEText
import xml.dom.minidom
import datetime

class PatchMerge(Mangage):
	def __init__(self,conf):
		self.simplex=False
		self.insertDataToPrsm= True
		basedir = conf.getConf('basedir','base dir','/local')
		self.proj = conf.getConf('project','project name','')
		#self.patchowner = conf.getConf('patchowner','patch owner','')
		self.repopath = '/local/tools/repo/repo'
		print 'change dir ==================>%s\n' % basedir
		os.chdir(basedir)
		self.__baseDir = os.getcwd()		
		self.debug = False
		self.__pushCodeToGit = True
		
		wb = xlrd.open_workbook('/local/int_jenkins/mtk_patch/jb3-mp-import.xls')
		mtkSheet = wb.sheet_by_name(u'MTKInfo')
		print "project name",self.proj
		for row in xrange(0,mtkSheet.nrows):
			#print "project of ALPS",self.proj,ap_st.cell(row,0).value.strip()
			if mtkSheet.cell(row,0).value.strip() == self.proj:
				ap_row = row
		
		if not ap_row:
			print "Cannot find project in the ALPS SHEET OF THE Excel!"
			sys.exit(1)
		
		self.__branch = mtkSheet.cell(ap_row, 1).value.strip()
		self.__project = mtkSheet.cell(ap_row, 2).value.strip()
		self.mtkproj = mtkSheet.cell(ap_row, 2).value.strip()
		self.mtkrelease = mtkSheet.cell(ap_row, 3).value.strip()
		self.__DriveOnlyBranch = mtkSheet.cell(ap_row, 11).value.strip().split(',')
		self.__TelewebDirName = mtkSheet.cell(ap_row, 12).value.strip().split(',')
		self.dept = mtkSheet.cell(ap_row, 13).value.strip()
		self.manifestdir = mtkSheet.cell(ap_row, 14).value.strip()
		self.lunchproj = mtkSheet.cell(ap_row, 15).value.strip()
		self.platform = mtkSheet.cell(ap_row, 16).value.strip()
		self.updatePjName = mtkSheet.cell(ap_row, 17).value.strip().split(',')
		self.sharefoldname = mtkSheet.cell(ap_row,18).value.strip()
		if not self.sharefoldname:
			self.sharefoldname = self.__project
		self.otherprj = mtkSheet.cell(ap_row, 19).value.strip().split(',')
		self.default_band = mtkSheet.cell(ap_row, 20).value.strip()
		self.default_build = mtkSheet.cell(ap_row, 21).value.strip()
		self.grep_v = mtkSheet.cell(ap_row, 22).value.strip()
		self.care_driveronly = mtkSheet.cell(ap_row, 24).value.strip()
		self.care_git_folder = mtkSheet.cell(ap_row, 25).value.strip()
		self.care_files = mtkSheet.cell(ap_row, 26).value.strip()
		self.download_type = mtkSheet.cell(ap_row, 27).value.strip()
                #self.mtkrelease = mtkSheet.cell(ap_row, 28).value.strip()
                self.mtkversion = mtkSheet.cell(ap_row, 29).value.strip()
		self.keepmtk = mtkSheet.cell(ap_row, 31).value.strip()
                self.patchnum = conf.getConf('patchnum','patch number',-1)#sys.argv[3]
                #self.mtktag = "t-" + self.mtkrelease + "." + str(self.patchnum)
                self.mtktag = "t-" + self.mtkrelease + str(self.patchnum)
		self.care_str = ''
		self.Code = "/local/mtk_patch_import/" + self.__branch
		self.__DriveOnlyCode = "/local/mtk_patch_import/"
		self.mergeDone = "/local/mtk_patch_import/mergeDone"
		self.__ignorePatch = "/local/mtk_patch_import/ignorePatch"
		self.ongoingPatch = "/local/mtk_patch_import/TODO"
		self.__mailDir = "/local/mtk_patch_import/Mail"
		self.__start = "/local/mtk_patch_import/start"
		self.branchDict = {}
		self.checkFileDict = self.getAffectFileDict()
		self.projectList = self.checkProjectName()
		self.devCodeBranch = []
		self.devCodeProjectIDList = []
		self.importIdDict = {}
		self.projectid_codeBranch_Dict = {}
		self.patch_type = ''
		self.vnum = ''
		self.pnum = ''
		self.eservice_ID = ''
		self.description = ''
		self.untardir = ''
		self.untarstr = "%s/P%s"
		self.spacelimit = 20
		self.gitlog_format = '%s forall -c \'git log --format=%s\' | grep "%s" | grep "%s"'
		self.gitlog = self.gitlog_format % (self.repopath, '%s', self.mtkproj,self.mtkrelease)
		self.build_cmd = 'source build/envsetup.sh && lunch full_%s-eng && make -j24 2>&1 | tee android.log' % self.lunchproj
		self.get_db_connection()
		self.devCodeProjectIDList = self.getProjectIDFromImportBranch(self.__branch)
		print self.devCodeProjectIDList
		if len(self.devCodeProjectIDList)>0:
			self.devCodeBranch = self.getDevBranchNameFromIProjectID(self.devCodeProjectIDList,self.projectid_codeBranch_Dict,self.__branch)
		if len(self.__DriveOnlyBranch) == len(self.__TelewebDirName):
			for item in range(len(self.__DriveOnlyBranch)):
				self.branchDict[self.__DriveOnlyBranch[item]] = self.__TelewebDirName[item]
				print "the diff dirveonly branch need upto diff teleweb dir"
				print self.branchDict
		else:
			print "len(self.__DriveOnlyBranch) != len(self.__TelewebDirName)"
			print self.__DriveOnlyBranch,self.__TelewebDirName
		if not os.path.isdir(self.__start):
		    	os.system('mkdir -p %s' % self.__start)

	def updatemtkcurmanifest(self,manifest):
		dom = xml.dom.minidom.parse('%s' % manifest) 
		destDom = xml.dom.minidom.Document()
		manifestNode = destDom.createElement('manifest')
		destDom.appendChild(manifestNode)
		remoteList = dom.getElementsByTagName('remote')                              
		remoteNode = remoteList[0]               
		remoteNode.setAttribute('fetch', 'https://git01.mediatek.com/alps_release/')
		newNode = destDom.importNode(remoteNode, True)	
		manifestNode.appendChild(newNode)   
		defaultList = dom.getElementsByTagName('default')
		DefaultNode = defaultList[0]
		DefaultNode.setAttribute('sync-c', 'true')
		newNode = destDom.importNode(DefaultNode, True)	
		manifestNode.appendChild(newNode)  
		projList = dom.getElementsByTagName('project')  
		for proj in projList:
                            newNode = destDom.importNode(proj, True)                          
			    projClone = proj.getAttribute('clone-depth') 
			    if projClone != '':
                                  newNode.removeAttribute('clone-depth')                            
                            manifestNode.appendChild(newNode)
		#print "manifestNode",manifestNode
		xmlExisting = False
		workDir=os.getcwd()
		if os.path.isfile('%s' % (manifest)):
		           os.system('rm -f %s' % (manifest))
		fp = file('%s' % (manifest), 'w+')
		for line in destDom.toprettyxml(indent='  ', newl='\n', encoding='utf-8').split('\n'):
		           if line and not re.match('^\s*$', line):
			      fp.write('%s\n' % line)
		fp.close()
		print "%s has been updated" %manifest
		
	
	def repo_code(self, codedir, BranchName):
		print "Now checking the code if exist,"
		if not os.path.isdir(codedir):
			os.system('mkdir -p %s' % codedir)
		print 'change dir ==================>%s\n' % codedir
		os.chdir(codedir)
		if os.path.exists(codedir + "/.repo") == False:
	            print "-----------------------------download code start-----------------------------\n"  
                    if self.download_type == 'git' and BranchName == self.__branch:
                        manifest = codedir + "/.repo/manifests/" + self.mtktag + ".xml" 
			os.system('%s init -u http://git01.mediatek.com/alps_release/platform/manifest -b tcthz -m %s.xml --no-repo-verify' % (self.repopath,self.mtktag))
                        self.updatemtkcurmanifest(manifest)
                        os.system('%s sync -f -j8 --no-tag -c' % self.repopath)
                    elif self.download_type == 'git' and BranchName == "JRD_" + self.__branch:
                        repoinit = pexpect.spawn('%s init -u git@10.92.32.10:%s/MTK_manifest -m %s.xml && %s sync -j8 --no-tag -c' % (self.repopath,self.manifestdir,self.__branch,self.repopath))
			repoinit.expect('Your\s+Name.*')
			repoinit.sendline()
			repoinit.expect('Your\s+Email.*')
			repoinit.sendline()
			repoinit.expect('is this.*')
			repoinit.sendline('yes')
			repoinit.expect()                        

                    else:
			repoinit = pexpect.spawn('%s init -u git@10.92.32.10:%s/manifest -m %s.xml && %s sync -j8 --no-tag -c' % (self.repopath,self.manifestdir,BranchName,self.repopath))
			repoinit.expect('Your\s+Name.*')
			repoinit.sendline()
			repoinit.expect('Your\s+Email.*')
			repoinit.sendline()
			repoinit.expect('is this.*')
			repoinit.sendline('yes')
			repoinit.expect()
		    print "-----------------------------download code end-----------------------------\n"

	def GetGitList(self, codedir):
	        os.chdir(codedir)
	        os.system('find . -path ./.repo -prune -o -type d -name ".git" -print > git_list.txt')
                os.system('sed -i "s/\/\.git//g" git_list.txt')
                os.system('sed -i "s/\.\///" git_list.txt')


	def createMTKmanifest(self,codedir,branch):             
		if (os.path.exists("/local/mtk_patch_import/MTK_manifest")  == True):
			os.system('cd /local/mtk_patch_import/MTK_manifest ; git reset --hard HEAD ; git clean -df ; git pull')              
		else:
			os.system('cd /local/mtk_patch_import ; git clone git@10.92.32.10:alps/MTK_manifest')  
		os.chdir("/local/mtk_patch_import/MTK_manifest")
		if ( os.path.exists("/local/mtk_patch_import/MTK_manifest/%s.xml" %self.mtktag) == False ):
			if self.keepmtk=="yes":
				os.system('python /local/int_jenkins/others/basemanifest/main_keepmtk.py %s/.repo/manifests/%s.xml %s %s' %(codedir,self.mtktag,self.platform,branch)) 
			else:
				os.system('python /local/int_jenkins/others/basemanifest/main.py %s/.repo/manifests/%s.xml %s %s' %(codedir,self.mtktag,self.platform,branch)) 
			os.system('python /local/int_jenkins/others/updateManifest.py %s.xml %s.xml' %(branch,self.mtktag))
			os.system('mv %s.xml ./release_version/%s/' %(self.mtktag,self.platform))                      
			os.system('git add %s.xml release_version/%s/%s.xml ; git commit -m "add %s" ; git push' %(branch,self.platform,self.mtktag,self.mtktag))


	def ImportMTKGit(self,curlmanifest,gitpushlog):
		current_time = datetime.datetime.now().strftime("%Y-%m-%d")
		print current_time 
		pathlist = {}
		for eachCodeBranchName in self.devCodeBranch:
			DevBranchManifestUrl = 'http://10.92.32.10/gitweb.cgi?p=alps/manifest.git;a=blob_plain;f=%s.xml' %eachCodeBranchName
			f = urllib.urlopen(DevBranchManifestUrl, proxies={})
			pathlist[eachCodeBranchName] = []
			for line in f:
				m = re.match('.*path=\"(.*)\"\s*', line)         
				if m:                            
					pathlist[eachCodeBranchName].append(m.group(1))
			if len(pathlist[eachCodeBranchName])==0:
				print "Please check %s status" % DevBranchManifestUrl
				sys.exit(1)			
		dom = xml.dom.minidom.parse('%s' % curlmanifest)
		projList = dom.getElementsByTagName('project')
		for proj in projList:
			projName = proj.getAttribute('name')
			projPath = proj.getAttribute('path')
			if projPath == '':
				projPath = projName
			git_path = self.Code + "/" + projPath
			os.chdir(git_path)                    
			print 'git push git@10.92.32.10:%s/%s %s:%s' %(self.platform,projPath,current_time,self.__branch)
			os.system('git branch %s ; git push git@10.92.32.10:%s/%s %s:%s | tee -a %s' %(current_time,self.platform,projPath,current_time,self.__branch,gitpushlog))
			for eachCodeBranchName in self.devCodeBranch:
				if eachCodeBranchName in pathlist.keys():
					if projPath not in pathlist[eachCodeBranchName]:
						print "not find %s in %s " %(projPath,eachCodeBranchName)
						print 'git push git@10.92.32.10:%s/%s %s:%s' %(self.platform,projPath,current_time,eachCodeBranchName)
						os.system('git push git@10.92.32.10:%s/%s %s:%s' %(self.platform,projPath,current_time,eachCodeBranchName))
						for eachbranch in self.__DriveOnlyBranch:
							print 'git push git@10.92.32.10:%s/%s %s:%s' %(self.platform,projPath,current_time,eachbranch)
							os.system('git push git@10.92.32.10:%s/%s %s:%s' %(self.platform,projPath,current_time,eachbranch))


	def ImportMTKGit_else(self,curlmanifest,gitpushlog):
		current_time = datetime.datetime.now().strftime("%Y-%m-%d")
		print "current_time", current_time
		pathlist = {}
		for eachCodeBranchName in self.devCodeBranch:
			DevBranchManifestUrl = 'http://10.92.32.10/gitweb.cgi?p=alps/manifest.git;a=blob_plain;f=%s.xml' %eachCodeBranchName
			f = urllib.urlopen(DevBranchManifestUrl, proxies={})
			pathlist[eachCodeBranchName] = []
			for line in f:
				gitname_tmp = ''
				m = re.match('.*name=\"(.*)\"\s*path=.*', line)      
				if m:
					match = re.match('^mtk\w*\/(.*)', m.group(1)) 
					if match:											
						gitname_tmp= match.group(1)
					if gitname_tmp:                        
						pathlist[eachCodeBranchName].append(gitname_tmp)
			if len(pathlist[eachCodeBranchName])==0:
				print "Please check %s status" % DevBranchManifestUrl
				sys.exit(1)			
		dom = xml.dom.minidom.parse('%s' % curlmanifest)
		projList = dom.getElementsByTagName('project')
		for proj in projList:
			projName = proj.getAttribute('name')
			projPath = proj.getAttribute('path')
			match = re.match('^alps\/(.*)',projName)
			if match:
				projName = match.group(1)
			if projPath == '':
				projPath = projName
			git_path = self.Code + "/" + projPath
			os.chdir(git_path)
			print 'git push git@10.92.32.10:%s/%s %s:%s' %(self.platform,projName,current_time,self.__branch)
			os.system('git branch %s ; git push git@10.92.32.10:%s/%s %s:%s | tee -a %s' %(current_time,self.platform,projName,current_time,self.__branch,gitpushlog))
			for eachCodeBranchName in self.devCodeBranch:
				if eachCodeBranchName in pathlist.keys():
					if projName not in pathlist[eachCodeBranchName]:
						print "not find %s in %s " %(projName,eachCodeBranchName)													
						print 'git push git@10.92.32.10:%s/%s %s:%s' %(self.platform,projName,current_time,eachCodeBranchName)
						os.system('git push git@10.92.32.10:%s/%s %s:%s' %(self.platform,projName,current_time,eachCodeBranchName))
						for eachbranch in self.__DriveOnlyBranch:
							print 'git push git@10.92.32.10:%s/%s %s:%s' %(self.platform,projName,current_time,eachbranch)
							os.system('git push git@10.92.32.10:%s/%s %s:%s' %(self.platform,projName,current_time,eachbranch))

                           
                                          
	def MergePatch(self,patchtype,patchNo=-1):
		print "Now start to repo code"
		self.repo_code(self.Code, self.__branch)
		print "Please create file(start) on /local/mtk_patch_import directory. If not exist, the script will stop and exit."
		'''parameter patchNo is 0,1,2,3...'''
		if float(patchNo) == -1:
		     print "Parameter patchNo(%s) is error." % patchNo
		     return
		if (os.path.exists("/local/mtk_patch_import/start") == True):
		     print "Now start to get import code from server"
		     self.reset(self.Code)
                     if self.download_type == 'git':
                        print "patchNo %s" % patchNo
                        self.GetGitList(self.Code)
			self.vnum = self.mtkversion
			self.pnum = 'P'+ self.patchnum
			self.eservice_ID = self.mtktag
			ReleaseNoteDir =  u"\\\\10.92.32.12\\RDhzKM\\5-SWDI-Patch\\MTKPatch\\%s\\%s" %(self.sharefoldname,self.mtktag)
			self.description = "SW version:" + self.mtkversion + "." + self.patchnum + "; " +"release Tag:" + self.mtktag + ";\n" + "ReleaseNote&changeInfo:" + ReleaseNoteDir + ";"
			if len(self.devCodeProjectIDList)>0:
				self.insertAllImportInfoTO_importSheet(self.devCodeProjectIDList,self.__branch,'ALPS',self.vnum,self.pnum,self.eservice_ID,self.description,patchtype)
			if True == self.__pushCodeToGit:
				print 'start merge.....'
				gitpushlog = '/tmp/%s_gitpush.log'%self.__branch
				os.system(' > %s' % gitpushlog) 
                                curlmanifest = self.Code + "/.repo/manifests/" + self.mtktag + ".xml"
                                if  (os.path.exists(curlmanifest)== True):
                                    if self.keepmtk=="yes": 
					self.ImportMTKGit_else(curlmanifest,gitpushlog)					
                                    else:					
					self.ImportMTKGit(curlmanifest,gitpushlog)					
                                    tmp = getoutput("grep 'failed to push' %s" % gitpushlog)

                                    if tmp:
					print "=========logs======"
					print tmp
					print "=========logs======"
                                        sys.exit(1)   
                                else:
                                    print "Can not find %s" %curlmanifest
                                    sys.exit(1)

                                #if (os.path.exists(self.Code + "/git_list.txt")== True):
                                    #for line in open("git_list.txt"): 
                                       # line = line.strip("\n")                                       
                                        #git_path = self.Code + "/" + line
                                        #print 'git push git@10.92.32.10:%s/%s %s:%s' %(self.platform,line,self.__branch,self.__branch)
                                        #os.chdir(git_path)
                                        #os.system('git branch -d %s ; git branch %s ; git push git@10.92.32.10:%s/%s %s:%s | tee -a %s' %(self.__branch,self.__branch,self.platform,line,self.__branch,self.__branch,gitpushlog))
                                       
                                    #tmp = getoutput("grep 'failed to push' %s" % gitpushlog)
                                    #if tmp:
					#print "=========logs======"
					#print tmp
					#print "=========logs======"
                                        #sys.exit(1)                               
                                #else:
                                    #print "Can not find git_list.txt "
                                    #sys.exit(1)
				print "finish push to origin master"
				print 'finish merge....'   
			print "create %s.xml and push to MTK_manifest git" %self.mtktag
                        self.createMTKmanifest(self.Code, self.__branch)
                        print "end create %s.xml and push to MTK_manifest git" %self.mtktag
                        
                     else:
			print "patchNo %s" % patchNo
			patchFilename = self.takePatch(self.Code, patchNo)
			print 'patchFilename',patchFilename
			print "begin to clone jrd project"
			assert len(self.otherprj)==len(self.updatePjName),'len(self.otherprj) not equals to len(self.updatePjName)'
			#print 'len(self.updatePjName)',len(self.updatePjName)
			print self.updatePjName
			print self.otherprj
			for i  in xrange(0,len(self.updatePjName)):
				#print i,self.updatePjName[i],self.otherprj[i]
				if self.updatePjName[i]:
					if self.grep_v:
						print 'bash /local/int_jenkins/mtk_patch/lib/updatePjName.sh add %s %s %s %s'%(self.otherprj[i],self.updatePjName[i],self.Code+'/',self.grep_v)
						os.system('bash /local/int_jenkins/mtk_patch/lib/updatePjName.sh add %s %s %s %s'%(self.otherprj[i],self.updatePjName[i],self.Code+'/',self.grep_v))
					else:
						print 'bash /local/int_jenkins/mtk_patch/lib/updatePjName.sh add %s %s %s'%(self.otherprj[i],self.updatePjName[i],self.Code+'/')
						os.system('bash /local/int_jenkins/mtk_patch/lib/updatePjName.sh add %s %s %s'%(self.otherprj[i],self.updatePjName[i],self.Code+'/'))
			print "end to clone jrd project"
			if 'Nofile' == patchFilename:
				print "No p%s patch. Please copy the correct patch to TODO directory" % patchNo
				sys.exit(1)
			self.patch_type,self.vnum,self.pnum,self.eservice_ID = self.getMtkPatchInfor(patchFilename) 
			self.description = self.getDescriptionFromPatchListFile(self.Code, self.untardir,self.eservice_ID)
			print "description",self.description
			if len(self.devCodeProjectIDList)>0:	        
				self.insertAllImportInfoTO_importSheet(self.devCodeProjectIDList,self.__branch,self.patch_type,self.vnum,self.pnum,self.eservice_ID,self.description,patchtype)
		            
			comment = 'porting P%s_%s' %(patchNo, patchFilename.replace('(', '_').replace(')', '_'))
			tagname = 'porting_mtk_patch_%s' % patchFilename.replace('(', '_').replace(')', '_')
			tagcomment = 'porting mtk patch P%s' % patchNo
			print "commit comment is %s" % comment
			print "tagname is %s" % tagname
			print "tagcomment is %s" % tagcomment
			if True == self.__pushCodeToGit:
				print 'start merge.....'
				gitpushlog = '/tmp/%s_gitpush.log'%self.__branch
				os.system(' > %s' % gitpushlog)
				os.system('%s forall -c git add -A' % self.repopath)
				#os.system('%s forall -c git commit -m "%s"; %s forall -c git push jgs HEAD:refs/heads/%s; %s forall -c git tag -a %s -m "%s";%s forall -c git push jgs %s' % (self.repopath,comment,self.repopath,self.__branch,self.repopath,tagname,tagcomment,self.repopath,tagname))
				print '%s forall -c git commit -m "%s"; %s forall -c git push jgs HEAD:refs/heads/%s | tee -a %s' % (self.repopath,comment,self.repopath,self.__branch,gitpushlog)
				os.system('%s forall -c git commit -m "%s"; %s forall -c git push jgs HEAD:refs/heads/%s | tee -a %s' % (self.repopath,comment,self.repopath,self.__branch,gitpushlog))
				if int(patchNo) % 10 == 0:
					print '%s forall -c git tag -a %s -m "%s";%s forall -c git push jgs %s | tee -a %s' % (self.repopath,tagname,tagcomment,self.repopath,tagname,gitpushlog)
					os.system('%s forall -c git tag -a %s -m "%s";%s forall -c git push jgs %s | tee -a %s' % (self.repopath,tagname,tagcomment,self.repopath,tagname,gitpushlog))
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

    	
	
	def MergePatchToDriveOnly(self,patchNo=-1):
		print "Now start to import for each drive only branch"
		for eachbranch in self.__DriveOnlyBranch:
			DriveOnlyCode = ''
			DriveOnlygitDir = []
			DriveOnlyCode = self.__DriveOnlyCode + eachbranch
			self.repo_code(DriveOnlyCode, eachbranch)
		        #self.reset(DriveOnlyCode)
			DriveOnlygitDir = self.getGitNameOfDir(DriveOnlyCode)
			self.eachDriveOnlyBranchImport(DriveOnlygitDir, DriveOnlyCode,eachbranch, patchNo)
			DriveOnlyCode = ''
		#self.movePatchToMergeDone(patchNo)
		
	def grep_care_branch_files(self):
		pwdcd = os.getcwd()
		print 'change dir ==================>%s\n' % self.__DriveOnlyCode+self.care_driveronly+'/'+self.care_git_folder
		os.chdir(self.__DriveOnlyCode+self.care_driveronly+'/'+self.care_git_folder)
		care_files_str = self.care_files.replace(',','|')
		tmp = getoutput("git log -1 --name-only | grep -E '%s'" % care_files_str)
		if tmp:
			print 'care files detected!!!'
			print tmp
			self.care_str = "git log -1 --name-only and find all these files are modify but these files need to check by bsp :\n" + tmp + "\n Thanks"
			print 'change dir ==================>%s\n' % pwdcd
			os.chdir(pwdcd)
			return True
		print 'change dir ==================>%s\n' % pwdcd
		os.chdir(pwdcd)
		return False
	def sendmail_bsp(self):
		print "detected some conflic need to be solved by bsp"
		print "+++++++++++++++++++++send mai start+++++++++++++++++++++++++"
		mailBody = [self.care_str]
		smtpServer = smtplib.SMTP(u'mail.tcl.com')
		reload(sys)
		sys.setdefaultencoding('gbk')	
		msg = MIMEText(''.join(mailBody), 'html','utf-16')
		msg.set_charset('gb2312')   
		msg['From'] = "xiaodan.cheng@tcl.com"
		msg['Subject'] = "[MTK patch][%s][driveonly branch conflic need to be solved by ersen.shang]" % self.care_driveronly
		msg['To'] = u'ersen.shang@tcl.com'
		msg['Cc'] = u'shie.zhao@tcl.com'
		tolist = [ u'ersen.shang@tcl.com',u"xiaodan.cheng@tcl.com",u'shie.zhao@tcl.com']
		domainAccount = u'xiaodan.cheng'
		domainPassword = "cxd@6235"
		smtpServer.login(domainAccount, domainPassword)
		smtpServer.sendmail(u"xiaodan.cheng@tcl.com", tolist , msg.as_string())
		smtpServer.quit()
		print "+++++++++++++++++++++send mai end+++++++++++++++++++++++++"
		print "exit!!!"
		sys.exit(1)
	def getGitNameOfDir(self, repodir):
		gitDir = []
		projectFile = repodir + "/.repo/project.list"
		print "the project list is %s" % projectFile
		F = getoutput('grep "" "%s"' % projectFile).split('\n')
		for line in F:
		    	if line.strip() not in gitDir:
		    		gitDir.append(line.strip())
		return gitDir

	def eachDriveOnlyBranchImport(self,DriveOnlygitDir, DriveOnlyCode, eachbranch, patchNo=-1):
		if int(patchNo) == -1:
		    	print "Parameter patchNo(%s) is error." % patchNo
		    	return

		if (os.path.exists("/local/mtk_patch_import/start") == True):
		    print "Now start to get drive only code from server"
		    self.reset(DriveOnlyCode)
		    print "patchNo %s" % patchNo
                    if self.download_type == 'git':
                        if True == self.__pushCodeToGit:
		        	print 'start merge to driveronly .......'
				gitpushlog = '/tmp/%s_gitpush.log'%self.__branch
				os.system(' > %s' % gitpushlog)     
                                self.gitMergeToDriveronly(DriveOnlyCode, self.__branch, eachbranch,patchNo,gitpushlog) 
                 
                    else:
		    	patchFilename = self.takePatch(DriveOnlyCode,patchNo,False)
		    	comment = 'porting P%s_%s for driveonly branch' %(patchNo, patchFilename.replace('(', '_').replace(')', '_'))
		    	tagname = 'porting_mtk_patch_%s_for_%s' % (patchFilename.replace('(', '_').replace(')', '_'),eachbranch)
		    	tagcomment = 'porting mtk patch P%s for DOnly' % patchNo
		    	print "commit comment is %s" % comment
		    	print "tagname is %s" % tagname
		    	print "tagcomment is %s" % tagcomment
		    	if True == self.__pushCodeToGit:
		        	print 'start merge.....'
				gitpushlog = '/tmp/%s_gitpush.log'%self.__branch
				os.system(' > %s' % gitpushlog)
				self.takeImportCommitForDriveOnly(DriveOnlyCode, self.__branch, eachbranch,patchNo,DriveOnlygitDir)
				#os.system('%s forall -c git push jgs HEAD:refs/heads/%s; %s forall -c git tag -a %s -m "%s";%s forall -c git push jgs %s' % (self.repopath,eachbranch,self.repopath,tagname,tagcomment,self.repopath,tagname))
				if self.care_driveronly and self.grep_care_branch_files():
					self.sendmail_bsp()
				else:
					os.system('%s forall -c git push jgs HEAD:refs/heads/%s | tee -a %s' % (self.repopath,eachbranch,gitpushlog))
				if int(patchNo) % 20 == 0:
					os.system('%s forall -c git tag -a %s -m "%s";%s forall -c git push jgs %s | tee -a %s' % (self.repopath,tagname,tagcomment,self.repopath,tagname,gitpushlog))
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
	
	
                               
	def rmdatabase(self,codedir,patchNo):
		print "no need to rm data base"

		
	def reset(self, codedir):
		if False == self.debug:     
			print "-----------------------------reset start-----------------------------\n"
			print 'change dir ==================>%s\n' % codedir
            		os.chdir(codedir)
            		#sleep(180)
            		print "reset start... \nClean all, reset to HEAD and repo sync"
            		os.system('rm -rf ./out')

		        if self.download_type == 'git' and codedir == self.Code:
            		    print "-----------------------------update mtk manifest and download code start-----------------------------\n" 
            		    os.system('cd .repo/manifests ; git reset --hard HEAD ; git pull')
            		    os.chdir(codedir)
            		    manifest = codedir + "/.repo/manifests/" + self.mtktag + ".xml"                   
            		    if os.path.exists(manifest) == True:
                                os.system('rm -rf .repo/manifest.xml ; ln -s %s .repo/manifest.xml' %(manifest) )  
                                self.updatemtkcurmanifest(manifest)
                                #os.system('%s sync -f -j8 --no-tag -c ' % self.repopath)
                                os.system('%s sync -f -c --no-tag' % self.repopath)

            		    else:
                                print "can not find %s ,please check" %(manifest) 

                            print "-----------------------------download code end-----------------------------\n"  

                        else:
                            
            		    os.system('%s forall -c "git reset --hard HEAD; git clean -df"' % self.repopath)
                            if codedir == self.Code :
                                os.system('%s sync -j4 -c --no-tag' % self.repopath)
                            else:
            		        os.system('%s sync -j4 --no-tag' % self.repopath)
            		print "-----------------------------reset done-----------------------------\n"

    	

    	
	def checkcompile(self,buildstatus,branchname=''):
		if buildstatus >> 8 == 0 and os.path.exists(r"/local/mtk_patch_import/%s/out/target/product/%s"  % (branchname,self.lunchproj)):
			print 'change dir ==================>/local/mtk_patch_import/%s/out/target/product/%s\n' % (branchname,self.lunchproj)
			os.chdir(r'/local/mtk_patch_import/%s/out/target/product/%s'  % (branchname,self.lunchproj))
			if (os.path.exists('system.img') and os.path.exists('userdata.img') and os.path.exists('recovery.img')):
				return 'Success'
			else:
				return 'Fail'
		else:
			return 'Fail'
	
    	def justBuild(self):
        	print "Just to build now"
        	print "Repo sync latest import code"
                if self.download_type == 'git':
                    branch = "JRD_" + self.__branch
                    codepath = "/local/mtk_patch_import/" + branch                    
                else:
                    codepath = self.Code   
                    branch = self.__branch
        	self.repo_code(codepath, branch)
        	self.reset(codepath)
 
        	if 'Fail' == self._compile(codepath,self.__branch):
			print "Build Failed"
			sys.exit(1)
		os.system("touch /local/release/%s_justBuild.txt" % self.proj)

	def DriveOnlyBranchBuild(self, patchNo):
		print "Now start to build driveonly branch"
		print "Repo sync latest driveonly code"
		for eachbranch in self.__DriveOnlyBranch:
			DriveOnlyCode = ''
			DriveOnlyCode = self.__DriveOnlyCode + eachbranch
			self.repo_code(DriveOnlyCode, eachbranch)
			self.reset(DriveOnlyCode)
			if 'Fail' == self._compile(DriveOnlyCode, eachbranch):
				print "Driveonli branch Build Failed"
				sys.exit(1)
			os.system("touch /local/release/%s_%s_DriveOnlyBranchBuild.txt" % (eachbranch,self.proj))
			self.uploadBinToTeleweb(DriveOnlyCode, eachbranch, patchNo)
			DriveOnlyCode = ''

    	def uploadBinToTeleweb(self, DriveOnlyCode, eachbranch, patchNo):
		print "Now start to upload"
		print 'change dir ==================>%s\n' % DriveOnlyCode
		os.chdir(DriveOnlyCode)
        	if '' == patchNo:
            		print "patchNo is none"
            		sys.exit(1)
		version_num="P%s-%s" % (patchNo, eachbranch)
		#os.system('/local/int_jenkins/sortresult/projects/Driveronly_CopyImg.sh %s %s %s '%(eachbranch, version_num, self.lunchproj))
		driveonly_release_dir = r'/local/release/%s' % eachbranch
        	if not os.path.isdir(driveonly_release_dir+'/v'+version_num):
            		os.system('mkdir -p %s' % driveonly_release_dir+'/v'+version_num)
		if not os.path.isdir(DriveOnlyCode + '/out/target/product/' + self.lunchproj):
			print 'such dir not exist: ',DriveOnlyCode + '/out/target/product/' + self.lunchproj
			print 'please check it!'
			sys.exit(1)
		print 'change dir ==================>%s\n' % DriveOnlyCode + '/out/target/product/' + self.lunchproj
		os.chdir(DriveOnlyCode + '/out/target/product/' + self.lunchproj)	
		tmpstrs=getoutput('ls | grep -E ".bin|.img|_scatter.txt|MBR|EBR1|EBR2|previous_build_config.mk"').split('\n')
		print 'tmpstr',tmpstrs
		if tmpstrs:
			for tmpstr in tmpstrs:
				print 'cp -f %s %s'%(tmpstr,driveonly_release_dir+'/v'+version_num)
				os.system('cp -f %s %s'%(tmpstr,driveonly_release_dir+'/v'+version_num))
		modem_dir = getoutput("grep modem %s/.repo/project.list" % DriveOnlyCode).split('\n')[-1]
		print 'modem_dir',modem_dir
		if modem_dir and os.path.isdir(DriveOnlyCode+'/'+modem_dir+'/.git'):
			if os.path.isdir(DriveOnlyCode+'/'+modem_dir+'/mcu'):
				tmpstrs=''
				tmpstrs=getoutput('find %s -name *.EDB -o -name *.check -o -name DbgInfo_DSP*'%(DriveOnlyCode+'/out')).split('\n')
				print 'tmpsts',tmpstrs
				if tmpstrs:
					for tmpstr in tmpstrs:
						os.system('cp -f %s %s'%(tmpstr,driveonly_release_dir+'/v'+version_num))
			elif os.path.isdir(DriveOnlyCode+'/'+modem_dir):
				tmpstrs=''
				tmpstrs=getoutput('find %s -name BPLGUInfoCustomApp* -o -name DbgInfo_* -o -name BPMdMetaDataBase*'%(DriveOnlyCode+'/out')).split('\n')
				print 'tmpsts',tmpstrs
				if tmpstrs:
					for tmpstr in tmpstrs:
						os.system('cp -f %s %s'%(tmpstr,driveonly_release_dir+'/v'+version_num))
			else:
				print "DriveOnlyCode+'/'+modem_dir====",DriveOnlyCode+'/'+modem_dir
				print "ERROR!!!"
				sys.exit(1)
		else:
			print "modem_dir,DriveOnlyCode+'/'+modem_dir+'/.git'",modem_dir,DriveOnlyCode+'/'+modem_dir+'/.git'
			print "ERROR!!!"
			sys.exit(1)
		print "begin to upload result to teleweb"
		print 'change dir ==================>%s\n' % driveonly_release_dir
		os.chdir(driveonly_release_dir)
		print 'scp -r v%s sl_hz_hran@10.92.32.26:/mfs/teleweb/%s/driveonly/' % (version_num,self.branchDict[eachbranch])
		os.system('scp -r v%s sl_hz_hran@10.92.32.26:/mfs/teleweb/%s/driveonly/' % (version_num,self.branchDict[eachbranch]))
		print "finish upload"
	def rmbuild(self):
		self.rmbuildfile(self.Code)
	def rmdriveonlybuild(self):
		for eachbranch in self.__DriveOnlyBranch:
			DriveOnlyCode = self.__DriveOnlyCode + eachbranch
			self.rmbuildfile(DriveOnlyCode)	

if __name__ == "__main__":
	print "test for argv"
	print sys.argv
	conf = Config()
	conf.addFromArg(sys.argv[1:])
	patchtype = conf.getConf('patchtype','patch type','critical')
	patchnum = conf.getConf('patchnum','patch number',-1)#sys.argv[3]
	operation = conf.getConf('operation','operation','')
	pm = PatchMerge(conf)
	print '====================begin of %s====================\n' % operation
	if operation == 'MergePatch':
		pm.MergePatch(patchtype,patchnum)
	elif operation == 'MergePatchToDriveOnly':  
		pm.MergePatchToDriveOnly(patchnum)
	elif operation == 'build':
		pm.justBuild()
	elif operation == 'DriveOnlybuild':
		pm.DriveOnlyBranchBuild(patchnum)
	elif operation == 'rmbuild':
		pm.rmbuild()
	elif operation == 'rmdriveonlybuild':
		pm.rmdriveonlybuild()
	else:
		print "ERROR eccour in operation!"
	print '====================end of %s====================\n' % operation
