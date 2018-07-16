#!/usr/bin/python
# coding=utf-8

############################################################################
## modify SCA.txt automatically for pixi4-4tf efuse version
## add by xueqin.zhang create 2016-11-15
###########################################################################

import os
import sys
import re

def modify_sca(project,version,confname):
	filepath = '/local/release/'+project+'-release/v'+version+'/flashtool/'+confname
	print filepath
	config_dic = {}
	if os.path.exists(filepath):
		f = open(filepath,'r')
		lines = f.readlines()
		#print lines.__len__()
		f.close()

		tarline1 = 0
		tarline2 = 0
		for i in range(lines.__len__()):
			if lines[i].__contains__("seccfg"):
				tarline1 = int(i)+1
				tarline2 = int(i)+2
				#print tarline1
				#print tarline2
				#print lines[tarline1]
				#print lines[tarline2]
		if "NONE" in lines[tarline1]:
			lines[tarline1] = lines[tarline1].replace("NONE","seccfg.bin")
		if "false" in lines[tarline2]:
			lines[tarline2] = lines[tarline2].replace("false","true")
		
		fnew = open(filepath,'w')
		for item in lines:
			fnew.write(item)
		fnew.close()					

	else:
		print 'Error: Can\'t get result dir!!! Please check dir!!!'
		sys.exit()


if __name__ == "__main__":
	project = sys.argv[1]
	version = sys.argv[2]
	confname = sys.argv[3]
	modify_sca(project,version,confname)






