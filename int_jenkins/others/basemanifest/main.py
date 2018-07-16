#!/usr/bin/python

############################################################################
## add by shie.zhao  create 2017-08-08
###########################################################################

import sys
import os
import re
import commands
import xml.dom.minidom
import glob
import string

def main():
	if len(sys.argv) != 4:
		print 'please input 3 parameters like: python main.py git_list.txt mtk6739 mtk6739-n-v1.0-import  or  python main.py t-alps-release-o1.bsp_P5.xml mtk6737 alps-release-o1.bsp-default '
		sys.exit(1)
	gitlist = sys.argv[1]
	patform = sys.argv[2]
        branch = sys.argv[3]
        print "begin to create manifest"

        if 'xml' in gitlist:
           destDom = xml.dom.minidom.Document()
           manifestNode = destDom.createElement('manifest')
           destDom.appendChild(manifestNode)
           dom = xml.dom.minidom.parse('%s' % gitlist)
           remoteList = dom.getElementsByTagName('remote')
           if len(remoteList) == 1:
		remoteNode = remoteList[0]               
                remoteNode.setAttribute('fetch', 'git@10.92.32.10:')
                remoteNode.setAttribute('name', 'jgs')
                remoteNode.setAttribute('review', 'http://10.92.32.10:8081')
                newNode = destDom.importNode(remoteNode, True)	
		manifestNode.appendChild(newNode)

           else:
		print "Error: more than one 'remote' in %s" % gitlist
		sys.exit(1)

           defaultList = dom.getElementsByTagName('default')
           if len(defaultList) == 1:
		DefaultNode = defaultList[0]
                DefaultNode.setAttribute('remote', 'jgs')
                DefaultNode.setAttribute('revision', '%s' %branch)
                DefaultNode.setAttribute('sync-j', '4')	
                DefaultNode.setAttribute('sync-c', 'true')
                newNode = destDom.importNode(DefaultNode, True)		
		manifestNode.appendChild(newNode)
           else:
		print "Error: more than one 'default' in %s" % gitlist
		sys.exit(1)


           projList = dom.getElementsByTagName('project')
           for proj in projList:
		projName = proj.getAttribute('name')
		projPath = proj.getAttribute('path')
		projRevision = proj.getAttribute('revision')
                projGroups = proj.getAttribute('groups')
                projClone = proj.getAttribute('clone-depth')
                projupstream = proj.getAttribute('upstream')
		newNode = destDom.importNode(proj, True)
                if projRevision != '':
		   newNode.removeAttribute('revision')
                if projGroups != '' :
                   newNode.removeAttribute('groups')
                if projClone != '':
                   newNode.removeAttribute('clone-depth')
                if projupstream != '':
                   newNode.removeAttribute('upstream')
                if projPath == '':
                   projPath = projName
                projName = patform + "/" + projPath
 
                newNode.setAttribute('name',projName)
                newNode.setAttribute('path',projPath)
		manifestNode.appendChild(newNode)

           #add modem git
           #modemNode = destDom.createElement('project')
           #modemname = patform + "/modem/LWTG"
           #modemNode.setAttribute('name',modemname)
           #modemNode.setAttribute('path',"modem/LWTG")
           #newNode = destDom.importNode(modemNode, True)	
           #manifestNode.appendChild(newNode)

           #modemNode = destDom.createElement('project')
           #modemname = patform + "/modem/C2K"
           #modemNode.setAttribute('name',modemname)
           #modemNode.setAttribute('path',"modem/C2K")
           #newNode = destDom.importNode(modemNode, True)	
           #manifestNode.appendChild(newNode)

           xmlExisting = False
           workDir=os.getcwd()
           manifest="%s.xml" %branch
           if os.path.isfile('%s' % (manifest)):
		os.system('rm -f %s' % (manifest))
           fp = file('%s' % (manifest), 'w+')
           for line in destDom.toprettyxml(indent='  ', newl='\n', encoding='utf-8').split('\n'):
		if line and not re.match('^\s*$', line):
			fp.write('%s\n' % line)
           fp.close()
           print "%s has been created" %manifest

        else:
	   html = ''
	   html +='<?xml version="1.0" encoding="UTF-8"?>\n'
	   html +='<manifest>\n'
	   html +='  <remote fetch="git@10.92.32.10:" name="jgs" review="http://10.92.32.10:8081"/>\n'
	   html +='  <default remote="jgs" revision="%s" sync-j="4" sync-c="true"/>\n' %branch
	   for line in file(gitlist).readlines():
                #print line
                line = line.strip('\n')
                line = line.strip('\/')
                html +='  <project name="%s/%s" path="%s" />\n' %(patform,line,line)
	   html +='</manifest>'
	   manifest="%s.xml" %branch
	   print "%s has been created" %manifest
	   f = open(manifest,'w')
	   f.write(html)		

if __name__ == '__main__':
	main()

