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


class PatchMerge(CheckFile,dotProjectDb,checkPatchInfor):
    def __init__(self,basedir='/local'):
	self.repopath = '/local/tools/repo/repo'
        os.chdir(basedir)
        self.__baseDir = os.getcwd()		
        self.__debug = False
        self.__pushCodeToGit = True
        wb = xlrd.open_workbook('%s/mtk6737_53_n-jb3-mp-import.xls' % getoutput("dirname %s" % (sys.argv[0])))
        mtkSheet = wb.sheet_by_name(u'MTKInfo')
        self.__branch = mtkSheet.cell(1, 0).value.strip()
        self.__project = mtkSheet.cell(1, 1).value.strip()
        self.__patchFormat = mtkSheet.cell(1, 2).value.strip()
        self.__mailServer = mtkSheet.cell(1, 3).value.strip()
        self.__mailTitle = mtkSheet.cell(1, 4).value.strip()
        self.__mailAccount = mtkSheet.cell(1, 5).value.strip()
        self.__mailSender = mtkSheet.cell(1, 6).value.strip()
        self.__mailToList = mtkSheet.cell(1, 7).value.strip().split(',')
        self.__mailccList = mtkSheet.cell(1, 8).value.strip().split(',')
        self.__SPMList = mtkSheet.cell(1, 9).value.strip().split(',')
        self.__DriveOnlyBranchName = mtkSheet.cell(1, 10).value.strip().split(',')
        self.__TelewebDirName = mtkSheet.cell(1, 11).value.strip().split(',')
        self.__importCode = "/" + "local" + "/mtk_patch_import" +  "/" + self.__branch
        self.__DriveOnlyCode = "/" + "local" + "/mtk_patch_import" +  "/"
        self.__mergeDone = "/" + "local" + "/mtk_patch_import" + "/mergeDone"
        self.__ignorePatch = "/" + "local" + "/mtk_patch_import" + "/ignorePatch"
        self.__ongoingPatch = "/" + "local" + "/mtk_patch_import" + "/TODO"
        self.__mailDir = "/" + "local" + "/mtk_patch_import" + "/Mail"
	self.__start = "/" + "local" + "/mtk_patch_import" + "/start"
	self.branchDict = {}
	self.checkFileDict = self.getAffectFileDict()
	self.projectList = self.checkProjectName()
	self.devCodeBranch = []
	self.devCodeProjectIDList = []
	self.SPMIDList = []
	self.SPMEmailList = []
	self.importIdDict = {}
	self.projectid_codeBranch_Dict = {}
	self.patch_type = ''
	self.vnum = ''
	self.pnum = ''
	self.eservice_ID = ''
	self.description = ''
	self.untardir = ''
	self.get_db_connection()
	self.devCodeProjectIDList = self.getProjectIDFromImportBranch(self.__branch)
	print self.devCodeProjectIDList
	self.SPMIDList = self.getContactIDList(self.devCodeProjectIDList)
	print "self.SPMIDList",self.SPMIDList
	self.SPMEmailList = self.getSpmEmailList(self.SPMIDList)
	print "self.SPMEmailList",self.SPMEmailList
	self.devCodeBranch = self.getDevBranchNameFromIProjectID(self.devCodeProjectIDList,self.projectid_codeBranch_Dict)
	if len(self.__DriveOnlyBranchName) == len(self.__TelewebDirName):
		for item in range(len(self.__DriveOnlyBranchName)):
			self.branchDict[self.__DriveOnlyBranchName[item]] = self.__TelewebDirName[item]
			print "the diff dirveonly branch need upto diff teleweb dir"
			print self.branchDict

        if not os.path.isdir(self.__start):
            os.system('mkdir -p %s' % self.__start)

        print "baseDir = %s\nbranch = %s\nproject = %s\npatchFormat = %s\nmailServer = %s\nmailTitle = %s\nmailAccount = %s\nmailSender = %s\nongoingPatch = %s\nDriveOnlyBranchName = %s" % (self.__baseDir,self.__branch, self.__project, self.__patchFormat, self.__mailServer, self.__mailTitle, self.__mailAccount,self.__mailSender, self.__ongoingPatch, self.__DriveOnlyBranchName)
        print "mailToList = %s\nmailccList = %s\nSPMList = %s\n" % (self.__mailToList, self.__mailccList, self.__SPMList)
		
    def MergePatch(self):
        print "Please create file(start) on /local/mtk_patch_import directory. If not exist, the script will stop and exit."  
        while (os.path.exists("/" + "local" + "/mtk_patch_import" + "/start") == True):
            print "Now start to get import code from server"
            self.__reset(self.__importCode)
            patchNo = self.__getNextPatchNo()
            print "getNextPatchNo %s" % patchNo
            patchFilename = self.__takePatch(self.__importCode, patchNo)
            if 'Nofile' == getNextPatchNo:
                print "Wait next patch, patchNo = %s" % patchNo
                continue
            prevMD5 = getoutput('rm -rf /tmp/tempfile; %s forall -c "git add .; git status" >> /tmp/tempfile; md5sum /tmp/tempfile' % self.repopath).split()[0]
            if sys.argv[5].lower() == "yes" and 'Success' == self.__compile(self.__importCode,self.__branch):
                print "Compile success"
                self.__reset(self.__importCode)
                patchFilename = self.__takePatch(self.__importCode, patchNo)
                comment = 'porting P%s_%s' %(patchNo, patchFilename.replace('(', '_').replace(')', '_'))
                print comment
                if True == self.__pushCodeToGit:
                    print 'start merge.....'
                    os.system('%s forall -c git add .' % self.repopath)
                    nextMD5 = getoutput('rm -rf /tmp/tempfile; %s forall -c "git status" >> /tmp/tempfile; md5sum /tmp/tempfile' % self.repopath).split()[0]
                    if prevMD5 == nextMD5:
                        os.system('%s forall -c git commit -m "%s"; %s forall -c git push jgs HEAD:refs/heads/%s' % (self.repopath,comment,self.repopath,self.__branch))
                        self.__movePatchToMergeDone(patchNo)
                    print 'finish merge....'
            elif sys.argv[5].lower() == "no":
		print "You choice not to build the project"
                comment = 'porting P%s_%s' %(patchNo, patchFilename.replace('(', '_').replace(')', '_'))
                print comment
                if True == self.__pushCodeToGit:
                    print 'start merge.....'
                    os.system('%s forall -c git add .' % self.repopath)
                    os.system('%s forall -c git commit -m "%s"; %s forall -c git push jgs HEAD:refs/heads/%s' % (self.repopath,comment,self.repopath,self.__branch))
                    self.__movePatchToMergeDone(patchNo)
            else:
                print "Compile failed"
                mailBody = []
                mailBody.append('Compile Error: patchNo = %s' % patchNo)
                self.__sendMail(patchNo, mailBody)
    
    def MergeOnePatch(self,patchtype,patchNo=-1):
        print "Now start to repo code"
        self.RepoCode(self.__importCode, self.__branch)
        print "Please create file(start) on /local/mtk_patch_import directory. If not exist, the script will stop and exit."
        '''parameter patchNo is 0,1,2,3...'''
        if int(patchNo) == -1:
            print "Parameter patchNo(%s) is error." % patchNo
            return
        if (os.path.exists("/" + "local" + "/mtk_patch_import"+"/start") == True):
            print "Now start to get import code from server"
            self.__reset(self.__importCode)
            print "patchNo %s" % patchNo
            patchFilename = self.__takePatch(self.__importCode, patchNo)
            print "begin to clone jrd project"
            os.system('bash /local/int_jenkins/mtk_patch/lib/updatePjName.sh add jhz6737m_35_n mickey6t /local/mtk_patch_import/mtk6737_53-n-v1.0-import/')
            os.system('bash /local/int_jenkins/mtk_patch/lib/updatePjName.sh add jhz6753_66_n simba6l /local/mtk_patch_import/mtk6737_53-n-v1.0-import/')
            os.system('bash /local/int_jenkins/mtk_patch/lib/updatePjName.sh add jhz6737m_35_n buzz6e /local/mtk_patch_import/mtk6737_53-n-v1.0-import/')
            os.system('bash /local/int_jenkins/mtk_patch/lib/updatePjName.sh add jhz6737m_35_n buzz6t_orange /local/mtk_patch_import/mtk6737_53-n-v1.0-import/')
            os.system('bash /local/int_jenkins/mtk_patch/lib/updatePjName.sh add jhz6737m_35_n mickey6t_gmo /local/mtk_patch_import/mtk6737_53-n-v1.0-import/')
            print "end to clone jrd project"
            if 'Nofile' == patchFilename:
                print "No p%s patch. Please copy the correct patch to TODO directory" % patchNo
                sys.exit(1)

            self.patch_type,self.vnum,self.pnum,self.eservice_ID = self.getMtkPatchInfor(patchFilename) 
            self.description = self.getDescriptionFromPatchListFile(self.__importCode, self.untardir,self.eservice_ID)
            print "description",self.description	        
            self.insertAllImportInfoTO_importSheet(self.devCodeProjectIDList,self.__branch,self.patch_type,self.vnum,self.pnum,self.eservice_ID,self.description,patchtype)
                    
            comment = 'porting P%s_%s' %(patchNo, patchFilename.replace('(', '_').replace(')', '_'))
            tagname = 'porting_mtk_patch_%s' % patchFilename.replace('(', '_').replace(')', '_')
            tagcomment = 'porting mtk patch P%s' % patchNo
            print "commit comment is %s" % comment
            print "tagname is %s" % tagname
            print "tagcomment is %s" % tagcomment
            if True == self.__pushCodeToGit:
		print 'start merge.....'
		os.system('%s forall -c git add -A' % self.repopath)
		#os.system('%s forall -c git commit -m "%s"; %s forall -c git push jgs HEAD:refs/heads/%s; %s forall -c git tag -a %s -m "%s";%s forall -c git push jgs %s' % (self.repopath,comment,self.repopath,self.__branch,self.repopath,tagname,tagcomment,self.repopath,tagname))
		os.system('%s forall -c git commit -m "%s"; %s forall -c git push jgs HEAD:refs/heads/%s' % (self.repopath,comment,self.repopath,self.__branch))
		if int(patchNo) % 10 == 0:
			os.system('%s forall -c git tag -a %s -m "%s";%s forall -c git push jgs %s' % (self.repopath,tagname,tagcomment,self.repopath,tagname))
		print 'finish merge....'


    def RepoCode(self, CodeDir, BranchName):
        print "Now checking the code if exist,"
        if not os.path.isdir(CodeDir):
            os.system('mkdir -p %s' % CodeDir)
	print "change dir =========>",CodeDir
        os.chdir(CodeDir)
        if os.path.exists(CodeDir + "/.repo") == False:  
            repoinit = pexpect.spawn('%s init -u git@10.92.32.10:alps/manifest -m %s.xml' % (self.repopath, BranchName))
            repoinit.expect('Your\s+Name.*')
            repoinit.sendline()
            repoinit.expect('Your\s+Email.*')
            repoinit.sendline()
            repoinit.expect('is this.*')
            repoinit.sendline('yes')
	
    def MergeOnePatchForDriveOnly(self,patchNo=-1):
        print "Now start to import for each drive only branch"
	for eachbranch in self.__DriveOnlyBranchName:
		DriveOnlyCode = ''
		DriveOnlygitDir = []
		DriveOnlyCode = self.__DriveOnlyCode + eachbranch
		self.RepoCode(DriveOnlyCode, eachbranch)
                self.__reset(DriveOnlyCode)
		DriveOnlygitDir = self.getGitNameOfDir(DriveOnlyCode)
		self.eachDriveOnlyBranchImport(DriveOnlygitDir, DriveOnlyCode,eachbranch, patchNo)
		DriveOnlyCode = ''
	#self.__movePatchToMergeDone(patchNo)


    def getGitNameOfDir(self, repodir):
	gitDir = []
        projectFile = repodir + "/.repo/project.list"
        print "the project list is %s" % projectFile
        F = open(projectFile,'r')
        for line in F:
            if line.strip() not in gitDir:
            	gitDir.append(line.strip())
	return gitDir

    def eachDriveOnlyBranchImport(self,DriveOnlygitDir, DriveOnlyCode, eachbranch, patchNo=-1):
        if int(patchNo) == -1:
            print "Parameter patchNo(%s) is error." % patchNo
            return

        if (os.path.exists("/" + "local" + "/mtk_patch_import"+"/start") == True):
            print "Now start to get drive only code from server"
            self.__reset(DriveOnlyCode)
            print "patchNo %s" % patchNo
            patchFilename = self.__takePatchForDriveOnly(patchNo)
            comment = 'porting P%s_%s for driveonly branch' %(patchNo, patchFilename.replace('(', '_').replace(')', '_'))
            tagname = 'porting_mtk_patch_%s_for_%s' % (patchFilename.replace('(', '_').replace(')', '_'),eachbranch)
            tagcomment = 'porting mtk patch P%s for DOnly' % patchNo
            print "commit comment is %s" % comment
            print "tagname is %s" % tagname
            print "tagcomment is %s" % tagcomment
            if True == self.__pushCodeToGit:
                print 'start merge.....'
		self.__takeImportCommitForDriveOnly(DriveOnlygitDir, DriveOnlyCode, self.__branch, eachbranch,patchNo)
		#os.system('%s forall -c git push jgs HEAD:refs/heads/%s; %s forall -c git tag -a %s -m "%s";%s forall -c git push jgs %s' % (self.repopath,eachbranch,self.repopath,tagname,tagcomment,self.repopath,tagname))
		os.system('%s forall -c git push jgs HEAD:refs/heads/%s' % (self.repopath,eachbranch))
		if int(patchNo) % 10 == 0:
			os.system('%s forall -c git tag -a %s -m "%s";%s forall -c git push jgs %s' % (self.repopath,tagname,tagcomment,self.repopath,tagname))
                print 'finish merge....'
	
    def makePatchMail(self,patchNo=-1):
        '''parameter patchNo is 0,1,2,3...'''
        if int(patchNo) == -1:
            print "Parameter patchNo(%s) is error." % patchNo
            return
        if not os.path.isdir(self.__mailDir):
            os.system('mkdir -p %s' % self.__mailDir)
	print self.__ongoingPatch, self.__patchFormat, patchNo
        patchFilename = getoutput("ls %s | grep %s | grep _P%s\).tar.gz" % (self.__ongoingPatch, self.__patchFormat, patchNo))
	print 'patchFilename',patchFilename
        self.patch_type,self.vnum,self.pnum,self.eservice_ID = self.getMtkPatchInfor(patchFilename) 
        os.chdir(self.__importCode)
        #Please don't add 'repo sync' action here, it will affect merge work.
        patchList = getoutput('%s forall -c \'git log jgs/%s --format=%s\' | grep "%s" | grep "porting P%s_" | sort' %(self.repopath,self.__branch, '%s^^^^^^%H^^^^^^$PWD', self.__patchFormat, patchNo)).split('\n')
        for item in range(len(patchList)):
            itemInfo = patchList[item].split('^^^^^^')
            if 3 != len(itemInfo):
                print "patchList have problems. patchList = %s" % patchList
		print "The pacth has no modification"
                sys.exit(1)

        bugInfo = self.__getBugzillaInfo(patchList[0].split('^^^^^^')[0])
        mailBody = []
        dearName = sys.argv[4].split('@')[0]
        if bugInfo['patchID'] == 'JRD':
            mailBody.append('<p align=\'Left\'><b>Dear %s,</b></p>' % dearName)
            mailBody.append('<p align=\'Left\'>MTK6737_53_N Platform Mickey6T/Buzz6E/SIMBA6L defect %s(<a href="%s">%s </a>)</p>' %(bugInfo['bugID'], bugInfo['bugLink'], bugInfo['bugLink']))

        if bugInfo['patchID'] == 'ALPS':
            mailBody.append('<p align=\'Left\'><b>Dear %s,</b></p>' % dearName)
            mailBody.append('<p align=\'Left\'>MTK6737 Platform Mickey6T/Buzz6E/SIMBA6L Patch %s<br/></p>' %bugInfo['bugID'])
        self.getEmailContent(mailBody,patchNo,bugInfo,patchList)
	mailtitle = '%s P%s Patch merge' %(self.__mailTitle, patchNo)                           
        print 'self.importIdDict',self.importIdDict
        print 'self.projectid_codeBranch_Dict',self.projectid_codeBranch_Dict	
        for projectID1 in self.importIdDict.keys():
		for projectID2 in self.projectid_codeBranch_Dict.keys():
			if projectID1 == projectID2:
				self.insertImportId_And_DevBranch_To_dotp_mtk_merge(self.importIdDict[projectID1],self.projectid_codeBranch_Dict[projectID2],sys.argv[4])			             
        #os.system('python /local/int_jenkins/mtk_patch/lib/insertdbToWr.py %s %s %s %s' % (self.__branch,self.vnum,self.pnum,self.eservice_ID) )
        os.system('python /local/int_jenkins/mtk_patch/lib/insertInforToManpower.py %s %s %s %s %s' % (self.__branch,self.vnum,self.pnum,self.eservice_ID,sys.argv[6]) )			             
        self.__sendMail(patchNo, mailtitle, mailBody, [bugInfo['assigned']])
                               
    def getEmailContent(self,mailBody,patchNo,bugInfo,patchList):
        #mailBody.append('<p align=\'Left\'>Summary: </p>')
        mailBody.append('<p align=\'Left\'>MTK Patch <b><font color="#FF0000">P%s</font></b> has been merged to import branch(%s)<br/></p>' % (patchNo,self.__branch))
        mailBody.append('<p align=\'Left\'><b>Please help to merge patch to below branch:</b></p>')
        for eachCodeBranchName in self.devCodeBranch:
            mailBody.append('<p align=\'Left\'><b><font color="#FF0000">%s</font></b></p>' % eachCodeBranchName)
        mailBody.append('<p align=\'Left\'><font color="#FF0000">Please kindly give a feedback in 24h.</b></font><br/></p>')
        mailBody.append('<p align=\'Left\'>Note: When commit MTK related patch, please follow below comment.</p>')
        mailBody.append('<p align=\'Left\'><font color="#FF0000">The comment same as: %s</b></font><br/></p>' % bugInfo['comment'])
        mailBody.append('<p align=\'Left\'>Patch Link in import branch:</p>')
        for item in range(len(patchList)):
            itemInfo = patchList[item].split('^^^^^^')
            gitName = itemInfo[2].split(self.__branch)[1]
            match = re.match("^/(.*)",gitName)
            gitName = match.group(1)
            gitNamefilder = gitName
            if gitName == "kernel-3.18":
                gitName = 'kernel'	
            gitLink = 'http://10.92.32.10/sdd2/gitweb-mtk6753/?p=%s.git;a=commit;h=%s' % (gitName, itemInfo[1])
            self.insertImportCommitInfoTO_dotp_mtk_commit(self.importIdDict,self.devCodeProjectIDList,self.__branch,self.patch_type,self.vnum,self.pnum,self.eservice_ID,itemInfo[1],gitLink,gitNamefilder)
            mailBody.append('<p align=\'Left\'>%s) %s<br/></p><p align=\'Left\'><a href="%s">%s</a></p>' % (item+1,gitName,gitLink,gitLink))
            gitnameDir = self.__importCode + "/"+ gitNamefilder
            for keyname in self.checkFileDict.keys():
                filename = self.checkFileDict[keyname]['filename']
                if self.checkFileDict[keyname]['gitname'] == gitName:
			if True == self.getFileLibNvram(gitnameDir,filename):
				mailBody.append('<p align=\'Left\'><font color="#FF0000"><b>Note: The file of %s has been changed in patch P%s.</font></b></p>' % (filename,patchNo))
				mailBody.append('<p align=\'Left\'><font color="#FF0000"><b>Please contact System team to check whether to merge this modification to project code</font></b></p>')
				mailBody.append('<br/>')  
            projectnamestr = '' 
            for projectname in self.projectList:
		if True == self.getFileLibNvram(gitnameDir,projectname):
			projectnamestr = projectname + ',' + projectnamestr
			projectnamestr = projectnamestr.strip(',')
            if projectnamestr:
            	project_str = u'请将以上链接中' + projectnamestr + u'文件夹的修改merge到项目对应的文件夹中'
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
        a = u"\\\\10.92.32.12\\RDhzKM\\SWD-Share\\INT\\MTKPatch\\mtk6737_53_n"
        mailBody.append('<p align=\'Left\'><b>You can also find this patch (P%s) in:<font color="#FF0000">%s</font></b></p>' % (patchNo, a))
        mailBody.append('<p align=\'Left\'><b>After you complete to merge the MTK6737 Buzz6t-4G&Buzz6t-4G Orange patch P%s,</b></p>' % patchNo)
        mailBody.append('<p align=\'Left\'><b>please make sure the related issues of this MTK Patch you merged are fixed, and</b></p>')
        mailBody.append('<p align=\'Left\'><font color="#FF0000"><b>please send a remind email to us!!!</b></font></p>') 



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
	allDriveOnlyBranch = ','.join(self.__DriveOnlyBranchName)
        mailBody.append('<p align=\'Left\'>MTK Patch <b><font color="#FF0000">P%s</font></b> has been merged to driveonly branch(%s)<br/></p>' % (patchNo, allDriveOnlyBranch))
        mailBody.append('<p align=\'Left\'>You can check the merge result.</b></p>')
	mailBody = self.getPatchLink(mailBody,patchNo)
	a = u"\\\\10.92.32.12\\RDhzKM\\SWD-Share\\INT\\MTKPatch\\mtk6737_53_n"
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
	allDriveOnlyBranch = ','.join(self.__DriveOnlyBranchName)
        mailBody.append('<p align=\'Left\'>MTK Patch <b><font color="#FF0000">P%s</font></b> has been merged to driveonly branch(%s)<br/></p>' % (patchNo, allDriveOnlyBranch))
        mailBody.append('<p align=\'Left\'>It has been built and been uploaded to teleweb.</b></p>')
        mailBody.append('<p align=\'Left\'>Build eng version, mtk project: %s.</b></p>' % self.__project )
	for eachbranch in self.__DriveOnlyBranchName:
		DriveOnlyCode = ''
		DriveOnlyCode = self.__DriveOnlyCode + eachbranch
        	mailBody.append('<p align=\'Left\'>You can find %s bins at teleweb:<b><font color="#FF0000">%s/driveonly/P%s_%s</font></b></p>' % (self.branchDict[eachbranch],self.branchDict[eachbranch], patchNo,eachbranch))
	mailBody = self.getPatchLink(mailBody,patchNo)
	mailtitle = '%s P%s Patch driveonly branch build done' %(self.__mailTitle, patchNo)
        self.__sendMail(patchNo, mailtitle, mailBody, '')


    def getPatchLink(self, mailBody, patchNo=-1):
	for eachbranch in self.__DriveOnlyBranchName:
		DriveOnlyCode = ''
		DriveOnlyCode = self.__DriveOnlyCode + eachbranch
        	os.chdir(DriveOnlyCode)
        	patchList = getoutput('%s forall -c \'git log jgs/%s --format=%s\' | grep "%s" | grep "porting P%s_" | sort' %(self.repopath,eachbranch, '%s^^^^^^%H^^^^^^$PWD', self.__patchFormat, patchNo)).split('\n')
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
                	if gitName == "kernel-3.18":
                    		gitName = 'kernel'				
                	gitLink = 'http://10.92.32.10/sdd2/gitweb-mtk6753/?p=%s.git;a=commit;h=%s' % (gitName, itemInfo[1])
                	mailBody.append('<p align=\'Left\'>%s) %s</p><p align=\'Left\'><a href="%s">%s</a></p>' % (item+1,gitName,gitLink,gitLink))
	return mailBody
		
    def __reset(self, codedir):
        if False == self.__debug:
            print "change dir ==========>",codedir
            os.chdir(codedir)
            sleep(120)
            print "reset start... \nClean all, reset to HEAD and repo sync"
            os.system('rm -rf ./out')
            os.system('%s forall -c "git reset --hard HEAD; git clean -df"' % self.repopath)
            os.system('%s sync' % self.repopath)
            print "reset done"

    def __getNextPatchNo(self):
        PatchNo = 0
        os.chdir(self.__importCode)
        patchList = getoutput('%s forall -c "git log jgs/%s --format=%s | grep %s"' %(self.repopath, self.__branch, '%s', self.__patchFormat)).split('\n')
        for item in patchList: 
            match = re.match(r'porting P(\d+).+', item)
            if match:
                tmpNo = match.group(1)
            else:
                continue
            
            if int(tmpNo) > int(PatchNo):
                PatchNo = tmpNo
        return int(PatchNo) + 1

    def __takePatch(self, codedir, patchNo=''):
        if '' == patchNo:
            print "patchNo is none"
            sys.exit(1)
        patchFilename = getoutput("ls %s | grep %s | grep _P%s\).tar.gz" % (self.__ongoingPatch, self.__patchFormat, patchNo))
        if 0 == len(patchFilename):
            return "Nofile"
        self.untardir = "%s/P%s" % (self.__ongoingPatch,patchNo)
        os.system('mkdir -p %s' % self.untardir)
        os.system('tar zxvf "%s/%s" -C %s' % (self.__ongoingPatch,patchFilename,self.untardir))
        if not os.path.isdir(codedir):
            os.system('mkdir -p %s' % codedir)

        self.deletefile(codedir, self.untardir)
        os.system('cp -dpRv %s/alps/* %s' %(self.untardir,codedir))
        #os.system('rm -rf %s' % untardir)		
        return patchFilename


    def deletefile(self, codedir, untardir):
        os.chdir(untardir)
        patchlistFilename = commands.getstatusoutput('ls | grep *.txt')	
        if patchlistFilename[0] == 0:
            gitconf = untardir + "/" + patchlistFilename[1]
            f = open(gitconf,'r')	
            os.chdir(codedir)
            for line in f:
            	match = re.search("^delete ",line)		
            	if match:
			line = line.replace("delete ",'')
			line = line.strip()
			print "the delete file is %s" % line	
			os.system('chmod -R 777 %s' % line)	
			deleteResult = commands.getstatusoutput('rm -rf %s' % line)
			if deleteResult[0] != 0:
				print "delete file %s failed" % line
				print "Please check why the file %s cannot be deleted" % line
				sys.exit(1)
			else:
				print "delete file %s successfully" % line

    def __takePatchForDriveOnly(self, patchNo=''):
        if '' == patchNo:
            print "patchNo is none"
            sys.exit(1)
        patchFilename = getoutput("ls %s | grep %s | grep _P%s\).tar.gz" % (self.__ongoingPatch, self.__patchFormat, patchNo))
        if 0 == len(patchFilename):
            return "Nofile"		
        return patchFilename


    def __takeImportCommitForDriveOnly(self, DriveOnlygitDir, codedir, branch, driveonlyBranch, patchNo=''):
        if '' == patchNo:
            print "patchNo is none"
            sys.exit(1)

        if not os.path.isdir(codedir):
            print "The driveonly code download failed"
            sys.exit(1)
	
	for folder in DriveOnlygitDir:
		gitDir = ''
		gitDir = codedir + "/" + folder
		os.chdir(gitDir)
		patchList = getoutput('git log jgs/%s --format=%s | grep "%s" | grep "porting P%s_" | sort' %(branch, '%s^^^^^^%H^^^^^^$PWD', self.__patchFormat, patchNo)).split('\n')
		if "fatal: ambiguous argument" in patchList[0]:
			continue
		if len(patchList) != 0:
			for item in range(len(patchList)):
				if patchList[item] == '':
					continue
				itemInfo = patchList[item].split('^^^^^^')
				if len(itemInfo) == 0:
					continue
				gitName = itemInfo[2].split(driveonlyBranch)[1]
				match = re.match("^/(.*)",gitName)
                		gitName = match.group(1)
				print "the gitname is %s" % gitName
				if gitName == folder:
					print "itemInfo[1]",itemInfo[1]
					cerryPickInfo = getoutput('git cherry-pick %s' % itemInfo[1])		
					if "error:" in cerryPickInfo:
						print "cherry pick failed"
						print "you have to check conflicts"
						sys.exit(1)
					else:
						print "cherry pick successfully"

    def __compile(self, CodeDir, branchname):		
        space = getoutput('df -h /local/ | awk \'{print $4}\'').split('\n')[1][:-1]
        if (space < 20):
            print "**Error: there is no enough space left on device!"
            return "Fail"
        os.chdir(CodeDir)
        print "building......"
        if False == self.__debug:
            os.chdir(CodeDir+'/modem')
            os.system('python compile_modem.py -p mickey6t -b US_2S')
            os.chdir(CodeDir)
            status = os.system('source build/envsetup.sh && lunch full_mickey6t-eng && make -j24 2>&1 |tee android.log')
            print "status is %s" % status            
            if os.path.exists(r"/local/mtk_patch_import/%s/out/target/product/mickey6t"  % branchname):
                os.chdir(r'/local/mtk_patch_import/%s/out/target/product/mickey6t'  % branchname)
                if (os.path.exists('system.img') and os.path.exists('userdata.img') and os.path.exists('recovery.img')):
					return 'Success'
                else:
					return 'Fail'
            else:
				return 'Fail'

        else:
            buildInfo = raw_input('[Debug mode] Please input compile result Info "==> [FAIL]" or "other string":') 
            if buildInfo.find("==> [FAIL]") >= 0:
                return "Fail"
            return 'Success'
	
    def __movePatchToMergeDone(self, patchNo):
        os.system('mkdir -p %s' % self.__mergeDone)
        os.system('mv %s/*%s*_P%s\).tar.gz %s' % (self.__ongoingPatch,self.__patchFormat,patchNo,self.__mergeDone))

    def __sendMail(self,patchNo, mailtitle, mailBody=[], to=[]):
        '''parameter toList: the PR owner(assigned) or interface or leader'''
        smtpServer = smtplib.SMTP(self.__mailServer)
	reload(sys)
	print sys.setdefaultencoding('gbk')	
        msg = MIMEText(''.join(mailBody), 'html','utf-16')
        msg.set_charset('gb2312')   
        msg['From'] = self.__mailSender
        msg['Subject'] = mailtitle
        #msg['Subject'] = '%s P%s Patch Merge' %(self.__mailTitle, patchNo)
        domainAccount = self.__mailAccount
        domainPassword = "Hzsw#123"
        smtpServer.login(self.__mailAccount, domainPassword)
        sendTo = "all"
        if sendTo == "self":
            msg['To'] = self.__mailSender
            smtpServer.sendmail(self.__mailSender, self.__mailSender , msg.as_string())
        elif sendTo == "all":
            if len(sys.argv) == 7 and sys.argv[5] == "true":		
            	msg['To'] = ','.join(list(set(self.SPMEmailList + [sys.argv[4]])))
            	msg['Cc'] = ','.join(list(set(self.__mailToList)))
            	smtpServer.sendmail(self.__mailSender, list(set(self.__mailToList + self.__mailccList + self.__SPMList + self.SPMEmailList + [sys.argv[4]])), msg.as_string())
            else:
            	msg['To'] = ','.join(list(set(self.__mailToList)))
            	msg['Cc'] = ','.join(list(set(self.__mailccList + self.__SPMList)))
            	smtpServer.sendmail(self.__mailSender, list(set(self.__mailToList + self.__mailccList + self.__SPMList)), msg.as_string())
        else:
            print "Send Mail to (%s) Error: %s" % (sendTo, msg.as_string())
        fp = open(self.__mailDir + "/P%s.eml" % str(patchNo), 'wb')
        fp.write(msg.as_string())
        fp.close()
        smtpServer.quit()

    def __getBugzillaInfo(self, comment=''):
        result = {}
        if 0 == len(comment):
            return "comment is none"
        reciever = 'renzhi.yang.hz@tcl.com'
        if reciever.endswith('.com'):
            result['assigned'] = reciever
            result['assigned'] = result['assigned'].encode('gb2312')	
        match =re.match(r'porting P\d+_+ALPS(\d+)_.+', comment)
        if match:
            while True:
		InputString = "Summary:"              
                if len(InputString) > 0:
                    result['shortDesc'] = InputString
                    break
                else:
                    continue
            result['bugID'] = 'ALPS'+match.group(1)
            result['comment'] = comment
            result['patchID'] = 'ALPS'
            return result
        bugID =re.match(r'porting P\d+_.+?(\d+)_.+', comment).group(1)
        result['bugID'] = bugID
        result['comment'] = comment
        result['bugLink'] = "https://alm.tclcom.com:7003/im/issues?selection=%s" % bugID
        result['patchID'] = 'JRD'
        return result


	
    def justBuild(self):
        print "Just to build now"
        print "Repo sync latest import code"
        self.RepoCode(self.__importCode, self.__branch)
        self.__reset(self.__importCode)
        if 'Fail' == self.__compile(self.__importCode,self.__branch):
		print "Build Failed"
		sys.exit(1)

    def DriveOnlyBranchBuild(self, patchNo):
        print "Now start to build driveonly branch"
        print "Repo sync latest driveonly code"
	for eachbranch in self.__DriveOnlyBranchName:
		DriveOnlyCode = ''
		DriveOnlyCode = self.__DriveOnlyCode + eachbranch
        	self.RepoCode(DriveOnlyCode, eachbranch)
        	self.__reset(DriveOnlyCode)
        	if 'Fail' == self.__compile(DriveOnlyCode, eachbranch):
			print "Driveonli branch Build Failed"
			sys.exit(1)
		self.uploadBinToTeleweb(DriveOnlyCode, eachbranch, patchNo)
		DriveOnlyCode = ''

    def uploadBinToTeleweb(self, DriveOnlyCode, eachbranch, patchNo):
        print "Now start to upload"
	os.chdir(DriveOnlyCode)
        if '' == patchNo:
            print "patchNo is none"
            sys.exit(1)
	version_num="P%s-%s" % (patchNo, eachbranch)
	driveonly_release_dir = r'/local/release/%s' % eachbranch
	if not os.path.isdir(driveonly_release_dir+'/v'+version_num):
            os.system('mkdir -p %s' % driveonly_release_dir+'/v'+version_num)
	
	#os.system('/local/int_jenkins/sortresult/projects/Driveronly_CopyImg.sh %s %s %s '%(eachbranch, version_num, self.__project))
	os.chdir(DriveOnlyCode+'/out/target/product/mickey6t')
	tmpstrs=getoutput('ls | grep -E ".bin|.img|_Android_scatter.txt"').split('\n')
	print 'tmpstr',tmpstrs
	if tmpstrs:
		for tmpstr in tmpstrs:
			os.system('cp -f %s %s'%(tmpstr,driveonly_release_dir+'/v'+version_num))
	tmpstrs=''
	tmpstrs=getoutput('find %s -name BPLGUInfoCustomApp* -o -name DbgInfo_* -o -name BPMdMetaDataBase*'%(DriveOnlyCode+'/out')).split('\n')
	print 'tmpsts',tmpstrs
	if tmpstrs:
		for tmpstr in tmpstrs:
			os.system('cp -f %s %s'%(tmpstr,driveonly_release_dir+'/v'+version_num))
	
	print "begin to upload result to teleweb"
	
        
	#os.system('cp %s %s'%(tmpstrs,driveonly_release_dir))
	os.chdir(driveonly_release_dir)
	os.system('scp -r v%s sl_hz_hran@10.92.32.26:/mfs/teleweb/%s/driveonly/' % (version_num,self.branchDict[eachbranch]))
	print "finish upload"		

if __name__ == "__main__":
    print sys.argv
    if len(sys.argv) == 5 and sys.argv[2] == 'MergePatch':
        pm = PatchMerge(sys.argv[1])
        pm.MergePatch()
	pm.MergeOnePatchForDriveOnly()
    elif len(sys.argv) == 5 and sys.argv[2] == 'MergeOnePatch':
        pm = PatchMerge(sys.argv[1])
        pm.MergeOnePatch(sys.argv[4],sys.argv[3])
    elif len(sys.argv) == 6 and sys.argv[2] == 'MergeOnePatchToDriveOnly':
	print '====MergeOnePatchToDriveOnly start===='
        pm = PatchMerge(sys.argv[1])
        pm.MergeOnePatchForDriveOnly(sys.argv[3])
	if sys.argv[5] == 'false':
		pm.makeDriveOnlyPatchMail(sys.argv[3])
	print '====MergeOnePatchToDriveOnly end===='
    elif len(sys.argv) == 7 and sys.argv[2] == 'PatchMail':
        pm = PatchMerge(sys.argv[1])
        pm.makePatchMail(sys.argv[3])
    elif len(sys.argv) == 3 and sys.argv[2] == 'build':
        pm = PatchMerge(sys.argv[1])
        pm.justBuild()

    elif len(sys.argv) == 4 and sys.argv[2] == 'DriveOnlybuild':
        pm = PatchMerge(sys.argv[1])
        pm.DriveOnlyBranchBuild(sys.argv[3])
        pm.checkDriveOnlyBuildResult(sys.argv[3])

    else:
        print "%s Usage:" % sys.argv[0]
        print "\t%s BaseDir MergePatch" % sys.argv[0]
        print "\t%s BaseDir MergeOnePatch PatchNo" % sys.argv[0]
        print "\t%s BaseDir PatchMail PatchNo" % sys.argv[0]
        print "For example: \n\t%s . MergePatch\n\t%s . MergeOnePatch 1\n\t%s . PatchMail 1" % (sys.argv[0], sys.argv[0],sys.argv[0])

