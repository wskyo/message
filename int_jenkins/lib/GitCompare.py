#!/usr/bin/python
##################################################
# compare file or dir of two manifest or commit id
##################################################

import sys
import os
import re
from sd3int import *
from commands import *

class GitCompare:
	_oldProjectPath = {}
	_newProjectPath = {}
	_oldDictionary = {}
	_newDictionary = {}

	def __init__(self, oldxml, newxml):
		self.oldxml = oldxml
		self.newxml = newxml
		self.compileXml()

	def debug(self):
		print '---------GitCompare----------'
		print 'oldxml=',self.oldxml
		print 'newxml=',self.newxml
		print '_oldDictionary=',self._oldDictionary
		print '_newDictionary=',self._newDictionary
		print '_oldProjectPath=',self._oldProjectPath
		print '_newProjectPath=',self._newProjectPath
		print '------------------------------'

	def _operateXml(self, fileName):
		fp = open(fileName, 'r')
		tmpDictionary1 = {}
		tmpDictionary2 = {}
		regex1 = r'<project\s+name=\"(?P<g1>[^\"]+)\"\s+path=\"(?P<g2>[^\"]+)\"\s+revision=\"(?P<g3>[^\"]+)\"'
		regex2 = r'refs\/tags\/(?P<g1>.+)'
		for line in fp.readlines():
#			print line,
			if re.search(regex1, line):
				m = re.search(regex1, line)
				project = m.group('g1')
				path = m.group('g2')
				revision = m.group('g3')
				tmpDictionary2[project] = path
				if re.search(regex2, revision):
					n = re.search(regex2, revision)
					tmpDictionary1[path] = n.group('g1')
				else:
					tmpDictionary1[path] = revision
		fp.close()

		return (tmpDictionary1, tmpDictionary2)

	def compileXml(self):
		if not os.path.isfile(self.oldxml):
			print 'Error: the xml path wrong:',self.oldxml
			sys.exit(1)
		if not os.path.isfile(self.newxml):
			print 'Error: the xml path wrong:',self.newxml
			sys.exit(1)
		(self._oldDictionary, self._oldProjectPath) = self._operateXml(self.oldxml)
		(self._newDictionary, self._newProjectPath) = self._operateXml(self.newxml)

	def printInfo(self, path):
		print 'operate dir:===================>'+path

	def hasDiffofStructure(self, commitId1, commitId2, path='/tmp/', include=[], exclude=[]):
		tmpdir = os.getcwd()
		try:
			os.chdir(path)
		except:
			print 'Error: you give the wrong dir:',path
			sys.exit(1)

		self.printInfo(path)

		cmd1 = 'git ls-tree -r --name-status '+commitId1
		cmd2 = 'git ls-tree -r --name-status '+commitId2
		(status1, output1) = getstatusoutput(cmd1)
		(status2, output2) = getstatusoutput(cmd2)
		list1 = output1.split('\n')
		list2 = output2.split('\n')
		os.chdir(tmpdir)
		if len(include)>0 and len(exclude)>0:
			print 'Error: you can just operate include or exclude suffix only!'
			sys.exit(1)
		elif len(include)>0:
			iclist1 = []
			iclist2 = []
			for ic in include:
				regex = r'.+\.'+ic+'$'
				for l1 in list1:
					if re.match(regex, l1) != None:
						iclist1.append(l1)
				for l2 in list2:
					if re.match(regex, l2) != None:
						iclist2.append(l2)
			list1 = iclist1
			list2 = iclist2
		elif len(exclude)>0:
			eclist1 = []
			eclist2 = []
			for l1 in list1:
				flag = True
				for ec in exclude:
					regex = r'.+\.'+ec+'$'
					if re.match(regex, l1) != None:
						flag = False
						break
				if flag:
					eclist1.append(l1)
			for l2 in list2:
				flag = True
				for ec in exclude:
					regex = r'.+\.'+ec+'$'
					if re.match(regex, l2) != None:
						flag = False
						break
				if flag:
					eclist2.append(l2)
			list1 = eclist1
			list2 = eclist2

		list1.sort()
		list2.sort()

		if len(list1) != len(list2):
			return (True, list1, list2)
		else:
			for i, str in enumerate(list1):
				if str != list2[i]:
					return (True, list1, list2)
			return (False, list1, list2)
		

	def hasDiffofDir(self, commitId1, commitId2, path='/tmp/'):
		tmpdir = os.getcwd()
		if os.path.isdir(path):
			os.chdir(path)
		else:
			print 'Error: you give the wrong dir:',path
			sys.exit(1)

		self.printInfo(path)

		cmd = 'git diff --name-only '+commitId1+' '+commitId2
		print 'command:',cmd
		(status, output) = getstatusoutput(cmd)
		os.chdir(tmpdir)
		if status != 0:
			print 'Error: command \'',cmd,'\'!'
			sys.exit(1)

		if output != '':
			return (True, output.split('\n'))
		else:
			return (False, [])

	def hasDiffofNormalFile(self, commitId1, commitId2, filePath):
		tmpdir = os.getcwd()
		if not os.path.isfile(filePath):
			print 'Error: the file:',filePath,' is not exists!'
			sys.exit(1)

		path = os.path.split(filePath)[0]
		fileName = os.path.split(filePath)[1]
		os.chdir(path)

		self.printInfo(path)

		cmd = 'git diff '+commitId1+' '+commitId2+' '+fileName
		print 'command:',cmd
		(status, output) = getstatusoutput(cmd)
		os.chdir(tmpdir)
		if status != 0:
			print 'Error: command \'',cmd,'\'!'
			sys.exit(1)
		if output != '':
			return (True, output)
		else:
			return (False, output)

	def hasDiffofZip(self, commitId1, commitId2, path):
		tmpdir = os.getcwd()
		if os.path.isfile(path):
			filePath = os.path.split(path)[0]
			fileName = os.path.split(path)[1]
		else:
			print 'Error: the zip file path \'',path,'\' wrong.'
			sys.exit(1)

		self.printInfo(filePath)
		os.chdir(filePath)
		regex = r'.+\s(?P<g1>\w{40}).+'
		oldplfId = ''
		oldList = []
		newplfId = ''
		newList = []
		randomDir = os.tmpnam()
		docmd('mkdir '+randomDir)
		old = getoutput('git ls-tree '+commitId1+' '+fileName)
		new = getoutput('git ls-tree '+commitId2+' '+fileName)
		if re.search(regex, old):
			m = re.search(regex, old)
			oldplfId = m.group('g1')
			result1 = getoutput('/bin/bash -c "git cat-file -p '+oldplfId+' > '+randomDir+'/a.zip "')
		if re.search(regex, new):
			m = re.search(regex, new)
			newplfId = m.group('g1')
			result1 = getoutput('/bin/bash -c "git cat-file -p '+newplfId+' > '+randomDir+'/b.zip "')
		oldList = getoutput('unzip -l '+randomDir+'/a.zip').split('\n')
		newList = getoutput('unzip -l '+randomDir+'/b.zip').split('\n')
		os.chdir(tmpdir)
		docmd('rm -rf '+randomDir)
		if len(oldList) == len(newList) and len(oldList) > 4:
			for index in range(3,len(oldList)-2):
#				print 'oldList=',oldList[index][28:]
				if oldList[index][28:] != newList[index][28:]:
					return True
			return False
		else:
 			return True

	def hasDiffofXmlorPlf(self, commitId1, commitId2, path, xp='xml'):
		tmpdir = os.getcwd()
		if xp != 'xml' and xp != 'plf':
			print 'Error: you give the wrong file description.'
			print 'WARNING: hasDiffofXmlorPlf(self, commitId1, commitId2, path, xp=\'<xml|plf>\')'
			sys.exit(1)
		if os.path.isfile(path):
			filePath = os.path.split(path)[0]
			fileName = os.path.split(path)[1]
			os.chdir(filePath)
		else:
			print 'Error: the '+xp+' file path is wrong \''+path+'\'.'
			sys.exit(1)

		self.printInfo(filePath)
		regex = r'.+\s(?P<g1>\w{40}).+'
		fileList1 = []
		oldplfId = ''
		fileList2 = []
		newplfId = ''
		old = getoutput('git ls-tree '+commitId1+' '+fileName)
		new = getoutput('git ls-tree '+commitId2+' '+fileName)
		if re.search(regex, old):
			m = re.search(regex, old)
			oldplfId = m.group('g1')
			result1 = getoutput('git cat-file -p '+oldplfId)
			if xp == 'xml':
				fileList1 = re.findall(r'<[^!].+?>', result1)
			else:
				fileList1 = re.findall(r'<.+?>', result1)
		if re.search(regex, new):
			m = re.search(regex, new)
			newplfId = m.group('g1')
			result2 = getoutput('git cat-file -p '+newplfId)
			if xp == 'xml':
				fileList2 = re.findall(r'<[^!].+?>', result2)
			else:
				fileList2 = re.findall(r'<.+?>', result1)

		os.chdir(tmpdir)
		if fileList1 == fileList2:
			return False
		else:
			return True

	def __getFilesorDirsofDir(self, commitId1, commitId2, path, flag=0):
		tmpdir = os.getcwd()
		if os.path.isdir(path):
			os.chdir(path)
		else:
			print 'Error: the path is wrong \''+path+'\'.'
			sys.exit(1)

		allList1 = []
		fileList1 = []
		dirList1 = []
		allList2 = []
		fileList2 = []
		dirList2 = []
		cmd1 = 'git ls-tree --name-only '+commitId1
		cmd2 = 'git ls-tree --name-only '+commitId2

		allList1 = getoutput(cmd1).split('\n')
		allList2 = getoutput(cmd2).split('\n')

		for element in allList1:
			if os.path.isdir(element):
				dirList1.append(element)
			else:
				fileList1.append(element)

		for element in allList2:
			if os.path.isdir(element):
				dirList2.append(element)
			else:
				fileList2.append(element)

		os.chdir(tmpdir)
		if flag == 0:
			return (allList1, allList2)
		elif flag == 1:
			return (fileList1, fileList2)
		elif flag == 2:
			return (dirList1, dirList2)
		else:
			return (allList1, allList2, fileList1, fileList2, dirList1, dirList2)

	def getFilesofDir(self, commitId1, commitId2, path):
		return self.__getFilesorDirsofDir(commitId1, commitId2, path, 1)

	def getDirsofDir(self, commitId1, commitId2, path):
		return self.__getFilesorDirsofDir(commitId1, commitId2, path, 2)

	def getAllofDir(self, commitId1, commitId2, path):
		return self.__getFilesorDirsofDir(commitId1, commitId2, path, 0)

	def getCommitByPath(self, path):
		commitId1 = self._oldDictionary[path]
		commitId2 = self._newDictionary[path]
		return (commitId1, commitId2)


	def getCommitByProject(self, project):
		if self._oldProjectPath != self._newProjectPath:
			difflist = []
			oldkeys = self._oldProjectPath.keys()
			for key, value in self._newProjectPath.items():
				if self._oldProjectPath.has_key(key):
					oldkeys.remove(key)
					if value != self._oldProjectPath[key]:
						difflist.append('    x[new:old] '+key+':'+value+' => '+key+':'+self._oldProjectPath[key])
				else:
					difflist.append('    +[new]     '+key+':'+value)
			if len(oldkeys) > 0:
				for key in oldkeys:
					difflist.append('    -[new]     '+key+':'+self._oldProjectPath[key])
			print '------------------------------------------'
			print 'WARINING: It\'s diff of two manifest file.'
			print '\n'.join(difflist)
			print '------------------------------------------'

			commitId1 = ''
			commitId2 = ''
			if self._oldProjectPath.has_key(project):
				path1 = self._oldProjectPath[project]
				commitId1 = self._oldDictionary[path1]
			if self._newProjectPath.has_key(project):
				path2 = self._newProjectPath[project]
				commitId2 = self._newDictionary[path2]
			return (commitId1, commitId2)
		else:
			path = self._newProjectPath[project]
			return self.getCommitByPath(path)


if __name__ == '__main__':
	fc = GitCompare('/tmp/manifest/manifest/int/deliv/v23A.xml', '/tmp/manifest/manifest/int/deliv/v239.xml')
#	fc = GitCompare('/tmp/manifest/manifest/int/deliv/v112.xml', '/tmp/manifest/manifest/int/deliv/v113.xml')
#	fc.compileXml()
#	fc.debug()
#	fc.hasDiffofStructure('31fb56e043a93eb70524c019a11cb4a138ef1ac0','93b33036da50ee9c6f6e3387e4235f4a6e793cf7', '/local/build/v264/packages/apps/Email/',exclude=['java','xml','png','html','txt'])
#	fc.ifPersoofOpal('/local/build/v264/')
#	fc.hasDiffofZip('3331a9421fe8a0e8973d4b9bb90246d3a3b00f41', 'c7f08ba4a716863b0d9d90accae16e5e9ce31996', '/local/build/v264/opal_wimdata_ng/wcustores/Audios/audios.zip')
#	fc.hasDiffofXmlorPlf('31fb56e043a93eb70524c019a11cb4a138ef1ac0','93b33036da50ee9c6f6e3387e4235f4a6e793cf7', '/local/build/v264/packages/apps/Email/res/values/arrays.xml')	
#	(m,n) = fc.getCommitByProject('qaep/bionic')
	(m, n) = fc.getDirsofDir('31fb56e043a93eb70524c019a11cb4a138ef1ac0','93b33036da50ee9c6f6e3387e4235f4a6e793cf7', '/local/build/v264/packages/apps/Email/res')
	print m


