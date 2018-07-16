#!/usr/bin/python

############################################################################
## add by yinfang.lai  create 2015-02-26
## add 3 parameters from command line and add makeConfig.bat by xueqin.zhang 2015-02-28
## replace 4 blank by Tab xueqin.zhang 2015-03-09
## add by lang.feng get_default && get_new_tag 2017-12-27
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
		curManifest = sys.argv[2]
		for line in file(curManifest).readlines():
			match = re.search('<project(.*?)\s+name=\"([^\"]+)\"\s+path=\"([^\"]+)\"+', line)
			if match:
                                #print line
				curDict[match.group(3).strip()] = [match.group(2).strip()] #{'packages/apps/JrdContainer': ['mtk6737/packages/apps/JrdContainer']}


def getChangeMessage():
		html = ''
		for key in sorted(curDict.keys()):
			curVal = curDict.pop(key)
                        #print curVal              #mtk6737/packages/apps/JrdContainer
			match = re.match('^(.*\/(.*))$', curVal[0])
			lab = match.group(2) 
			uplab = lab.upper()  #JrdContainer
			resDict[curVal[0]] = [uplab]#['mtk6737/packages/apps/JrdContainer']:JrdContainer
			if uplab in baseList:
				repeatList.append(uplab)
			baseList.append(uplab)
def get_default():
    afile=open(sys.argv[2])
    alines=afile.readlines()
    for line in alines:
        if re.match('\<default',line.strip()):
            dline=line.strip()
            break
    print dline
    match=re.search('.*revision=\"(.*?)\".*',dline)
    dint=match.group(1)
    for i in dint.split('-'):
        if i.startswith('v' or 'V'):
            tag=i[i.upper().index('V')+1:]
            break
    return dint,tag

def get_new_tag(key):
    newtag=0
    for line in open(sys.argv[2]).readlines():
        if key in line:
            newline=line
            break
    mm=re.search('.*revision=\"(.*)\"',newline.strip())
    newdint=0
    if mm is not None:
        newdint=mm.group(1)
        for j in newdint.split('-'):
            if j.startswith('v' or 'V'):
                newtag=j[j.upper().index('V')+1:]
                break    
    return newtag,newdint

def main():
	if len(sys.argv) != 3:
		print 'please input 2 parameters like: python main.py MT6582-L-PIXI3-5- mt6582-l-pixi3-5-v1.0-tmp.xml'
		sys.exit(1)
	prename = sys.argv[1]
	
	initGitDic()
	getChangeMessage()
        dint,tag=get_default()
	print '******************************'
	print 'repeatList'
	print '******************************'
	#print repeatList
	html = ''
	html +='<?xml version="1.0" encoding="UTF-8"?>\n'
	html +='<projects>\n'
	for key in sorted(resDict.keys()):
                newtag,newdint=get_new_tag(key)
		cVal = resDict.pop(key)
		cValue = cVal[0]#JrdContainer
		if cVal[0] in repeatList:
			count =key.count('/')
			if  count > 1:
				match = re.match('^(.*\/((.*)\/(.*)))$', key)
				lab = '%s-%s' %(match.group(3),match.group(4))
				cValue = lab.upper()
		html +='<project>\n'
		html +='	<name>%s</name>\n' %key
                if newdint==0:
		    html +='	<branch>refs/heads/%s</branch>\n' %dint
                else:
                    html +='	<branch>refs/heads/%s</branch>\n' %newdint
                if newtag==0:
		    html +='	<baseline>%s%s-P%s</baseline>\n' %(prename,cValue,tag)
                else:
                    html +='	<baseline>%s%s-P%s</baseline>\n' %(prename,cValue,newtag)
		html +='</project>\n'	
	html +='</projects>'
	f = open ('projectConfig.xml','w')
	f.write(html)		

if __name__ == '__main__':
	main()

