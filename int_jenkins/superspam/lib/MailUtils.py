#!/usr/bin/python
#coding=utf-8
############################################################################
## MailUtils be user to create mail html and send mail to recipients.
## this class has mail head, body, foot, attach method for comment mail message.
## add by jianbo.deng for superspam create 2013-08-27
############################################################################

import sys
import os
import re
import glob

import email
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.mime.image import MIMEImage
from time import strftime, localtime
from commands import *
import commands
from Utils import *
import time


class MailUtils:

	## mail head please didn't modified
	def getMailHeadHtml(self, conf):
		html = '<html xmlns="http://www.w3.org/1999/xhtml">'
		html += '<head>'
		html += '<meta http-equiv="Content-Type" content="text/html; charset=gb2312" />'
		html += '<style type="text/css">'
		html += 'body {font-family:arial; font-size:10pt;}'
		html += 'td {font-family:arial; font-size:10pt;}'
		html += '</style>'
		buildok = conf.getConf('buildok', 'build ok or no <yes|no>','yes' )
		version = conf.getConf('version', 'project current version')
		projectName = conf.getConf('project', 'Project name in check list file name')
		if buildok == 'no':
			html += '<title>[Compile Failed] %s %s compile failed</title>' % (projectName,version)
		else:
			html += '<title>%s Delivery</title>' % conf.getConf('mailsubject', 'mail subject title')
		html += '</head>'
		return html

	def getMailBodyHtml(self, conf):
		html = ''
		html += self.getBodyHalfHtml(conf)
		return html
		

	###create 1. AP/Modem Database from 2. Images List 3. Manifest path
	def getBodyHalfHtml(self, conf):
		subVer = '0'
		version = conf.getConf('version', 'project current version')
		projectName = conf.getConf('project', 'Project name in check list file name')
		isMiniVersion = conf.getConf('isMiniVersion', 'is mini version or not, defualt is no', 'no')
		miniVersionBand = conf.getConf('BAND', 'mini version band defualt is EU', 'EU')
		baseVersion = conf.getConf('baseversion', 'project base version')
		telewebVersion = conf.getConf('telewebversion', 'download teleweb version')
		modemVersion = conf.getConf('modemversion', 'modem version')
		mtkBaseLine = conf.getConf('mtkBaseLine', 'mtk base line')
                branch = conf.getConf('codebranch','codebranch')
		releasenoteprojname = conf.getConf('releasenoteprojname', 'release note project name')
		buildok = conf.getConf('buildok', 'build OK or no <yes|no>','yes')
                band = conf.getConf('BAND', 'which BAND version to deliver? <CN|EU|US|2G|LATAM3G|LATAM2G|EU-1S|EU-2S|US0-1S|US0-2S|US1-1S|US1-2S|US2-1S|US2-2S|US3-1S|US3-2S>')    
                 
		if(version.__contains__('-')):
			num = version.index('-')
			subVer = version[num+1]
			manVer = version[0:num]
		avdb = getoutput("ls -lh --time-style=long-iso /local/release/"+projectName+"-release/v"+version+"/ | cut -d' ' -f10 | grep -e '^A.*.db'")
		mvdb = getoutput("ls -lh --time-style=long-iso /local/release/"+projectName+"-release/v"+version+"/ | cut -d' ' -f10 | grep -e '^O.*.db'")

		versionDir = 'Daily_version'
		if isMiniVersion == 'yes':
			versionDir = 'mini'
		else:
			if subVer == '0':
				versionDir = 'appli'
		html = '<p>Dear all,</p>'

		## create Teleweb download path
		if buildok == 'no':
			errorInfo = self.getBuildErrorInfo(conf)
			self.errorInfo = self.getBuildErrorDetail(conf)
			html += '<p align=\'Left\'>'+ '%s %s compile failed! please check!!! <br/></p>' % (projectName,version)
			if errorInfo:
				html += '<p align=\'Left\'>'+ 'Please check the error infomation from android.log as following:<br/></p>'
				html += '<p align=\'Left\'><font color="#FF0000">%s</font>' % self.errorInfo
				html += '<p align=\'Left\'><font color="#FF0000">%s</font>' % errorInfo
			html += '<p align=\'Left\'>'+ 'Attachment is the compiling log,which can be refered.<br/></p>'
 			html += '<p align=\'Left\'>'+ 'The following change list may give you some help! <br/></p>'
		else:  
			pixi35rpmb = self.ForPixi35RPMB(conf)
			if pixi35rpmb:
                                releasenoteprojname = "Pixi3-5_3G_RPMB"       		
			if band != '' and conf.getConf('isMiniVersion', 'is mini version') == 'yes':						      
                                html += '<p align=\'Left\'>'+ conf.getConf('mailsubject', 'mail subject')+'It has been delivered to TeleWeb. You can find it at %s/%s/v%s_%s.<br/></p>' % (releasenoteprojname, versionDir, version, band)
 			else:
                                html += '<p align=\'Left\'>'+ conf.getConf('mailsubject', 'mail subject')+'It has been delivered to TeleWeb. You can find it at %s/%s/v%s.<br/></p>' % (releasenoteprojname, versionDir, version)

			### Based On
			html += '<p><br/><b>Based On: v'+baseVersion+'</b></p>'
                        html += '<p align=\'Left\'>Please use TeleWeb %s to download the images.</p>' % telewebVersion
                        html += '<p align=\'Left\'>Teleweb: <br/r><a href=https://webampbis.tcl-ta.com/TELEWEB/TELEWEB/TOOLS/TELEWEB/delivery/1_MTK_SP/TeleWeb_S/>https://webampbis.tcl-ta.com/TELEWEB/TELEWEB/TOOLS/TELEWEB/delivery/1_MTK_SP/TeleWeb_S/</a></p>'
			#android security patch level,gsm,cts,gts info
			html += '<br align=\'Left\'><font color=green>Android security patch level from current version code:</font><b><font color=blue>%s</font></b><br/>' % self.curCodeSecuPatchLevel
			html += '<br align=\'Left\'><font color=green>GMS version from current version code:</font><b><font color=blue>%s</font></b>' % self.GMSVersionFromCode
			html += '<br align=\'Left\'><font color=green>The End date of Google GMS version </font><b><font color=blue>%s</font></b> is </font><b><font color=blue>%s</font></b>' % (self.GoogleGmsLastVertion, self.GMSDeadline)
			html += '<br align=\'Left\'><font color=green>Google GMS latest version:</font><b><font color=blue>%s</font></b>, End date:<b><font color=blue>NA</font></b><br/>' % self.GMSVersionReleased
			html += '<br align=\'Left\'><font color=green>The End date of Google CTS version </font><b><font color=blue>%s</font></b> is </font><b><font color=blue>%s</font></b>' % (self.GoogleCTSLastVertion, self.GoogleCTSNewVersionDeadline)
			html += '<br align=\'Left\'><font color=green>Google CTS latest version:</font><b><font color=blue>%s</font></b>, End date:<b><font color=blue>NA</font></b><br/>' % self.GoogleCTSVersion
			html += '<br align=\'Left\'><font color=green>The End date of Google GTS version </font><b><font color=blue>%s</font></b> is </font><b><font color=blue>%s</font></b>' % (self.GoogleGTSLastVertion, self.GoogleGTSNewVersionDeadline)
			html += '<br align=\'Left\'><font color=green>Google GTS latest version:</font><b><font color=blue>%s</font></b>, End date:<b><font color=blue>NA</font></b><br/>' % self.GoogleGTSVersion
			##create the AP/Modem Database from 
			html += '<p align=\'Left\'>Please get the AP/Modem Database from:<br/></p>'
			if conf.getConf('isMiniVersion', 'is mini version') == 'yes':
                                band = ''
 				band = conf.getConf('BAND', 'which BAND version to deliver? <CN|EU|US|2G|LATAM3G|LATAM2G|EU-1S|EU-2S|US0-1S|US0-2S|US1-1S|US1-2S|US2-2S|US3-1S|US3-2S|US4-1S|US4-2S|US5-2S|US5-1S>')  
                                if band != '' :
                                     version = '%s_%s' %(version,band)
			html += '<p align=\'Left\'><font color=blue>/mfs/teleweb/'+releasenoteprojname+'/'+versionDir+'/v'+version+'/%s</font></p>' % avdb
			html += '<p align=\'Left\'><font color=blue>/mfs/teleweb/'+releasenoteprojname+'/'+versionDir+'/v'+version+'/%s</font></p>' % mvdb

			html += '<p align=\'Left\'><font color=blue>Modem Version:'+modemVersion+'</font></p>'
			html += '<p align=\'Left\'><font color=blue>MtkBaseLine:'+mtkBaseLine+'</font></p>'
			html += '<p class="STYLE1">Images List of SW%s</p>' % version
			html += '<table>'
		
			##create Images List frome here
			pushdir(conf.getConf('releasedir', 'Release image files folder', '/local/release/%s-release/v%s/' % (projectName, version)))
			VerScaFile = getoutput("ls -lh --time-style=long-iso /local/release/"+projectName+"-release/v"+version+"/ | grep .sca | cut -d' ' -f10,12  | sort").split('\n')
			VerFileList = getoutput("ls -lh --time-style=long-iso /local/release/"+projectName+"-release/v"+version+"/ | grep .mbn | cut -d' ' -f10,12  | sort").split('\n')
			VerDBList = getoutput("ls -lh --time-style=long-iso /local/release/"+projectName+"-release/v"+version+"/ | grep .db | cut -d' ' -f10,12  | sort").split('\n')
			strFormat =  '<tr><td width="200">%s:</td1><td><b>%s</b></td></tr>'
			#print "----ver scafile -----------"
			#print VerScaFile
			#print '--------++++++++-----------'
			for i in range(len(VerScaFile)):
				pair = VerScaFile[i].split(' ')
				html += strFormat % (pair[1][len('flashtool/'):].split('.')[0].upper()[7:], pair[0])
			for i in range(len(VerFileList)):
				pair = VerFileList[i].split(' ')
				html += strFormat % (pair[1][len('flashtool/'):].split('.')[0].upper()[0:20], pair[0])
			for i in range(len(VerDBList)):
				pair = VerDBList[i].split(' ')
				html += strFormat % (pair[1][len('flashtool/'):].split('.')[0].upper()[0:20], pair[0])
			popdir()
			##end create images list 
		
			## create download path
			html += '</table>'
                        html += '<p align=\'Left\'><font color=blue>Code Branch Name:'+branch+'</font></p>'
			if releasenoteprojname.lower() == "pixi4-35_3g":
				html += '<p>V%s Manifest:<br/><a href=http://10.92.32.10/gitweb.cgi/?p=sdd1/odm_manifest.git;a=blob;f=int/%s/v%s.xml>http://10.92.32.10/gitweb.cgi/?p=sdd1/odm_manifest.git;a=blob;f=int/%s/v%s.xml</a></p>' % (version, releasenoteprojname.lower(), version, releasenoteprojname.lower(), version)
			elif releasenoteprojname == "Pixi3-5_3G_RPMB":
				html += '<p>V%s Manifest:<br/><a href=http://10.92.32.10/gitweb.cgi/?p=sdd1/manifest.git;a=blob;f=int/pixi3-5_3g/v%s.xml>http://10.92.32.10/gitweb.cgi/?p=sdd1/manifest.git;a=blob;f=int/pixi3-5_3g/v%s.xml</a></p>' % (version, version, version)			
			else:
				html += '<p>V%s Manifest:<br/><a href=http://10.92.32.10/gitweb.cgi/?p=sdd1/manifest.git;a=blob;f=int/%s/v%s.xml>http://10.92.32.10/gitweb.cgi/?p=sdd1/manifest.git;a=blob;f=int/%s/v%s.xml</a></p>' % (version, releasenoteprojname.lower(), version, releasenoteprojname.lower(), version)
		return html

	### email foot 
	def getFootEMailHtml(self, conf):
		html = '<br/><img src="cid:ReleaseMailLogo.jpg">'
		html += '<p><font color="gray">'
		html += 'Best Regards,<br />'
		html += conf.getConf('fullName','send mail name, defualt is hudson.admin.hz', 'Hudson.admin.hz')+'<br />'
		html += 'TEL: '+conf.getConf('TEL', 'send email tel, defualt 0752-8228580(68580)', '0752-8228580(68580)')+'<br />'
		html += 'MAIL: '+conf.getConf('EMail','email, hudson.admin.hz@tcl.com', 'hudson.admin.hz@tcl.com')+'<br />'
		html += 'ADDR: 17 Huifeng 3rd Road, Zhongkai Hi-tech Developmen District,Huizhou,Guangdong'
		html += '</font></p>'
		html += '</body>'
		html += '</html>'
		return html

	def sendMail(self, conf, html):
		fullName = conf.getConf('fullname', 'full name')
		defultEmaill = conf.getConf('defultmail', 'Defult Email')
		buildok = conf.getConf('buildok', 'build ok or no <yes|no>','yes')
		#tempdir = conf.getConf('tempdir', 'temp dir')
		officeList = None
		miniList = None
		DailyList = None
		msg = MIMEMultipart('mixed')
		msg['Date'] = strftime("%a, %d %b %Y %T", localtime()) + ' +0800'
		if buildok == 'yes':
			msg['Subject'] = conf.getConf('mailsubject', 'Mail subject')
		else:
          		msg['Subject'] = '[Compile Failed] %s %s compile failed !' % (conf.getConf('project', 'Project name in check list file name'),conf.getConf('version', 'project current version'))
		msg['From'] = '"\'%s\'" <%s>' % (fullName, defultEmaill)
		
		smtpAddrSet = set([])
		sendTo = conf.getConf('sendto', 'email send to list<self|all>', )
		version = self.getVersion(conf)
		## big version will send to office list
		print self.getMailList(conf)
		#msg['To'] = '"\'%s\'" <%s>' % (self.getMailList(conf),self.getMailList(conf))
		msg['To'] = ''
		tmp = self.getMailList(conf).split(',')
		smtpAddrSet = self.getMailList(conf).split(',')		
		
		for to in tmp:
			if msg['To'] == '':
				msg['To'] = '"\'%s\'" <%s>' %(to,to)
			else:
				msg['To'] = msg['To'] + '"\'%s\'" <%s>' %(to,to)
		self.emailContent(conf,html,msg,defultEmaill,smtpAddrSet)	


	#copy symbols
	def CopySymbols(self,conf):
		projectname = conf.getConf('prlistprojname', 'Project name in PR List file name')
		version = conf.getConf('version','current version')
		mtkproject = conf.getConf('mtkproject','mtk product')	
		out_val_elf = os.system('tar -zcf modem_elf.tar.gz modem/out_modem/*.elf')
                if out_val_elf != 0:
                       out_val_elf = os.system('tar -zcf modem_elf.tar.gz modem/mcu/temp_modem/')
		out_val = os.system('tar -zcf symbols.tar.gz out/target/product/%s/symbols' %mtkproject)
		out_val_vmlinux = os.system('tar -zcf vmlinux.tar.gz out/target/product/%s/obj/KERNEL_OBJ/vmlinux' %mtkproject)
		if out_val != 0:
			print "tar symbols error!!!"
			return False
		if out_val_elf != 0:
			print "tar modem elf file error!!!"
			return False
		if out_val_vmlinux != 0:
			print "tar vmlinux file error!!!"
			return False

                os.system('/local/int_jenkins/misc/copy_symbols.sh %s %s %s %s %s'%(self.username,self.ip,self.password,projectname,version))	    
                docmd('scp symbols.tar.gz user@10.92.35.20:/var/www/data/symbols/%s/v%s' %(projectname,version))
                docmd('scp modem_elf.tar.gz user@10.92.35.20:/var/www/data/symbols/%s/v%s' %(projectname,version))
                docmd('scp vmlinux.tar.gz user@10.92.35.20:/var/www/data/symbols/%s/v%s' %(projectname,version))

	#insert buildinfo
	def InsertBuildInfo(self,conf):
		projectname=conf.getConf('prlistprojname', 'Project name in PR List file name')
		version =conf.getConf('version','current version')
		branch =conf.getConf('codebranch','codebranch')
		spm =conf.getConf('Spmlist','spm')
		spm = spm.replace('<','')
		spm = spm.replace('>','')
		releasenote = 'ReleaseNote_%s_SW%s.xls' % (projectname,version)
		owner =conf.getConf('owner','owner')

		version_type ='CU'
		if conf.getConf('isBigVersion', 'version is big version') == 'yes':
			version_type ='CU'
		if self.isMiniVersion(version) == 'yes':
			version_type ='mini'
			releasenote = 'MiniSW_ReleaseNote_%s_%s.xls'% (projectname,version)
		if conf.getConf('isDailyVersion', 'version is Daily version') == 'yes':	
			version_type ='daily'
		if "pixi3-5_3g" == conf.getConf('releasenoteprojname', 'project name '):
			if version[2] == '6' or version[2] == 'T':
                            projectname = "Pixi3-5_3G_RPMB"
		docmd('python /local/int_jenkins/misc/insertBuildInfo.py -version %s -Project %s -manifestbranch %s -versiontype %s -releasenote %s -spm %s -owner %s -patchlevel %s -gmsversion %s -releasegms %s -gmsdeadline %s -ctsversion %s -ctsdeadline %s -gtsversion %s -gtsdeadline %s' %(version,projectname,branch,version_type,releasenote,spm,owner,self.curCodeSecuPatchLevel,self.GMSVersionFromCode,self.GMSVersionReleased,self.GMSDeadline,self.GoogleCTSVersion,self.GoogleCTSNewVersionDeadline,self.GoogleGTSVersion,self.GoogleGTSNewVersionDeadline))
	# insert release infor for weekly report
	def InsertWeeklyReport(self, conf, integrator,comment):
		projectname=conf.getConf('prlistprojname', 'Project name in PR List file name')
		version =conf.getConf('version','current version')
		#comment = conf.getConf('version_use','The use of current version offered by spm')
		if "pixi3-5_3g" == conf.getConf('releasenoteprojname', 'project name '):
			if version[2] == '6' or version[2] == 'T':
                            projectname = "Pixi3-5_3G_RPMB"
		#docmd('python /local/int_jenkins/misc/insertReleaseinforWhenEmail.py "%s" "%s" "%s" "%s"' %(projectname,version,comment,integrator))

	def checkDBFromTemp(self, telewebBaseDir, version):
		docmd('ssh sl_hz_hran@10.92.32.26 ls -l %s/tmp/v%s > dblog.txt' % (telewebBaseDir, version) )
		f = open('dblog.txt')
		Adbtag=0
		Odbtag=0
		checksumtag=0
		for line in f.readlines():                    
                       if line.find('A') != -1 and line.find('.db') != -1 and line.find('APDB_') != -1 :
		            print 'A*.db file exist'
                            Adbtag=1   
                       if line.find('O') != -1 and line.find('.db') != -1 and line.find('InfoCustomApp') != -1 :
                            print 'O*.db file exist'  
                            Odbtag=1   
                       if line.find('checksum_') != -1 and line.find('.ini') != -1 :
                            print 'checksum*.ini file exist'  
                            checksumtag=1                  					
		f.close()
		if Adbtag == 1 and Odbtag == 1 :
                       print 'DB files has exist in Teleweb:%s/tmp/v%s'  % (telewebBaseDir, version)
		else:
                       res = self.conf.getConf('DB', 'DB files not exist in Teleweb, Pls upload A*.db and O*.db to teleweb' + '<yes|no>')
                       if res.upper() == 'YES':
                            print "Upload DB ,Done"
                       elif res.upper() == 'NO':
                            print "Not Upload DB to Teleweb, pls check"
                            sys.exit(1)
		if checksumtag == 1 :
                       print 'checksum_*.ini file is exist in Teleweb:%s/tmp/v%s'  % (telewebBaseDir, version)
		else:
                       res = self.conf.getConf('CheckSum', 'CheckSum_*.ini not exist, Pls create CheckSum_*.ini and upload to teleweb' + '<yes|no>')
                       if res.upper() == 'YES':
                            print "Upload CheckSum_*.ini ,Done"
                       elif res.upper() == 'NO':
                            print "Not Upload CheckSum_*.ini to Teleweb, pls check"
                            #sys.exit(1)

                

	## if teleweb change pls override this method
	def moveResultFromTemp(self, conf):
		sendto = conf.getConf('sendto','send to')
		if conf.getConf('mvteleweb', 'Change teleweb folder <yes|no>', 'yes' if sendto == 'all' else 'no') == 'yes':
			telewebBaseDir = '/mfs/teleweb/%s'% conf.getConf('releasenoteprojname', 'project name ')
			version =  conf.getConf('version', 'current version')
		        projectName = conf.getConf('project', 'Project name in check list file name')
		        
			rpmb = self.ForPixi35RPMB(conf)			                       
			#band = conf.getConf('BAND', 'which BAND version to deliver? <CN|EU|US|2G|LATAM3G|LATAM2G>')
			if conf.getConf('isDailyVersion', 'is Daily version') == 'yes':
				docmd('ssh sl_hz_hran@10.92.32.26 rm -rfv %s/Daily_version/v%s' % (telewebBaseDir, version))
				if rpmb:
					docmd('ssh sl_hz_hran@10.92.32.26 mv -v %s/tmp/v%s/ %s/Daily_version/' % (telewebBaseDir, version, rpmb))
				else:
					docmd('ssh sl_hz_hran@10.92.32.26 mv -v %s/tmp/v%s/ %s/Daily_version/' % (telewebBaseDir, version, telewebBaseDir))
			elif conf.getConf('isMiniVersion', 'is mini version') == 'yes':
                                band = ''
                                band = conf.getConf('BAND', 'which BAND version to deliver? <CN|EU|US|2G|LATAM3G|LATAM2G|EU-1S|EU-2S|US0-1S|US0-2S|US1-1S|US1-2S|US2-2S|US3-1S|US3-2S>')  
                                if band != '':  
                                     version = '%s_%s' %(version,band)
				docmd('ssh sl_hz_hran@10.92.32.26 rm -rfv %s/mini/v%s' % (telewebBaseDir, version))
				#docmd('ssh sl_hz_hran@10.92.32.26 mv -v %s/tmp/v%s/ %s/mini/' % (telewebBaseDir, version, telewebBaseDir))
                                self.checkDBFromTemp(telewebBaseDir,version)

				if rpmb:
					print "The pixi3-5 rpmb mini dir is %s" % rpmb
					docmd('ssh sl_hz_hran@10.92.32.26 mv -v %s/tmp/v%s/ %s/mini/' % (telewebBaseDir, version, rpmb))
				else:
					docmd('ssh sl_hz_hran@10.92.32.26 mv -v %s/tmp/v%s/ %s/mini/' % (telewebBaseDir, version, telewebBaseDir))

			else :
				docmd('ssh sl_hz_hran@10.92.32.26 rm -rfv %s/appli/v%s' % (telewebBaseDir, version))
                                self.checkDBFromTemp(telewebBaseDir,version)
				if rpmb:
					print "The pixi3-5 rpmb appli dir is %s" % rpmb
					docmd('ssh sl_hz_hran@10.92.32.26 mv -v %s/tmp/v%s/ %s/appli/' % (telewebBaseDir, version, rpmb))
				else:
					docmd('ssh sl_hz_hran@10.92.32.26 mv -v %s/tmp/v%s/ %s/appli/' % (telewebBaseDir, version, telewebBaseDir))
					docmd('ssh sl_hz_hran@10.92.32.26 rm -rfv %s/tmp/v%s_perso/' % (telewebBaseDir, version))


	#yangrenzhi add for pixi3-5 RPMB 2015-11-30
	def ForPixi35RPMB(self, conf):
		version =  conf.getConf('version', 'current version')
		if "pixi3-5_3g" == conf.getConf('releasenoteprojname', 'project name '):
			if version[2] == '6' or version[2] == 'T':
				telewebName = "Pixi3-5_3G_RPMB"
				telewebBaseDirForRpmb = '/mfs/teleweb/Pixi3-5_3G_RPMB'
			else:
				telewebBaseDirForRpmb = ''
		else:
			telewebBaseDirForRpmb = ''			
		
		return telewebBaseDirForRpmb

	#yangrenzhi end add for pixi3-5 RPMB 2015-11-30
	#get build error info from android.log by renzhi.yang 20160-3-17
	def getBuildErrorInfo(self, conf):
		projectname = conf.getConf('prlistprojname', 'Project name in PR List file name')
		version = conf.getConf('version','current version')
		if projectname == 'pixi3-45':
			codeDir = '/local/build/%s-release/' % projectname
		else:
			codeDir = '/local/build/%s-release/v%s' % (projectname,version)
		os.chdir(codeDir)		
                if projectname == 'ELSA6T' :
                     unfinished_job = commands.getstatusoutput('grep -n "make: *** [ninja_wrapper]" android.log')
                else:
                     unfinished_job = commands.getstatusoutput('grep -n "Waiting for unfinished jobs\.\.\.\." android.log')
		if unfinished_job[0] == 0:
			match = re.match('^(\d+):make.*',unfinished_job[1]) 
			if match:
				error_info = commands.getstatusoutput("sed -n '%d,%d'p android.log" % ((int(match.group(1))-4),int(match.group(1))))
				if error_info[0] == 0:
					print "The error info as follow"
					print error_info[1]
				else:
					error_info[1] = ''
		return error_info[1]

	def getBuildErrorDetail(self, conf):
		projectname = conf.getConf('prlistprojname', 'Project name in PR List file name')
		version = conf.getConf('version','current version')
		if projectname == 'pixi3-45':
			codeDir = '/local/build/%s-release/' % projectname
		else:
			codeDir = '/local/build/%s-release/v%s' % (projectname,version)
		os.chdir(codeDir)
		F = open("android.log",'r')
		error_list = []
		while True:
			line = F.readline()
			line = line.strip()
			if len(line) == 0:
				break
			match = re.match('^(ERROR:.*)',line) 
                        match_failed = re.match('^(FAILED:.*)',line)
			if match:
				error_list.append(line) if line not in error_list else '' 
			elif match_failed:
				error_list.append(line) if line not in error_list else ''
		error_info = ';'.join(error_list)
		print "error_info",error_infos
		return error_info

	def sendMailForRemindPlatformSesurityPatch(self, conf):
		fullName = conf.getConf('fullname', 'full name')
		defultEmaill = conf.getConf('defultmail', 'Defult Email')
		msg = MIMEMultipart('mixed')
		project = conf.getConf('project', 'Project name in check list file name') 
		version = conf.getConf('version', 'project current version')
		codeBranch = conf.getConf('codebranch','codebranch')
		msg['Date'] = strftime("%a, %d %b %Y %T", localtime()) + ' +0800'
		msg['Subject'] = '[PLATFORM_SECURITY_PATCH][%s %s] remind to check security patch level value!' % (project,version)
		msg['From'] = '"\'%s\'" <%s>' % (fullName, defultEmaill)	

		html = '' 
		html += self.getMailBodyHtmlForRemind(conf,html,project,version,codeBranch)


		smtpAddrSet = set([])
		sendTo = conf.getConf('Spmlist','the spm of the project')
		msg['To'] = ''
		msg['Cc'] = ''
		tmp = conf.getConf('officelist','if not mail list,pls input').split(',')
		smtpAddrSet.add(sendTo)
		if msg['To'] == '':
			msg['To'] = '"\'%s\'" <%s>' %(sendTo,sendTo)
		else:
			msg['To'] = msg['To'] + '"\'%s\'" <%s>' %(sendTo,sendTo)

		for cto in tmp:
			smtpAddrSet.add(cto)
			if msg['Cc'] == '':
				msg['Cc'] = '"\'%s\'" <%s>' %(cto,cto)
			else:
				msg['Cc'] = msg['Cc'] + '"\'%s\'" <%s>' %(cto,cto)
		self.emailContent(conf,html,msg,defultEmaill,smtpAddrSet)
		
	def emailContent(self,conf,html,msg,defultEmaill,smtpAddrSet):
		contMsg = MIMEMultipart('related')
		#htmlPart = MIMEBase('text', 'html', charset="us-ascii")
		htmlPart = MIMEBase('text', 'html', charset="utf-8")		
		html = html.encode('utf-8')
		htmlPart.set_payload(html)
		encoders.encode_base64(htmlPart)
		htmlPart["Content-Disposition"] = 'filename="%s.html"' % conf.getConf('mailsubject', 'Mail subject').replace(' ', '_')
		contMsg.attach(htmlPart)	
		imageSet = set([])
	
		for imageStr in re.findall('<\s*img\s+src\s*=\s*\"?\s*cid\s*:\s*[^<>\"]+\s*\"?\s*>', html, re.M):
			match = re.search('<\s*img\s+src\s*=\s*\"?\s*cid\s*:\s*([^<>\"]+)\s*\"?\s*>', imageStr)
			if match:
				imageSet.add(match.group(1))
	
		for imageFile in list(imageSet):
			fp = open(self.tempdir+'/image/'+imageFile, 'r')
			imagePart = MIMEImage(fp.read())
			fp.close
			imagePart.add_header('Content-ID', '<%s>' % imageFile)
			imagePart["Content-Disposition"] = 'filename="%s"' % imageFile
			contMsg.attach(imagePart)	
		msg.attach(contMsg)	

		for attachFile in glob.glob(self.tempdir+'/attach/*'):
			attach = MIMEBase('application', 'octet-stream')
			fp=open(attachFile, 'rb')
			attach.set_payload(fp.read())
			fp.close()
			encoders.encode_base64(attach)
			attach["Content-Disposition"] = 'attachment; filename="%s"' % os.path.split(attachFile)[1]
			msg.attach(attach)
		##smtp server change here
		smtpServer = conf.getConf('smtpserver', 'Smtp server', 'mail.tcl.com')
		#smtpServer = '192.168.166.100'
		sendMailAccount = defultEmaill
                #print 'smtpServer ----- %s' % smtpServer
		if (conf.getConf('nosmtpauth', 'Do not authenticate smtp account <yes|no>', 'yes' if smtpServer == 'mail.tcl.com' else 'no') == 'no' or (sendMailAccount != 'hudson.admin.hz@tcl.com')):
			smtpPassword = conf.getConf('mailpassword', 'Passowrd for Email account <%s>' % sendMailAccount, echo=False)
                        #print "======if csz for the email password====="
		else:
			smtpPassword = 'Hzsw#123'
			#print "======else csz for the email password====="
		s = smtplib.SMTP(smtpServer)
		s.set_debuglevel(int(conf.getConf('smtpdebug', 'Smtp debug level <^\d$>', '1')))

		if smtpPassword:
			#print '====the password is:%s====' %smtpPassword
			s.login(sendMailAccount[:sendMailAccount.index('@')], smtpPassword)
		if smtpAddrSet != None and smtpAddrSet.__len__() == 0:
			smtpAddrSet.add('<shie.zhao@tcl.com>')			                   
		s.sendmail(sendMailAccount, list(smtpAddrSet), msg.as_string())
		s.quit()
		print '-------------------'
		print '--== MAIL SENT ==--'
		print '-------------------'


	def getMailBodyHtmlForRemind(self,conf,html,project,version,codeBranch):
		html += '<br align=\'Left\'>Dear SPM'
		html += '<br align=\'Left\'>Please check security patch level value in %s(codebranch:%s)' % (version,codeBranch)
		html += '<br align=\'Left\'>security patch level in %s code: <b><font color=red>%s</b></font>' % (version,self.curCodeSecuPatchLevel)
		html += '<br align=\'Left\'>But the latest value offered by google: <b><font color=red>%s</b></font><br/>' % (self.googleSecuPatchLevel)
		html += '<br align=\'Left\'>Time in code should <b><font color=red>newer</b></font> than time offered by google, please check.</font><br/>'
		html += '<br/><br/>'
		html += '<br/><br/>'
		html += '<br/>Best Regards,<br />'
		html += conf.getConf('fullName','send mail name, defualt is hudson.admin.hz', 'Hudson.admin.hz')+'<br />'
		html += 'TEL: '+conf.getConf('TEL', 'send email tel, defualt 0752-8228580(68580)', '0752-8228580(68580)')+'<br />'
		html += 'MAIL: '+conf.getConf('EMail','email, hudson.admin.hz@tcl.com', 'hudson.admin.hz@tcl.com')+'<br />'
		html += 'ADDR: 17 Huifeng 3rd Road, Zhongkai Hi-tech Developmen District,Huizhou,Guangdong'
		return html
				
	def unlock_zz(self, conf):
	        if conf.getConf('isBigVersion', 'version is big version') == 'yes':
         	   import MySQLdb, urllib, urllib2, traceback

         	   BIGBROTHER_DB = {'host': '10.92.32.22', 'port': 3306, 'user': 'toolsng', 'passwd': 'cnep1m2ppMSbsm', 'db': 'bigbrother'}

         	   project_b = ""
         	   family = ""
         	   conn = MySQLdb.Connect(**BIGBROTHER_DB)
         	   cursor = conn.cursor()
         	   try:
         	       project = conf.getConf('project', 'project name ')
         	       project = re.sub(r'[-_\s]', '', project.lower())
         	       version = conf.getConf('version', 'current version')
         	       sql = "SELECT distinct product FROM t_scg_production WHERE soft_label = '{0}' AND product = '{1}' AND doublon= 'zz'".format(version, project)
         	       print sql
         	       cursor.execute(sql)
         	       result = cursor.fetchall()
         	       if result:
         	           project_b = result[0][0]

         	       if project_b:
         	           sql = 'SELECT clid_data_path FROM t_web_project_conf WHERE project_name = \'{0}\''.format(project_b)
         	           print sql
         	           cursor.execute(sql)
         	           result = cursor.fetchone()
         	           family = result[0].split('/')[0]
         	   finally:
         	       cursor.close()
         	       conn.close()
         	   if project_b and family:
         	       try:
         	           data = "http://10.92.32.22/clid/software/clid/php/unlock_software_auto.php?" + urllib.urlencode({'family': family, 'project': project, 'version': version, 'login': 'autozz', 'password': 'zzauto', 'locksoft': '0'})
         	           print data
         	           retData = urllib2.urlopen(data).read()
         	           print retData
         	       except:
         	           print "!!!!!!!!!!!!!!!!!!!!!!unlick perso failed!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
         	           print traceback.format_exc()
         	       return
         	   print "!!!!!!!!!!!!!!!!!!!!!!unlick perso failed!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"


