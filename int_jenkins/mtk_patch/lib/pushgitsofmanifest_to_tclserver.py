#!/usr/bin/python
#coding=utf-8
import sys
sys.path.append('/local/int_jenkins/lib')
sys.path.append('/local/int_jenkins/mtk_patch/lib')
import os
import re
import xml.dom.minidom
import datetime
from Config import *


#python pushgitsofmanifest_to_tclserver.py -CodeDir -curlmanifest -platform -devCodeBranch
def ImportMTKGit(Code,curlmanifest,platform,devCodeBranch):
	current_time = datetime.datetime.now().strftime("%Y-%m-%d")
	print current_time 		
	dom = xml.dom.minidom.parse('%s' % curlmanifest)
	projList = dom.getElementsByTagName('project')
	for proj in projList:
		projName = proj.getAttribute('name')
		projPath = proj.getAttribute('path')
		if projPath == '':
			projPath = projName
		git_path = Code + "/" + projPath
		os.chdir(git_path)                    
		print 'git push git@10.92.32.10:%s/%s %s:%s' %(platform,projPath,current_time,devCodeBranch)
		os.system('git branch %s ; git push git@10.92.32.10:%s/%s %s:%s' %(current_time,platform,projPath,current_time,devCodeBranch))

if __name__ == "__main__":
	print "test for argv"
	print sys.argv
	conf = Config()
	conf.addFromArg(sys.argv[1:])
	Code = conf.getConf('CodeDir','the code dir')
	curlmanifest = conf.getConf('curlmanifest','the source manifest file dir name name')#sys.argv[3]
	platform = conf.getConf('platform','the platform for gitweb you want to push')
	devCodeBranch = conf.getConf('devCodeBranch','the new branch name you want to push git to ')
	ImportMTKGit(Code,curlmanifest,platform,devCodeBranch)

