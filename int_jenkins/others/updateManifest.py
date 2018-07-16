#!/usr/bin/python
import os
import sys
import xml.dom.minidom
import commands
import re
#/local/code/upload/int_jenkins/versiontool/lib/updateManifest.py yarism-v2.0-fsr.xml test.xml

def main():
	if not os.path.isfile(sys.argv[1]):
		origin_manifest_file=os.getcwd() + '/'+ sys.argv[1]
	else:
		origin_manifest_file=sys.argv[1]
	if not os.path.isfile(origin_manifest_file):
		print "The origin manifest file does not exist"
		sys.exit(1)
	new_file_name =sys.argv[2]
	destDom = xml.dom.minidom.Document()
	manifestNode = destDom.createElement('manifest')
	destDom.appendChild(manifestNode)
	dom = xml.dom.minidom.parse('%s' % origin_manifest_file)
	remoteList = dom.getElementsByTagName('remote')
	manifestRemoteDict = {}
	manifestDefaultDict = {}
	if len(remoteList) == 1:
		remoteNode = remoteList[0]
		if not manifestRemoteDict:
			manifestRemoteDict['fetch'] = remoteNode.getAttribute('fetch')
			manifestRemoteDict['name'] = remoteNode.getAttribute('name')
			manifestRemoteDict['review'] = remoteNode.getAttribute('review')
			newNode = destDom.importNode(remoteNode, True)
			manifestNode.appendChild(newNode)
		else:
			if manifestRemoteDict['fetch'] != remoteNode.getAttribute('fetch') or \
				manifestRemoteDict['name'] != remoteNode.getAttribute('name') or \
				manifestRemoteDict['review'] != remoteNode.getAttribute('review'):
					print "Error: 'remote' mismatch in manifest files"
					sys.exit(1)
	else:
		print "Error: more than one 'remote' in %s" % oneManifest
		sys.exit(1)
	print "manifestRemoteDict",manifestRemoteDict

	##get manifest default
	defaultList = dom.getElementsByTagName('default')
	if len(remoteList) == 1:
		defaultNode = defaultList[0]
		if not manifestDefaultDict:
			manifestDefaultDict['remote'] = defaultNode.getAttribute('remote')
			curManifestDefaultRevision = defaultNode.getAttribute('revision')
			newNode = destDom.importNode(defaultNode, True)
			newNode.removeAttribute('revision')
			manifestNode.appendChild(newNode)
		else:
			if manifestDefaultDict['remote'] != defaultNode.getAttribute('remote'):
				print "Error: 'default' mismatch in manifest files"
				sys.exit(1)
	else:
		print "Error: more than one 'default' in %s" % oneManifest
		sys.exit(1)

	##get manifest project 

	projList = dom.getElementsByTagName('project')
	for proj in projList:
		projName = proj.getAttribute('name')
		projPath = proj.getAttribute('path')
		projRevision = proj.getAttribute('revision')
		if not projRevision:
			projRevision = curManifestDefaultRevision
		if not projRevision:
			print "Error: no revision in %s" % proj
			sys.exit(1)
		headRef = None
		gitUrl = '%s%s' % (manifestRemoteDict['fetch'], projName)
		remoteRefList = commands.getstatusoutput('git ls-remote %s' % gitUrl)
		if remoteRefList[0] >> 8 != 0:
			print 'Error getting head ref in git %s' % projPath
			sys.exit(1)
		tmpList =  remoteRefList[1].split('\n')
		for oneRef in tmpList:
			match = re.match('([0-9a-fA-F]{40})\s+refs/heads/([^/]+)', oneRef)
			if match:
				if match.group(2) == projRevision:
					headRef = match.group(1)
					break
		if not headRef:
			print 'Error: no branch %s in %s' % (projRevision, gitUrl)
			sys.exit(1)
		#for oneRef in tmpList:
			#match = re.match('([0-9a-fA-F]{40})\s+(refs/tags/[^^]+)', oneRef)
			#if match:
				#if match.group(1) == headRef:
					#headRef = match.group(2)
					#break
		print '%s ==> %s' % (gitUrl, headRef)
		newNode = destDom.importNode(proj, True)
		newNode.setAttribute('revision', headRef)
		manifestNode.appendChild(newNode)
	print "manifestDefaultDict",manifestDefaultDict
	print "manifestNode",manifestNode
	xmlExisting = False
	workDir=os.getcwd()
	if os.path.isfile('%s/%s' % (workDir, new_file_name)):
		os.system('rm -f %s/%s' % (workDir, new_file_name))
	fp = file('%s/%s' % (workDir, new_file_name), 'w+')
	for line in destDom.toprettyxml(indent='  ', newl='\n', encoding='utf-8').split('\n'):
		if line and not re.match('^\s*$', line):
			fp.write('%s\n' % line)
	fp.close()

if __name__ == '__main__':
	main()
