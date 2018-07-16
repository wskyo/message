#!/usr/bin/python

############################################################################
## add by yinfang.lai  create 2015-02-26
## add 3 parameters from command line and add makeConfig.bat by xueqin.zhang 2015-02-28
## replace 4 blank by Tab xueqin.zhang 2015-03-09
###########################################################################

import sys
import os
import re
import commands
import xml.dom.minidom
import glob
import string

curDict = {}
resDict = {}
baseList = []
repeatList = []

def initGitDic():
		curManifest = sys.argv[3]
		for line in file(curManifest).readlines():
			match = re.search('<project(.*?)\s+name=\"([^\"]+)\"\s+path=\"([^\"]+)\"+', line)
			if match:
                                #print line
				curDict[match.group(3).strip()] = [match.group(2).strip()] #{'packages/apps/JrdContainer': ['mtk6737/packages/apps/JrdContainer']}


def getChangeMessage():
		html = ''
		for key in sorted(curDict.keys()):
			curVal = curDict.pop(key)
                        #print curVal
			match = re.match('^(.*\/(.*))$', curVal[0])
			lab = match.group(2) 
			uplab = lab.upper()  #JrdContainer
			resDict[curVal[0]] = [uplab]
			if uplab in baseList:
				repeatList.append(uplab)
			baseList.append(uplab)


def main():
	if len(sys.argv) != 4:
		print 'please input 3 parameters like: python main.py refs/heads/mt6582-l-pixi3-5-v1.0-tmp MT6582-L-PIXI3-5- mt6582-l-pixi3-5-v1.0-tmp.xml'
		sys.exit(1)
	branch = sys.argv[1]
	prename = sys.argv[2]
	
	initGitDic()
	getChangeMessage()
	print '******************************'
	print 'repeatList'
	print '******************************'
	print repeatList
	html = ''
	html +='<?xml version="1.0" encoding="UTF-8"?>\n'
	html +='<projects>\n'
	for key in sorted(resDict.keys()):
		cVal = resDict.pop(key)
		cValue = cVal[0]
		if cVal[0] in repeatList:
			count =key.count('/')
			if  count > 1:
				match = re.match('^(.*\/((.*)\/(.*)))$', key)
				lab = '%s-%s' %(match.group(3),match.group(4))
				cValue = lab.upper()
		html +='<project>\n'
		html +='	<name>%s</name>\n' %key
		html +='	<branch>%s</branch>\n' %branch
		html +='	<baseline>%s%s-P1.0</baseline>\n' %(prename,cValue)
		html +='</project>\n'	
	html +='</projects>'
	f = open ('projectConfig.xml','w')
	f.write(html)		

if __name__ == '__main__':
	main()

