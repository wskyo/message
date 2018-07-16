#!/usr/bin/python

############################################################################
## check the lunch files whether have been changed.
## add by xueqin for notice create 2016-7-1
###########################################################################
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import re
import datetime
import tempfile
sys.path.append('/local/int_jenkins/lib')
from pyExcelerator import *
import os.path
import xlrd
from commands import *
import commands
from Utils import *
from Config import *
from xlrd import xldate_as_tuple

class CheckLunch:
	def __init__(self):
		self.prjconf_allowdiffer_count = 0
		

	def getProjectConfigDict(self):
		xls_path = '/local/int_jenkins/checklunch/conf/%s.xls' %self.project
		sheet_name = 'ProjectConfig'

		workbook = xlrd.open_workbook(xls_path)
		sheet = workbook.sheet_by_name(sheet_name)
		rows_count = sheet.nrows
		cols_count = sheet.ncols
		self.prjconf_allowdiffer_count = rows_count-1

		project_name_row = sheet.row_values(0)
		module_name_col = sheet.col_values(0)

		allow_differ_dic = {}
		for i in range(cols_count-1):
			project_name = project_name_row[i+1].strip()
			project_col_num = i + 1
	
			module_dic = {}
			for i in range(rows_count-1):
				module_name = module_name_col[i+1].strip()
				value = sheet.cell(i+1, project_col_num).value.strip()
				module_dic[module_name]=value

			allow_differ_dic[project_name]=module_dic

		#print '---allow_differ_dic---%s' %allow_differ_dic
		#return '---allow_differ_dic---%s' %allow_differ_dic
		return allow_differ_dic

	def get_prjconf_allowdiffer_count_num(self):
        	return self.prjconf_allowdiffer_count



	def getProjectConfigDic(self,codeDir,needCompareDir):
		prjconfDir = codeDir + '/device/jrdchz/' + needCompareDir
		filepath = prjconfDir + '/ProjectConfig.mk'
		#print filepath
		config_dic = {}
		if os.path.exists(filepath):
			f = open(filepath,'r')
			lines = f.readlines()
			for line in lines:
				if (line.startswith('#') or line.startswith('\n')):
					continue
				else:
					if "#" in line.strip():
						l = line.split('#')[0]
						strlist = l.strip().split('=')
						conf_key = strlist[0].strip()
						conf_value = strlist[1].strip()
						config_dic[conf_key] = conf_value
					else:
						strlist = line.strip().split('=')
						conf_key = strlist[0].strip()
						conf_value = strlist[1].strip()
						config_dic[conf_key] = conf_value
			return config_dic
		else:
			print 'Error: Can\'t get result dir!!! Please check dir!!!'
			sys.exit()


	def getSameKeyDiffValueList(self,dic1,dic2):
		samekey_diffvalue_list = []
		samekey_diffvalue_list = [k for k in set(dic1)&set(dic2) if dic1.get(k) != dic2.get(k)] 
		return samekey_diffvalue_list


	def createSameKeyDic(self,samekey_diffvalue_list,dic):
		samekey_diffvalue_dic = {}
		for key in samekey_diffvalue_list:
			samekey_diffvalue_dic[key] = dic[key]
		return samekey_diffvalue_dic


	def getSideKeySet(self,dic1,dic2):
		sidekey_set = set(dic1)^set(dic2)
		return sidekey_set

	def createSideKeyDic(self,sidekey_set,dic):
		sidekey_dic = {}
		for key in sidekey_set:
			if key in dic.keys():
				sidekey_dic[key] = dic[key]
			else:
				sidekey_dic[key] = "noexsist"
		return sidekey_dic

	def isNeedLunchNotice(self,allow_differ_dic,code_host_dic,code_tf_dic):
		flag = ''
		allowkey_h_have_delete = {}
		hostcodekey_have_add = {}
		allowkey_h_have_change = {}
		hosecodekey_have_change = {}
		allowkey_tf_have_delete = {}
		tfcodekey_have_add = {}
		allowkey_tf_have_change = {}
		tfcodekey_have_change = {}

		codehostcount = len(code_host_dic)
		codetfcount = len(code_tf_dic)
		#print allow_differ_dic
		for key in allow_differ_dic.keys():
			allow_count = len(allow_differ_dic[key])
			#print allow_count
			#print
			if (key == 'pixi4_4_host'):
				differ_all_set = set(allow_differ_dic[key].items())^set(code_host_dic.items())
				#print '---differ_all_set---%s' %differ_all_set
				if (len(differ_all_set)=='0'):
					flag = 'false'
				else:
					flag = 'true'
					sidekey = set(allow_differ_dic[key])^set(code_host_dic)
					for k in sidekey:
						if k in allow_differ_dic[key].keys():
							allowkey_h_have_delete[k] = allow_differ_dic[key][k]
						else:
							hostcodekey_have_add[k] = code_host_dic[k]

					samekey_diffvalue_list = [k for k in set(allow_differ_dic[key])&set(code_host_dic) if allow_differ_dic[key].get(k) != code_host_dic.get(k)]
					for sk in samekey_diffvalue_list:
						allowkey_h_have_change[sk] = allow_differ_dic[key][sk]
						hosecodekey_have_change[sk] = code_host_dic[sk]

			if (key == 'pixi4_4_tf'):
				differ_all_set = set(allow_differ_dic[key].items())^set(code_tf_dic.items())
				#print '---differ_all_set---%s' %differ_all_set
				if (len(differ_all_set)=='0'):
					flag = 'false'
				else:
					flag = 'true'
					sidekey = set(allow_differ_dic[key])^set(code_tf_dic)
					for k in sidekey:
						if k in allow_differ_dic[key].keys():
							allowkey_tf_have_delete[k] = allow_differ_dic[key][k]
						else:
							tfcodekey_have_add[k] = code_tf_dic[k]

					samekey_diffvalue_list = [k for k in set(allow_differ_dic[key])&set(code_tf_dic) if allow_differ_dic[key].get(k) != code_tf_dic.get(k)]
					for sk in samekey_diffvalue_list:
						allowkey_t_have_change[sk] = allow_differ_dic[key][sk]
						tfcodekey_have_change[sk] = code_tf_dic[sk]
		return flag,allowkey_h_have_delete,hostcodekey_have_add,allowkey_h_have_change,hosecodekey_have_change,allowkey_tf_have_delete,tfcodekey_have_add,allowkey_tf_have_change,tfcodekey_have_change
		

















