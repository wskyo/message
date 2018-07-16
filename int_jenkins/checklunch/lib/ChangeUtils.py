#!/usr/bin/python
#coding=utf-8

import sys
import os
import re
import commands
import xml.dom.minidom
from Utils import *
from Config import *
from UserInfo import *
import glob

class ChangeUtils:
	gitComment = []
	curDict = {}
	lastDict = {}
	haveChangeCommit = []
	

	isMergeCommit = False
	nChanged = 0
	defRemote = None
	authorStr = ''
	dateStr = ''

	def getChangeList(self, conf):
		html = ''
		html += '<p><b>Config Change List:</b></p>'
		html += '<p>'

		changedFileInfoList = []
		self.initGitDic(conf)
		html += self.getChangeMessage(changedFileInfoList, conf)
		if len(self.curDict):
			html += 'Project added:<br />'
			nCount = 0 
			for key in sorted(self.curDict.keys()):
				nCount += 1
				html += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%d) %s<br />' % (nCount, key)
		html += '<br />'
		if len(self.lastDict):
			html += 'Project removed:<br />'
			nCount = 0 
			for key in sorted(self.lastDict.keys()):
				nCount += 1
				html += '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;%d) %s<br />' % (nCount, key)
		html += '</p>'
		popdir()
		## must check before build code 
		if self.nChanged == 0 and conf.getConf('version','curret version') != conf.getConf('baseversion','base version') and conf.getConf('exitnonewchange', 'Exit if no new change from last version <yes|no>', 'yes') == 'yes':
			print '========================================'
			print '!!! NO NEW CHANGE SINCE LAST VERSION !!!'
			print '========================================'
			sys.exit(1)
		return html


	####get manifest version git and revision
	def initGitDic(self, conf):
		maniPrefix = conf.getConf('manifestprefix', 'Prefix dir for manifest files')
		#print "maniPref=" + maniPrefix
		curManifest = conf.getConf('curmanifest', 'Current manifest file', '.repo/manifests/'+maniPrefix+'v'+conf.getConf('version', 'project current version')+'.xml')
		lastManifest = conf.getConf('lastmanifest', 'Base manifest file', '.repo/manifests/'+maniPrefix+'v'+conf.getConf('baseversion', 'project base version')+'.xml')
		for line in file(curManifest).readlines():
			match = re.search('<default\s+remote\s*=\s*\"([^\"]+)\"/>', line)
			if match:
				self.defRemote = match.group(1)
		for line in file(curManifest).readlines():
			match = re.search('<project\s+name=\"([^\"]+)\"\s+path=\"([^\"]+)\"\s+revision=\"([^\"]+)\"', line)
			if match and match.group(2).strip() == 'device':
				self.curDict[match.group(2).strip()] = [match.group(1).strip(), match.group(3).strip()]
				break
		for line in file(lastManifest).readlines():
			match = re.search('<project\s+name=\"([^\"]+)\"\s+path=\"([^\"]+)\"\s+revision=\"([^\"]+)\"', line)
			if match and match.group(2).strip() == 'device':
				self.lastDict[match.group(2).strip()] = [match.group(1).strip(), match.group(3).strip()]
				break
		#print '---self.defRemote---%s' %self.defRemote
		#print '---self.curDict---%s' %self.curDict
		#print '---self.lastDict---%s' %self.lastDict
		#exit(0)
	


	
	####get sdm change, apk change, update patch 
	def getChangeMessage(self, changedFileInfoList, conf):
		html = ''
		#html += "<script> function toggle(id,key){ var show=document.getElementById(id).style.display;if(show=='none'){document.getElementById(id).style.display='block';document.getElementById(key).innerHTML='[Commit Details Hide]'} else{document.getElementById(id).style.display='none';document.getElementById(key).innerHTML='[Commit Details]'}}</script>"
		#print "cur dict"
		#print self.curDict
		self.baselineEmail = False
		for key in sorted(self.curDict.keys()):
			if key in self.lastDict.keys():
				curVal = self.curDict.pop(key)
				lastVal = self.lastDict.pop(key)
				if curVal[1] != lastVal[1]:
					pushdir(key) ###cd git path
					revListStr = commands.getoutput('git rev-list %s..%s' % (lastVal[1], curVal[1])).strip()
					#print revListStr
					tagListStr = commands.getoutput('git show-ref --dereference --tags').strip()
					reviewChangesDict = {} ###user to get remote review change
					if self.defRemote: ### if git is remote
						for changeLine in commands.getoutput('git ls-remote %s refs/changes/*' % self.defRemote).split('\n'):
							match = re.search('([0-9a-f]{40})\s+refs/changes/\d+/(\d+)/\d+', changeLine)
							if match:
								reviewChangesDict[match.group(1)] = match.group(2)
					if revListStr:
						#self.nChanged += 1
						#html += '%d) %s<br />' % (self.nChanged, key) ##number and git name
						#idIndex=1
						for commit in revListStr.split('\n'):
							commit = commit.strip()
							configfilelist = ['ProjectConfig.mk','device.mk']
							for filename in configfilelist:
								#print filename					
								teststr = commands.getoutput('git show %s ./jrdchz/pixi4_4_*/%s' %(commit,filename)).strip()
								#print '---teststr---%s' %teststr
								if teststr == '':
									#print 'this commit have no modification about device.mk or ProjectConfig.mk'
									pass
								else: 
									self.haveChangeCommit.append(commit)
									self.nChanged += 1
									html += '%d) %s<br />' % (self.nChanged, filename) ##number and git name
									if re.match('^qaep/*',curVal[0]):
										curVal[0]=curVal[0][5:]
									if re.match('^sdd1/*',curVal[0]):
										temcurVal=curVal[0][5:]
										commitUrl = 'http://10.92.32.10/sdd1/gitweb-sdd1-all/?p=%s.git;a=commit;h=%s' % (temcurVal, commit)
									else:
										commitUrl = 'http://10.92.32.10/gitweb.cgi?p=%s.git;a=commit;h=%s' % (curVal[0], commit)  #modify by zhaoshie 20150320
									if commit in reviewChangesDict.keys():
										reviewUrl = 'http://10.92.32.10:8081/#change,%s' % reviewChangesDict[commit]
									else:
										reviewUrl = ''
									if not re.match('[0-9a-f]{40}', commit):
										continue
									firstComment = ''
									##########git log method init changedFileInfolist
									self.getGitLog(changedFileInfoList, commit, firstComment,commitUrl)
									##########get gitcommands 
									html += self.getGitCreateChangeMes(changedFileInfoList, curVal, firstComment, reviewUrl, tagListStr, commitUrl, commit, conf, key)

									#html += '<tr><td>'+'<span id=\'show'+str(self.nChanged)+'\' onclick=\"toggle(\'comment'+str(self.nChanged)+'\',\'show'+str(self.nChanged)+'\');\" style="cursor:pointer;color:#FFCC33">[Commit Details]</span></td></tr>'
									#html += '<tr><td><div id=\'comment'+str(self.nChanged)+'\' style="display:none;background-color:#FFCC33">'+teststr+'<span></div></td></tr>'


							
						html += '<br />'
					popdir()
		return html

	def getGitLog(self, changedFileInfoList, commit, firstComment,commitUrl):
		gitLog = commands.getoutput('git log -n1 --raw %s' % commit.strip())
		self.isMergeCommit = False
		self.changeApkAndSmdInfoList=[]
		self.gitComment=[]
		for line in gitLog.split('\n'):
			match = re.match('^\s\s\s\s(.*)', line)
			if match:
				if not firstComment:
					firstComment = match.group(1)
				self.gitComment.append(match.group(1))
			match = re.match('^Author:\s(.+)', line)
			if match:
				self.authorStr = match.group(1).strip()
			match = re.match('^Date:\s(.+)', line)
			if match:
				self.dateStr = match.group(1).strip()
			match = re.match('^Merge:\s', line)
			if match:
				self.isMergeCommit = True
			match = re.match(':(\w{6})\s(\w{6})\s(\w{7})\.\.\.\s(\w{7})\.\.\.\s([AMD])\s+(.+)', line)
			if match:
				if match.group(5) == 'M':
					tmpActStr = 'Update'
				if match.group(5) == 'A':
					tmpActStr = 'Add'
				if match.group(5) == 'D':
					tmpActStr = 'Delete'
				changedFileInfoList.append({'filename':match.group(6), 'action':tmpActStr, 'last_commit':match.group(3), 'current_commit':match.group(4),'commit':str(commit),'author':self.authorStr,'commitUrl':commitUrl})
				self.changeApkAndSmdInfoList.append({'filename':match.group(6), 'action':tmpActStr,'date':self.dateStr,'commit':str(commit),'author':self.authorStr})

	def getGitCreateChangeMes(self,changedFileInfoList, curVal, firstComment, reviewUrl, tagListStr, commitUrl, commit, conf, key):

		bugNumber = ''
		authoremail = ''
		prStrFixedList = []
		goodComment = ''
		moduleImpact = ''
		testSuggestion = ''
                rootcauseDetail = ''
		menutreeiamge = ''
                rootcause = ''
                Solution = ''
		commitDesc= ''
		tagList = []
		tagInDescStr = ''
		for line in self.gitComment:
			match = re.search('###%%%bug\snumber:(.+)', line)
			if not self.isMergeCommit and match:
				bugNumber = match.group(1).strip()
				if bugNumber.__contains__("###%%%"):
					bugNumber = (bugNumber.split('###%%%')[0]).strip()

			match = re.search('###%%%comment:(.+)', line)
			if match:
				goodComment = match.group(1).strip()
				if goodComment.__contains__("###%%%"):
					goodComment = (goodComment.split('###%%%')[0]).strip()
			match = re.search('###%%%Module_Impact:(.+)', line)
			if match:
				moduleImpact = match.group(1).strip()
				if moduleImpact.__contains__("###%%%"):
					moduleImpact = (moduleImpact.split('###%%%')[0]).strip()
			match = re.search('###%%%Change Menutree or image:(.+)', line)
			if match:
				menutreeiamge = match.group(1).strip()
				if menutreeiamge.__contains__("###%%%"):
					menutreeiamge = (menutreeiamge.split('###%%%')[0]).strip()
			match = re.search('###%%%Test_Suggestion:(.+)', line)
			if match:
				testSuggestion = match.group(1).strip()
				if testSuggestion.__contains__("###%%%"):
					testSuggestion = (testSuggestion.split('###%%%')[0]).strip()
                        #add by zhaoshie for adding rootcause,solution 20150612
			match = re.search('###%%%root cause:(.+)', line)
			if match:
				rootcause = match.group(1).strip()
				if rootcause.__contains__("###%%%"):
					rootcause = (rootcause.split('###%%%')[0]).strip()
			match = re.search('###%%%root cause detail:(.+)', line)
			if match:
				rootcauseDetail = match.group(1).strip()
				if rootcauseDetail.__contains__("###%%%"):
					rootcauseDetail = (rootcauseDetail.split('###%%%')[0]).strip()
			match = re.search('###%%%Solution:(.+)', line)
			if match:
				Solution = match.group(1).strip()
				if Solution.__contains__("###%%%"):
					Solution = (Solution.split('###%%%')[0]).strip()
                        #end


		#add by lyf,fixed no PR list
		if bugNumber in ['0','00','000','0000','00000','000000']:
			bugNumber = ''
		if bugNumber:
			for bugId in map(lambda x: int(x), re.findall('\d+', bugNumber)):
				if bugId not in self.prFromCodeDict.keys():
					self.prFromCodeDict[bugId] = {'moduleImpact': moduleImpact, 'testSuggestion': testSuggestion,'rootcause': rootcause,'rootcauseDetail': rootcauseDetail,'Solution': Solution,'localPath': set([key]),'menutree_iamge':menutreeiamge}
				else:
					if self.prFromCodeDict[bugId]['moduleImpact'] and self.prFromCodeDict[bugId]['moduleImpact'] != moduleImpact:
						self.prFromCodeDict[bugId]['moduleImpact'] += '\n%s' % moduleImpact
					if self.prFromCodeDict[bugId]['menutree_iamge'] and self.prFromCodeDict[bugId]['menutree_iamge'] != menutreeiamge:
						self.prFromCodeDict[bugId]['menutree_iamge'] += '\n%s' % menutreeiamge
					if self.prFromCodeDict[bugId]['testSuggestion'] and self.prFromCodeDict[bugId]['testSuggestion'] != testSuggestion:
						self.prFromCodeDict[bugId]['testSuggestion'] += '\n%s' % testSuggestion
                                        #add by zhaoshie 20150612
					if self.prFromCodeDict[bugId]['rootcause'] and self.prFromCodeDict[bugId]['rootcause'] != rootcause:
						self.prFromCodeDict[bugId]['rootcause'] += '\n%s' % rootcause
					if self.prFromCodeDict[bugId]['rootcauseDetail'] and self.prFromCodeDict[bugId]['rootcauseDetail'] != rootcauseDetail:
						self.prFromCodeDict[bugId]['rootcauseDetail'] += '\n%s' % rootcauseDetail
					if self.prFromCodeDict[bugId]['Solution'] and self.prFromCodeDict[bugId]['Solution'] != Solution:
						self.prFromCodeDict[bugId]['Solution'] += '\n%s' % Solution
					self.prFromCodeDict[bugId]['localPath'].add(key)

		if bugNumber and goodComment:
			commitDesc = 'Fix PR %s: %s' % (bugNumber, goodComment)
		else:
			#commitDesc = firstComment
			commitDesc = goodComment
		if commitDesc == '':  #add yinfang.lai 2015-03-26
			commitDesc = firstComment

		if commitDesc == '':  #add yinfang.lai 2015-05-04
			commitDesc = self.gitComment[0]

		if (not bugNumber) and (not self.isMergeCommit):
			self.patchWithoutPRList.append([self.authorStr, commitDesc, commitUrl])

		for line in tagListStr.split('\n'):
			match = re.match('^([0-9a-f]{40})\s+refs/tags/([^^]+)', line.strip())
			if match:
				if match.group(1) == commit:
					tagList.append(match.group(2).strip())
		if reviewUrl:
			reviewHtmlCont = '&nbsp;[<a href="%s">review</a>]' % reviewUrl
		else:
			reviewHtmlCont = ''
		if tagList:
			tmpList = []
			tagInDescStr = '&nbsp;('
			for line in tagList:
				tmpList.append(line)
			tagInDescStr += ', '.join(tmpList)
			tagInDescStr += ')'
		#modified by renzhi.yang, add self.authorStr in change list when email release
		html = '&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<a href="%s">%s</a>%s%s----%s<br />' % (commitUrl, commitDesc, reviewHtmlCont, tagInDescStr, self.authorStr)


		#end by renzhi.yang

		strCustStorePath = conf.getConf('custstorepath', 'Custsore path', 'none')
		#add by lyf,fixed no apk list
		strCustStorePath = '%swcustores' %strCustStorePath
		##print "strCustStorePath %s" % strCustStorePath
		if strCustStorePath != 'none' and key == strCustStorePath:
			#modified by renzhi.yang
			##for fileInfoDict in changedFileInfoList:
			for fileInfoDict in self.changeApkAndSmdInfoList:
			#end by renzhi
				match = re.search('\.[aA][pP][kK]', fileInfoDict['filename'])
				if not match:
					continue
				if fileInfoDict['filename'] not in self.apkChangeInfoDict.keys():
					self.apkChangeInfoDict[fileInfoDict['filename']] = {}
				#modified by junbiao.chen 20150105
				#self.apkChangeInfoDict[fileInfoDict['filename']].insert(0, {'action':fileInfoDict['action'], 'url':commitUrl, 'date':self.dateStr, 'author':self.authorStr})
				if 'pr' in self.apkChangeInfoDict[fileInfoDict['filename']].keys() and bugNumber:
					if bugNumber.find(','):
						allBugs=bugNumber.split(',')
						for eachBug in allBugs:
							if eachBug not in self.apkChangeInfoDict[fileInfoDict['filename']]['pr']:
								self.apkChangeInfoDict[fileInfoDict['filename']]['pr'].append(eachBug)
					else:
						self.apkChangeInfoDict[fileInfoDict['filename']]['pr'].append(bugNumber)	
				else:
					if bugNumber:
						if bugNumber.find(','):
							allBugs=bugNumber.split(',')
							self.apkChangeInfoDict[fileInfoDict['filename']]={'action':fileInfoDict['action'],'date':fileInfoDict['date'],'pr':[allBugs[0]]}
                                                	for index in range(1,len(allBugs),1):
								self.apkChangeInfoDict[fileInfoDict['filename']]['pr'].append(allBugs[index])
						else:
							self.apkChangeInfoDict[fileInfoDict['filename']]={'action':fileInfoDict['action'],'date':fileInfoDict['date'],'pr':[bugNumber]}
					else:
						self.apkChangeInfoDict[fileInfoDict['filename']]={'action':fileInfoDict['action'],'date':fileInfoDict['date']}
		#modified by junbiao.chen 20140105
		for fileInfoDict in changedFileInfoList:
			if str(fileInfoDict['commit']) == str(commit):
				match = re.search('\.[pP][lL][fF]', fileInfoDict['filename'])
				if match:
					self.sdmChangedInCommitsBool = True
					## add by ruifeng.dong for sdm FR/CR/PR begin
					if bugNumber:
						if bugNumber.find(','):
							allplfBugs=bugNumber.split(',')
							for eachPlfBug in allplfBugs:
								if eachPlfBug not in prStrFixedList:
									prStrFixedList.append(str(eachPlfBug))
						else:
							prStrFixedList.append(str(bugNumber))
					else:
						prStrFixedList.append("")
					## add by ruifeng.dong for sdm FR/CR/PR end	
					lastPlfDomPass1 = None
					curPlfDomPass1 = None
					try:
						if fileInfoDict['action'] == 'Add':
							curPlfDomPass1 = xml.dom.minidom.parseString(commands.getoutput('git cat-file blob %s' % fileInfoDict['current_commit']).strip())
						if fileInfoDict['action'] == 'Delete':
							lastPlfDomPass1 = xml.dom.minidom.parseString(commands.getoutput('git cat-file blob %s' % fileInfoDict['last_commit']).strip())
						if fileInfoDict['action'] == 'Update':
							lastPlfDomPass1 = xml.dom.minidom.parseString(commands.getoutput('git cat-file blob %s' % fileInfoDict['last_commit']).strip())
							curPlfDomPass1 = xml.dom.minidom.parseString(commands.getoutput('git cat-file blob %s' % fileInfoDict['current_commit']).strip())
					except xml.parsers.expat.ExpatError:
						continue
					#modName = os.path.split(fileInfoDict['filename'])[1]	
					for oneChangeSdm in self.getSdmChangeList(lastPlfDomPass1, curPlfDomPass1):
						tmpKeyName = fileInfoDict['filename']+'/'+oneChangeSdm
						if tmpKeyName not in self.sdmChangeToPRDict.keys():
							self.sdmChangeToPRDict[tmpKeyName] = []
						for onePR in prStrFixedList:
							if not onePR in self.sdmChangeToPRDict[tmpKeyName]:
								self.sdmChangeToPRDict[tmpKeyName].append(str(onePR))
						if tmpKeyName not in self.sdmauthor.keys():
							self.sdmauthor[tmpKeyName] = []
							self.sdmauthor[tmpKeyName].append(str(fileInfoDict['author']))
		for fileInfoDict in self.changeApkAndSmdInfoList:
			if str(fileInfoDict['commit']) == str(commit):
                        	match = re.search('\.[pP][lL][fF]', fileInfoDict['filename'])        
				if not match:
                                        continue
                        	if fileInfoDict['filename'] not in self.plfChangeInfoDict.keys():
                        		self.plfChangeInfoDict[fileInfoDict['filename']] = {}
				if 'pr' in self.plfChangeInfoDict[fileInfoDict['filename']].keys() and bugNumber:
                          		if bugNumber.find(','):
                                		allBugs=bugNumber.split(',')
                                   		for eachBug in allBugs:
                                       			if eachBug not in self.plfChangeInfoDict[fileInfoDict['filename']]['pr']:
                                             			self.plfChangeInfoDict[fileInfoDict['filename']]['pr'].append(eachBug)
                        		else:
                                    		self.plfChangeInfoDict[fileInfoDict['filename']]['pr'].append(bugNumber)
                		else:
                           		if bugNumber:
                                   		if bugNumber.find(','):
                                          		allBugs=bugNumber.split(',')
                                            		self.plfChangeInfoDict[fileInfoDict['filename']]={'action':fileInfoDict['action'],'pr':[allBugs[0]]}
                                             		for index in range(1,len(allBugs),1):
                                             			self.plfChangeInfoDict[fileInfoDict['filename']]['pr'].append(allBugs[index])
                                    		else:
                                          		self.plfChangeInfoDict[fileInfoDict['filename']]={'action':fileInfoDict['action'],'pr':[bugNumber]}
                              		else:
                                   		self.plfChangeInfoDict[fileInfoDict['filename']]={'action':fileInfoDict['action'],}
		html= html.decode('utf-8')
		return html
