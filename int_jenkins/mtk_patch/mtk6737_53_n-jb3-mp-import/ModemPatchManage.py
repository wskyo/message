#!/usr/bin/python
#coding=utf-8

import os
import re
import sys
import getpass
from commands import *
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

class ModemPatchMerge(CheckFile,dotProjectDb,checkPatchInfor):
    def __init__(self,basedir='/local'):
        self.repopath = '/local/tools/repo/repo'
        os.chdir(basedir)
        self.__baseDir = os.getcwd()		
        self.__debug = False
        self.__pushCodeToGit = True

        wb = xlrd.open_workbook('%s/mtk6737_53_n-jb3-mp-import.xls' % getoutput("dirname %s" % (sys.argv[0])))
        mtkSheet = wb.sheet_by_name(u'ModemInfo')
        self.__branch = mtkSheet.cell(1, 0).value.strip()
        self.__patchFormat = mtkSheet.cell(1, 1).value.strip()
        self.__mailServer = mtkSheet.cell(1, 2).value.strip()
        self.__mailTitle = mtkSheet.cell(1, 3).value.strip()
        self.__mailAccount = mtkSheet.cell(1, 4).value.strip()
        self.__mailSender = mtkSheet.cell(1, 5).value.strip()
        self.__mailToList = mtkSheet.cell(1, 6).value.strip().split(',')
        self.__mailccList = mtkSheet.cell(1, 7).value.strip().split(',')
        self.__SPMList = mtkSheet.cell(1, 8).value.strip().split(',')
        self.__DriveOnlyBranch = mtkSheet.cell(1, 9).value.strip().split(',')
        self.__importCode = "/" + "local" + "/mtk_patch_import" + "/" + self.__branch + "_MD"
        self.__ModemCode = self.__importCode + "/modem/LWTG_MOLY_LR9"
        self.__mergeDone = "/" + "local" + "/mtk_patch_import" + "/mergeDone"
        self.__ignorePatch = "/" + "local" + "/mtk_patch_import" + "/ignorePatch"
        self.__ongoingPatch = "/" + "local" + "/mtk_patch_import" + "/TODO"
        self.__mailDir = "/" + "local" + "/mtk_patch_import" + "/" + "/Mail"
        self.__start = "/" + "local" + "/mtk_patch_import" + "/start"
        self.__DriveOnlyCode = "/" + "local" + "/mtk_patch_import" + "/"
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

	self.checkFileDict = self.getAffectFileDict()
	self.projectList = self.checkProjectName()
        if not os.path.isdir(self.__start):
            os.system('mkdir -p %s' % self.__start)

        print "baseDir = %s\nbranch = %s\npatchFormat = %s\nmailServer = %s\nmailTitle = %s\nmailAccount = %s\nmailSender = %s\nongoingPatch = %s\nDriveOnlyBranchName = %s" % (self.__baseDir,self.__branch, self.__patchFormat, self.__mailServer, self.__mailTitle, self.__mailAccount,self.__mailSender, self.__ongoingPatch,self.__DriveOnlyBranch)
        print "mailToList = %s\nmailccList = %s\nSPMList = %s\n" % (self.__mailToList, self.__mailccList, self.__SPMList)

    def repo_code(self, CodeDir, ModemDir, CodeBranchName):
        print "Now checking the modem code if exist,"
        if not os.path.isdir(CodeDir):
            os.system('mkdir -p %s' % CodeDir)
        os.chdir(CodeDir)

        if os.path.exists(CodeDir + "/modem/LWTG_MOLY_LR9" + "/.git") == False:
            os.system('git clone git@10.92.32.10:mtk6753/modem/LWTG.git LWTG_MOLY_LR9')
            os.chdir(ModemDir)
            os.system('git checkout %s' % CodeBranchName)

        
    def MergeModemPatch(self):
        print "Please create file(start) on /local/mtk_patch_import directory. If not exist, the script will stop and exit."
        self.repo_code(self.__importCode, self.__ModemCode, self.__branch)
        while (os.path.exists("/" + "local" + "/mtk_patch_import" + "/start") == True):
            self.__reset(self.__ModemCode)
            patchNo = self.__getNextPatchNo()
            print "getNextPatchNo %s" % patchNo
            patchFilename = self.__takePatch(self.__ModemCode, patchNo)
            if 'Nofile' == patchFilename:
                print "Wait next patch, patchNo = %s" % patchNo
                continue
            os.chdir(self.__ModemCode)
            prevMD5 = getoutput('rm -rf /tmp/tempfile; git add .; git status >> /tmp/tempfile; md5sum /tmp/tempfile').split()[0]
            if 'Success' == self.__compile(self.__ModemCode):
                print "Compile success"
                self.__reset(self.__ModemCode)
                patchFilename = self.__takePatch(self.__ModemCode, patchNo)
                comment = 'porting P%s_%s' %(patchNo, patchFilename.replace('(', '_').replace(')', '_'))
                print comment
                if True == self.__pushCodeToGit:
                    print 'start merge.....'
                    os.system('git add .')
                    nextMD5 = getoutput('rm -rf /tmp/tempfile; git status >> /tmp/tempfile; md5sum /tmp/tempfile').split()[0]
                    if prevMD5 == nextMD5:
                        os.system('git commit -m "%s"; git push origin HEAD:refs/heads/%s' % (comment,self.__branch))
                        self.__movePatchToMergeDone(patchNo)
                    print 'finish merge....'
                   

    def MergeModemOnePatch(self,patchtype,patchNo=-1):
        print "Please create file(start) on /local/mtk_patch_import directory. If not exist, the script will stop and exit."
        self.repo_code(self.__importCode, self.__ModemCode, self.__branch)
        if (os.path.exists("/" + "local" + "/mtk_patch_import" + "/start") == True):
            self.__reset(self.__ModemCode)
            print "patchNo %s" % patchNo
            patchFilename = self.__takePatch(self.__ModemCode, patchNo)
            if 'Nofile' == patchFilename:
                print "No p%s patch. Please copy the correct patch to TODO directory" % patchNo
                sys.exit(1)
            mak_dir=self.__importCode + '/modem/LWTG_MOLY_LR9/make'
            mak_str='JHZ6737M_65_N(LWG_DSDS)%s.mak'
            print 'cp -f "%s/%s" "%s/%s"'%(mak_dir,mak_str%'',mak_dir,mak_str%'_MICKEY6T')
            os.system('cp -f "%s/%s" "%s/%s"'%(mak_dir,mak_str%'',mak_dir,mak_str%'_MICKEY6T'))
            os.system("sed -i 's/JHZ6737M_65_N(LWG_DSDS)/JHZ6737M_65_N(LWG_DSDS)_MICKEY6T/g' '%s/%s'"%(mak_dir,mak_str%'_MICKEY6T'))
            tmp = getoutput("sed -n '/MOLY.LR9.W1444.MD.LWTG.MP.V110.5/p' '%s/%s'"%(mak_dir,mak_str%'_MICKEY6T')).split('\n')
            if tmp:
	        assert len(tmp)==1,"more than one MOLY strings was found"
                if tmp[0].find('\r')==-1:
                    print "sed -i 's/%s/%s\r/g' '%s/%s'"%(tmp[0],tmp[0],mak_dir,mak_str%'_MICKEY6T')
                    os.system("sed -i 's/%s/%s\r/g' '%s/%s'"%(tmp[0],tmp[0],mak_dir,mak_str%'_MICKEY6T'))
            print 'cp -f "%s/%s" "%s/%s"'%(mak_dir,mak_str%'',mak_dir,mak_str%'_SIMBA6L')
            os.system('cp -f "%s/%s" "%s/%s"'%(mak_dir,mak_str%'',mak_dir,mak_str%'_SIMBA6L'))
            os.system("sed -i 's/JHZ6737M_65_N(LWG_DSDS)/JHZ6737M_65_N(LWG_DSDS)_SIMBA6L/g' '%s/%s'"%(mak_dir,mak_str%'_SIMBA6L'))
            tmp = getoutput("sed -n '/MOLY.LR9.W1444.MD.LWTG.MP.V110.5/p' '%s/%s'"%(mak_dir,mak_str%'_SIMBA6L')).split('\n')
            if tmp:
	        assert len(tmp)==1,"more than one MOLY strings was found"
                if tmp[0].find('\r')==-1:
                    print "sed -i 's/%s/%s\r/g' '%s/%s'"%(tmp[0],tmp[0],mak_dir,mak_str%'_SIMBA6L')
                    os.system("sed -i 's/%s/%s\r/g' '%s/%s'"%(tmp[0],tmp[0],mak_dir,mak_str%'_SIMBA6L'))
            mak_str='JHZ6737M_65_N(LWG_DSDS_COTSX)%s.mak'
            print 'cp -f "%s/%s" "%s/%s"'%(mak_dir,mak_str%'',mak_dir,mak_str%'_BUZZ6E')
            os.system('cp -f "%s/%s" "%s/%s"'%(mak_dir,mak_str%'',mak_dir,mak_str%'_BUZZ6E'))
            os.system("sed -i 's/JHZ6737M_65_N(LWG_DSDS_COTSX)/JHZ6737M_65_N(LWG_DSDS_COTSX)_BUZZ6E/g' '%s/%s'"%(mak_dir,mak_str%'_BUZZ6E'))
            tmp = getoutput("sed -n '/MOLY.LR9.W1444.MD.LWTG.MP.V110.5/p' '%s/%s'"%(mak_dir,mak_str%'_BUZZ6E')).split('\n')
            if tmp:
	        assert len(tmp)==1,"more than one MOLY strings was found"
                if tmp[0].find('\r')==-1:
                    print "sed -i 's/%s/%s\r/g' '%s/%s'"%(tmp[0],tmp[0],mak_dir,mak_str%'_BUZZ6E')
                    os.system("sed -i 's/%s/%s\r/g' '%s/%s'"%(tmp[0],tmp[0],mak_dir,mak_str%'_BUZZ6E'))
            os.chdir(self.__ModemCode)
            prevMD5 = getoutput('rm -rf /tmp/tempfile; git add .; git status >> /tmp/tempfile; md5sum /tmp/tempfile').split()[0]
            if 'Success' == self.__compile(self.__ModemCode):
                print "Compile success"
                self.__reset(self.__ModemCode)
                patchFilename = self.__takePatch(self.__ModemCode, patchNo)
		mak_dir=self.__importCode + '/modem/LWTG_MOLY_LR9/make'
            	mak_str='JHZ6737M_65_N(LWG_DSDS)%s.mak'
            	print 'cp -f "%s/%s" "%s/%s"'%(mak_dir,mak_str%'',mak_dir,mak_str%'_MICKEY6T')
            	os.system('cp -f "%s/%s" "%s/%s"'%(mak_dir,mak_str%'',mak_dir,mak_str%'_MICKEY6T'))
            	os.system("sed -i 's/JHZ6737M_65_N(LWG_DSDS)/JHZ6737M_65_N(LWG_DSDS)_MICKEY6T/g' '%s/%s'"%(mak_dir,mak_str%'_MICKEY6T'))
                tmp = getoutput("sed -n '/MOLY.LR9.W1444.MD.LWTG.MP.V110.5/p' '%s/%s'"%(mak_dir,mak_str%'_MICKEY6T')).split('\n')
                if tmp:
	            assert len(tmp)==1,"more than one MOLY strings was found"
                    if tmp[0].find('\r')==-1:
                        print "sed -i 's/%s/%s\r/g' '%s/%s'"%(tmp[0],tmp[0],mak_dir,mak_str%'_MICKEY6T')
                        os.system("sed -i 's/%s/%s\r/g' '%s/%s'"%(tmp[0],tmp[0],mak_dir,mak_str%'_MICKEY6T'))
            	print 'cp -f "%s/%s" "%s/%s"'%(mak_dir,mak_str%'',mak_dir,mak_str%'_SIMBA6L')
            	os.system('cp -f "%s/%s" "%s/%s"'%(mak_dir,mak_str%'',mak_dir,mak_str%'_SIMBA6L'))
            	os.system("sed -i 's/JHZ6737M_65_N(LWG_DSDS)/JHZ6737M_65_N(LWG_DSDS)_SIMBA6L/g' '%s/%s'"%(mak_dir,mak_str%'_SIMBA6L'))
                tmp = getoutput("sed -n '/MOLY.LR9.W1444.MD.LWTG.MP.V110.5/p' '%s/%s'"%(mak_dir,mak_str%'_SIMBA6L')).split('\n')
                if tmp:
	            assert len(tmp)==1,"more than one MOLY strings was found"
                    if tmp[0].find('\r')==-1:
                        print "sed -i 's/%s/%s\r/g' '%s/%s'"%(tmp[0],tmp[0],mak_dir,mak_str%'_SIMBA6L')
                        os.system("sed -i 's/%s/%s\r/g' '%s/%s'"%(tmp[0],tmp[0],mak_dir,mak_str%'_SIMBA6L'))
		mak_str='JHZ6737M_65_N(LWG_DSDS_COTSX)%s.mak'
		print 'cp -f "%s/%s" "%s/%s"'%(mak_dir,mak_str%'',mak_dir,mak_str%'_BUZZ6E')
            	os.system('cp -f "%s/%s" "%s/%s"'%(mak_dir,mak_str%'',mak_dir,mak_str%'_BUZZ6E'))
            	os.system("sed -i 's/JHZ6737M_65_N(LWG_DSDS_COTSX)/JHZ6737M_65_N(LWG_DSDS_COTSX)_BUZZ6E/g' '%s/%s'"%(mak_dir,mak_str%'_BUZZ6E'))
                tmp = getoutput("sed -n '/MOLY.LR9.W1444.MD.LWTG.MP.V110.5/p' '%s/%s'"%(mak_dir,mak_str%'_BUZZ6E')).split('\n')
                if tmp:
	            assert len(tmp)==1,"more than one MOLY strings was found"
                    if tmp[0].find('\r')==-1:
                        print "sed -i 's/%s/%s\r/g' '%s/%s'"%(tmp[0],tmp[0],mak_dir,mak_str%'_BUZZ6E')
                        os.system("sed -i 's/%s/%s\r/g' '%s/%s'"%(tmp[0],tmp[0],mak_dir,mak_str%'_BUZZ6E'))
                self.patch_type,self.vnum,self.pnum,self.eservice_ID = self.getMtkPatchInfor(patchFilename)
                self.description = self.getDescriptionFromPatchListFile(self.__importCode, self.untardir,self.eservice_ID)
                os.chdir(self.__ModemCode)
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
                    if prevMD5 == nextMD5:
                        os.system('git commit -m "%s"; git push origin HEAD:refs/heads/%s;' % (comment,self.__branch))
			print "prevMD5 == nextMD5"
                    print 'finish merge....'
            else:
		print "The code build failed"
		sys.exit(1)

    def __takePatchForDriveOnly(self, patchNo=''):
        if '' == patchNo:
            print "patchNo is none"
            sys.exit(1)
        elif '0' == patchNo:            
            match_patch = re.match(r'For_(.*)', self.__patchFormat) 
            if match_patch:
                patch_format = match_patch.group(1)
                patchFilename = getoutput("ls %s | grep %s.tar.gz" % (self.__ongoingPatch, patch_format))
        else:
            patchFilename = getoutput("ls %s | grep %s | grep P%s\).tar.gz" % (self.__ongoingPatch, self.__patchFormat, patchNo))
        if 0 == len(patchFilename):
            return "Nofile"
        return patchFilename

    def MergeModemOnePatchToDriveOnly(self,patchNo=-1):
	for branch in self.__DriveOnlyBranch:
            DriveOnlyCode =  self.__DriveOnlyCode + branch + "_MD"
            DriveModemCode = DriveOnlyCode + "/modem/LWTG_MOLY_LR9"
            self.repo_code(DriveOnlyCode,DriveModemCode,branch) 
            self.eachDriveOnlyBranchImport(DriveModemCode, branch, patchNo)
            DriveOnlyCode = ''
            DriveModemCode = ''		            	
	#self.__movePatchToMergeDone(patchNo)

    def eachDriveOnlyBranchImport(self, DriveModemCode, eachbranch, patchNo=-1):
	print "Please create file(start) on /local/mtk_patch_import directory. If not exist, the script will stop and exit."  
	if (os.path.exists("/" + "local" + "/mtk_patch_import" + "/start") == True):
            self.__reset(DriveModemCode)
            print "patchNo %s" % patchNo
            patchFilename = self.__takePatchForDriveOnly(patchNo)
            os.chdir(DriveModemCode)
            comment = 'porting P%s_%s for driveonly' %(patchNo, patchFilename.replace('(', '_').replace(')', '_'))
            tagname = 'porting_modem_patch_%s_for_%s' % (patchFilename.replace('(', '_').replace(')', '_'), eachbranch)
            tagcomment = 'porting modem patch P%s' % patchNo
            print "commit comment is %s" % comment
            print "tagname is %s" % tagname
            print "tagcomment is %s" % tagcomment   
            if True == self.__pushCodeToGit:
                print 'start merge.....'
                self.__takeImportCommitForDriveOnly(DriveModemCode, self.__branch, eachbranch, patchNo)
                os.system('git push origin HEAD:refs/heads/%s; git tag -a %s -m "%s"; git push origin %s' % (eachbranch,tagname,tagcomment,tagname))
                
            print 'finish drive only branch merge....'
            print "Now start to build drive only branch modem"
            if 'Success' == self.__compile(DriveModemCode,'_MICKEY6T'):
                print "Driveonly Branch build successfully"
            else:
		print "Driveonly Branch build failed"
		sys.exit(1)	

    def __takeImportCommitForDriveOnly(self, codedir, branch, driveonlyBranch, patchNo=''):
        if '' == patchNo:
            print "patchNo is none"
            sys.exit(1)

        if not os.path.isdir(codedir):
            print "The driveonly code download failed"
            sys.exit(1)

	os.chdir(codedir)
	patchList = getoutput('git log origin/mtk6737_53-n-v1.0-import --format=%s | grep "%s" | grep "porting P%s_" | sort' %('%s^^^^^^%H^^^^^^$PWD', self.__patchFormat, patchNo)).split('\n')
	print 	patchList	
	if len(patchList) != 0:
		for item in range(len(patchList)):
			if patchList[item] == '':
				continue
			itemInfo = patchList[item].split('^^^^^^')
			if len(itemInfo) == 0:
				continue
			print itemInfo
			if itemInfo[1]:		
				cerryPickInfo = getoutput('git cherry-pick %s' % itemInfo[1])		
				if "error:" in cerryPickInfo:
					print "cherry pick failed"
					print "you have to check conflicts"
					sys.exit(1)
				else:
					print "cherry pick successfully"
                
    def __reset(self, code):
        if False == self.__debug:
            os.chdir(code)
            sleep(120)
            print "reset start... \nClean all, reset to HEAD and git pull"
            os.system('rm -rf ./build')
            os.system('git reset --hard HEAD')
            os.system('git clean -df')
            os.system('git pull')
            print "reset done"

    def __getNextPatchNo(self):
        PatchNo = 0
        os.chdir(self.__ModemCode)
        patchList = getoutput('git log --format=%s | grep %s' %('%s', self.__patchFormat)).split('\n')
        for item in patchList: 
            match = re.match(r'porting P(\d+).+', item)
            if match:
                tmpNo = match.group(1)
            else:
                continue
            
            if int(tmpNo) > int(PatchNo):
                PatchNo = tmpNo
        return int(PatchNo) + 1

    def __takePatch(self,codedir,patchNo=''):
        if '' == patchNo:
            print "patchNo is none"
            sys.exit(1)
        elif '0' == patchNo:            
            match_patch = re.match(r'For_(.*)', self.__patchFormat) 
            if match_patch:
                patch_format = match_patch.group(1)
                patchFilename = getoutput("ls %s | grep %s.tar.gz" % (self.__ongoingPatch, patch_format))
        else:
            patchFilename = getoutput("ls %s | grep %s | grep P%s\).tar.gz" % (self.__ongoingPatch, self.__patchFormat, patchNo))
        if 0 == len(patchFilename):
            return "Nofile"
        self.untardir = "%s/MD-P%s" % (self.__ongoingPatch,patchNo)
        os.system('mkdir -p %s' % self.untardir)
        os.system('tar zxvf "%s/%s" -C %s' % (self.__ongoingPatch,patchFilename,self.untardir))
        if not os.path.isdir(codedir):
            os.system('mkdir -p %s' % codedir)
        
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LTG_DSDS/dhl/database/BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LTG_DSDS/dhl/database/_BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LTG_DSDS_COTSX/dhl/database/BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LTG_DSDS_COTSX/dhl/database/_BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LTG_DSDS_CDD48/dhl/database/BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LTG_DSDS_CDD48/dhl/database/_BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LTG_DSDS_COTSX_CDD48/dhl/database/BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LTG_DSDS_COTSX_CDD48/dhl/database/_BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LWG_DSDS/dhl/database/BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LWG_DSDS/dhl/database/_BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LWG_DSDS_COTSX/dhl/database/BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LWG_DSDS_COTSX/dhl/database/_BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LWG_DSDS_CDD48/dhl/database/BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LWG_DSDS_CDD48/dhl/database/_BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LWG_DSDS_COTSX_CDD48/dhl/database/BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LWG_DSDS_COTSX_CDD48/dhl/database/_BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LWG_TSTS/dhl/database/BPLGUInfoCustomApp*' %codedir)
        os.system('git rm %s/mtk_rel/JHZ6737M_65_N/LWG_TSTS/dhl/database/_BPLGUInfoCustomApp*' %codedir)

        os.system('cp -dpRv %s/* %s' %(self.untardir,codedir))
        #os.system('rm -rf %s' % untardir)		
        return patchFilename
    
    def __movePatchToMergeDone(self, patchNo):
        os.system('mkdir -p %s' % self.__mergeDone)
        if '0' == patchNo:
            match_patch = re.match(r'For_(.*)', self.__patchFormat) 
            if match_patch:
                patch_format = match_patch.group(1)
                os.system('mv %s/%s.tar.gz %s' % (self.__ongoingPatch,patch_format,self.__mergeDone))
        else:
            os.system('mv %s/*%s*.P%s\).tar.gz %s' % (self.__ongoingPatch,self.__patchFormat,patchNo,self.__mergeDone))


    def __compile(self, CodeDir,sp_modem=''):		
        space = getoutput('df -h /local/ | awk \'{print $4}\'').split('\n')[1][:-1]
        if (space < 5):
            print "**Error: there is no enough space left on device!"
            return "Fail"
        os.chdir(CodeDir)
        os.system('chmod 777 ./tools/init/strcmpex_linux.exe')
        print "building......"
        if False == self.__debug:
            buildStatus = getstatusoutput("./make.sh \"JHZ6737M_65_N(LWG_DSDS)%s.mak\" new"%sp_modem)
            if (buildStatus[0] >> 8) == 0:
                print buildStatus[1]
                return 'Success' 
            else:
                print buildStatus[1]
                return 'Fail'
        else:
            buildInfo = raw_input('[Debug mode] Please input compile result Info "==> [FAIL]" or "other string":') 
            if buildInfo.find("==> [FAIL]") >= 0:
                return "Fail"
            return 'Success'

    def makePatchMail(self,patchNo=-1):
        '''parameter patchNo is 0,1,2,3...'''
        if int(patchNo) == -1:
            print "Parameter patchNo(%s) is error." % patchNo
            return
	print self.__ongoingPatch, self.__patchFormat, patchNo
        patchFilename = getoutput("ls %s | grep %s | grep P%s\).tar.gz" % (self.__ongoingPatch, self.__patchFormat, patchNo))
	print 'patchFilename',patchFilename
        self.patch_type,self.vnum,self.pnum,self.eservice_ID = self.getMtkPatchInfor(patchFilename) 
        if not os.path.isdir(self.__mailDir):
            os.system('mkdir -p %s' % self.__mailDir)
        os.chdir(self.__ModemCode)
        #Please don't add 'repo sync' action here, it will affect merge work.
        patchList = getoutput('git log --format=%s\ | grep "%s" | grep "porting P%s_" | sort' %('%s^^^^^^%H^^^^^^$PWD', self.__patchFormat, patchNo)).split('\n')
	mailtitle = '%s P%s modem Patch Merge' % (self.__mailTitle, patchNo)
        for item in range(len(patchList)):
            itemInfo = patchList[item].split('^^^^^^')
            if 3 != len(itemInfo):
                print "patchList have problems. patchList = %s" % patchList
		print "The pacth has no modification"
                sys.exit(1)
        mailBody = []
	dearName = sys.argv[4].split('@')[0]
        mailBody.append('<p align=\'Left\'><b>Dear %s,</b></p>' % dearName)

        mailBody.append('<p align=\'Left\'>MTK modem Patch <b><font color="#FF0000">P%s</font></b> has been merged to import branch(%s)<br/></p>' % (patchNo,self.__branch))
        mailBody.append('<p align=\'Left\'><b>Please help to merge patch to below branch:</b><br/></p>')
        for eachCodeBranchName in self.devCodeBranch:		
            mailBody.append('<p align=\'Left\'><b><font color="#FF0000">%s</font></b></p>' % eachCodeBranchName)
        mailBody.append('<p align=\'Left\'><font color="#FF0000">Please kindly give a feedback in 24h.</b></font><br/><br/></p>')		
        mailBody.append('<p align=\'Left\'>Patch Link in import branch:</p>')
        for item in range(len(patchList)):
            itemInfo = patchList[item].split('^^^^^^')    			
            gitNamefilder = 'modem'  		
            gitLink = 'http://10.92.32.10/sdd2/gitweb-mtk6753/?p=modem/LWTG.git;a=commit;h=%s' % itemInfo[1]
            self.insertImportCommitInfoTO_dotp_mtk_commit(self.importIdDict,self.devCodeProjectIDList,self.__branch,self.patch_type,self.vnum,self.pnum,self.eservice_ID,itemInfo[1],gitLink,gitNamefilder)
            mailBody.append('<p align=\'Left\'>%s)modem</p><p align=\'Left\'><a href="%s">%s</a></p>' % (item+1,gitLink,gitLink))
            for keyname in self.checkFileDict.keys():
		filename = self.checkFileDict[keyname]['filename']
		if self.checkFileDict[keyname]['gitname'] == 'modem':
			if True == self.getFileLibNvram(self.__ModemCode,filename):
				mailBody.append('<p align=\'Left\'><font color="#FF0000"><b>Note: The file of %s has been changed in patch P%s.</font></b></p>' % (filename,patchNo))
				mailBody.append('<p align=\'Left\'><font color="#FF0000"><b>Please contact Drive team to check whether to merge this modification to project code</font></b></p>')
				mailBody.append('<br/>')		
            for projectname in self.projectList:
		if True == self.getFileLibNvram(self.__ModemCode,projectname):
			project_str = u'请将以上链接中' + projectname + u'文件夹的修改merge到项目对应的文件夹中'
			mailBody.append('<p align=\'Left\'><font color="#FF0000">%s:%s</font></p>' % (gitNamefilder,project_str))
            a = u"\\\\10.92.32.12\\RDhzKM\\SWD-Share\\INT\\MTKPatch\\mtk6737_53_n"
            mailBody.append('<p align=\'Left\'><b>You can also find this patch (P%s) in:<font color="#FF0000">%s</font></b></p>' % (patchNo, a))

            mailBody.append('<p align=\'Left\'><b>After you complete to merge the mtk6737_53_n Mickey6t/Buzz6E/SIMBA6L patch P%s,</b></p>' % patchNo)
            mailBody.append('<p align=\'Left\'><b>please make sure the related issues of this MTK Patch you merged are fixed,and</b></p>')
            mailBody.append('<p align=\'Left\'><font color="#FF0000"><b>please send a remind email to us!!!</b></font></p>')                          
        print 'self.importIdDict',self.importIdDict
        print 'self.projectid_codeBranch_Dict',self.projectid_codeBranch_Dict	
        for projectID1 in self.importIdDict.keys():
		for projectID2 in self.projectid_codeBranch_Dict.keys():
			if projectID1 == projectID2:
				self.insertImportId_And_DevBranch_To_dotp_mtk_merge(self.importIdDict[projectID1],self.projectid_codeBranch_Dict[projectID2],sys.argv[4])                          
        #os.system('python /local/int_jenkins/mtk_patch/lib/insertdbToWr.py %s %s %s %s' % (self.__branch,self.vnum,self.pnum,self.eservice_ID) )
        os.system('python /local/int_jenkins/mtk_patch/lib/insertInforToManpower.py %s %s %s %s %s' % (self.__branch,self.vnum,self.pnum,self.eservice_ID,sys.argv[6]) )                        
        self.__sendMail(patchNo, mailtitle, mailBody)

    def makePatchDriveOnlyMail(self,patchNo=-1):
        '''parameter patchNo is 0,1,2,3...'''
        if int(patchNo) == -1:
            print "Parameter patchNo(%s) is error." % patchNo
            return
        if not os.path.isdir(self.__mailDir):
            os.system('mkdir -p %s' % self.__mailDir)

        mailBody = []
        mailBody.append('<p align=\'Left\'><b>Dear Integrator,</b></p>')
        mailBody.append('<p align=\'Left\'>MTK modem Patch <b><font color="#FF0000">P%s</font></b> has been merged to driveonly import branch(%s)<br/></p>' % (patchNo,','.join(self.__DriveOnlyBranch))) 

	for branch in self.__DriveOnlyBranch:
            DriveOnlyCode =  self.__DriveOnlyCode + branch + "_MD"
            DriveModemCode = DriveOnlyCode + "/modem/LWTG_MOLY_LR9"
            os.chdir(DriveModemCode)
            patchList = getoutput('git log --format=%s\ | grep "%s" | grep "porting P%s_" | sort' %('%s^^^^^^%H^^^^^^$PWD', self.__patchFormat, patchNo)).split('\n')
            for item in range(len(patchList)):
            	itemInfo = patchList[item].split('^^^^^^')
            	if 3 != len(itemInfo):
                	print "patchList have problems. patchList = %s" % patchList
			print "The pacth has no modification"
                	sys.exit(1)
            mailBody.append('<p align=\'Left\'>Patch Link in driveonly import branch: %s</p>'  % branch )
            for item in range(len(patchList)):
            	itemInfo = patchList[item].split('^^^^^^')    			
            	gitLink = 'http://10.92.32.10/sdd2/gitweb-mtk6753/?p=modem/LWTG.git;a=commit;h=%s' % itemInfo[1]
            	mailBody.append('<p align=\'Left\'>%s)modem</p><p align=\'Left\'><a href="%s">%s</a></p>' % (item+1,gitLink,gitLink))
	a = u"\\\\10.92.32.12\\RDhzKM\\SWD-Share\\INT\\MTKPatch\\mtk6737_53_n"
	mailBody.append('<p align=\'Left\'><b>You can also find this patch (P%s) in:<font color="#FF0000">%s</font></b></p>' % (patchNo, a)) 
	mailBody.append('<p align=\'Left\'><b>please check the modification.</b></p>') 
	mailtitle = '%s P%s modem Patch Merged to driveonly branch' % (self.__mailTitle, patchNo)                      
        self.__sendMail(patchNo, mailtitle, mailBody)

    def __sendMail(self,patchNo, mailtitle, mailBody=[], to=[]):
        '''parameter toList: the PR owner(assigned) or interface or leader'''
        smtpServer = smtplib.SMTP(self.__mailServer)
	reload(sys)
	print sys.setdefaultencoding('gbk')	
        msg = MIMEText(''.join(mailBody), 'html','utf-16')
        msg.set_charset('gb2312')   
        msg['From'] = self.__mailSender
        #msg['Subject'] = '%s P%s modem Patch Merge' %(self.__mailTitle, patchNo)
        msg['Subject'] = mailtitle
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

if __name__ == "__main__":
    if len(sys.argv) == 5 and sys.argv[2] == 'MergePatch':
        pm = ModemPatchMerge(sys.argv[1])
        pm.MergeModemPatch()
    elif len(sys.argv) ==5 and sys.argv[2] == 'MergeOnePatch':
        pm = ModemPatchMerge(sys.argv[1])
        pm.MergeModemOnePatch(sys.argv[4],sys.argv[3])
    elif len(sys.argv) ==4 and sys.argv[2] == 'MergeOnePatchToDriveOnly':
	print 'MergeOnePatchToDriveOnly start'
        pm = ModemPatchMerge(sys.argv[1])
        pm.MergeModemOnePatchToDriveOnly(sys.argv[3])
        #pm.makePatchDriveOnlyMail(sys.argv[3])
	print 'MergeOnePatchToDriveOnly end'
    elif len(sys.argv) == 7 and sys.argv[2] == 'PatchMail':
        pm = ModemPatchMerge(sys.argv[1])
        pm.makePatchMail(sys.argv[3])
    else:
        print "%s Usage:" % sys.argv[0]
        print "\t%s BaseDir MergePatch" % sys.argv[0]
        print "\t%s BaseDir MergeOnePatch PatchNo" % sys.argv[0]
