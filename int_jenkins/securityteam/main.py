#!/usr/bin/python
#################################################################################################
# sign project from here, if project didn't sign, pls don't process this class
#################################################################################################

import os
import sys

from Utils import *
from Config import *

def main():
	conf = Config();
	conf.addFromArg(sys.argv[1:])
	signProject = conf.getConf('signProject', 'jrd_common')
	## add by laiyinfang for mtk project 2015-11-4
	mtkProject = conf.getConf('mtkProject','mtkProject', 'none')
	docmd('cp /local/int_jenkins/securityteam/%s/signStart.py .' %signProject)
	docmd('cp /local/int_jenkins/securityteam/AutoSign.sh .')
	docmd('chmod a+x signStart.py')
	docmd('chmod a+x AutoSign.sh')
	if mtkProject == 'none':
		docmd('./AutoSign.sh %s' %signProject)
	else:
		docmd('./AutoSign.sh %s %s' %(signProject, mtkProject))
if __name__ == '__main__':
	main()
