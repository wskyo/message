#!/usr/bin/python
#
#for git push of xls 
#
import sys,os
sys.path.append('/local/int_jenkins/lib')
#sys.path.append('/local/int_jenkins/mtk_patch/lib')
from Config import *
import xlrd,xlwt
from xlutils.copy import copy
import commands

class modify_xls:
	def __init__(self,project,number,filename='/local/int_jenkins/mtk_patch/jb3-mp-import.xls'):
		wb = xlrd.open_workbook(filename,formatting_info=True)
		self.project = project
		self.number = number
		self.wb = copy(wb)
		self.ap_st = self.wb.get_sheet(0)#u'MTKInfo'
		self.mp_st = self.wb.get_sheet(1)#u'ModemInfo'
		self.row_list = []
		self.col_list = [23,20,21]
		self.get_prj_from_same_import(wb,project[0])
		self.get_row_from_prj(wb)
	def get_row_from_prj(self,wb):
		ap_st = wb.sheet_by_name(u'MTKInfo')
		mp_st = wb.sheet_by_name(u'ModemInfo')
		for i in xrange(0,len(self.project)):
			ap_row = ''
			mp_row = ''
			row = []
			for _row in xrange(0,ap_st.nrows):
				if ap_st.cell(_row,0).value.strip() == self.project[i]:
					ap_row = _row
					print "ap_row",ap_row
			for _row in xrange(0,mp_st.nrows):
				if mp_st.cell(_row,0).value.strip() == self.project[i]:
					mp_row = _row
					print "mp_row",mp_row
			if ap_row and mp_row:
				row.append(ap_row)
				row.append(mp_row)
				self.row_list.append(row)
	def get_prj_from_same_import(self,wb,prj):
		import_branch = ''
		ap_st = wb.sheet_by_name(u'MTKInfo')
		for _row in xrange(0,ap_st.nrows):
			if ap_st.cell(_row,0).value.strip() == prj:
				import_branch = ap_st.cell(_row,1).value.strip()
		print 'import_branch',import_branch
		if not import_branch:
			print "Cannot load import_branch"
			sys.exit(1)
		for _row in xrange(0,ap_st.nrows):
			_prj = ap_st.cell(_row,0).value.strip()
			_import_branch = ap_st.cell(_row,1).value.strip()
			if _import_branch == import_branch and _prj not in self.project:
				self.project.append(_prj)
				_num = self.number[0]
				self.number.append(_num)
				
	def modify(self):
		print self.row_list,len(self.project)
		for i in xrange(0,len(self.project)):
			#print "i===",i
			assert self.row_list[i][0] and self.row_list[i][1],"wrong row number"
			if self.number[i][0]:
				self.ap_st.write(self.row_list[i][0],self.col_list[0],int(self.number[i][0]))
			if self.number[i][1]:
				self.mp_st.write(self.row_list[i][1],self.col_list[1],int(self.number[i][1]))
			if self.number[i][2]:
				self.mp_st.write(self.row_list[i][1],self.col_list[2],int(self.number[i][2]))
	def save(self,filename='/local/int_jenkins/mtk_patch/jb3-mp-import.xls'):
		self.wb.save(filename)
def main_modify_xls(project,number):
	xls = modify_xls(project,number)
	xls.modify()
	xls.save()

def git_push(filename='mtk_patch/jb3-mp-import.xls'):
	os.chdir('/local/int_jenkins')
	print "change dir =====/local/int_jenkins"
	os.system("> /local/release/git_push.log")
	print commands.getoutput("git status | tee -a /local/release/git_push.log")
	print commands.getoutput("git add %s | tee -a /local/release/git_push.log"%filename)
	print commands.getoutput("git commit -m 'update mtk_patch/jb3-mp-import.xls for dayly update' | tee -a /local/release/git_push.log")
	print commands.getoutput("git push origin master | tee -a /local/release/git_push.log")
	error = commands.getoutput("grep -E 'fatal:|error:' /local/release/git_push.log")
	if error:
		print "====git push error start====!!!"
		print error
		print "====git push error end====!!!"
		sys.exit(1)
def git_reset():
	os.chdir('/local/int_jenkins')
	print "change dir =====/local/int_jenkins"
	print commands.getoutput("git reset --hard HEAD^")
	print commands.getoutput("git pull")
if __name__ == '__main__':
	conf = Config()
	conf.addFromArg(sys.argv[1:])
	project = conf.getConf("project","project name")
	alps = conf.getConf("ALPS","alps number",-1)
	moly = conf.getConf("MOLY","moly number",-1)
	sixth = conf.getConf("SIXTH","sixth number",-1)
	if alps == -1:
		alps = ''
	if moly == -1:
		moly = ''
	if sixth == -1:
		sixth = ''
	print alps,moly,sixth
	if alps or moly or sixth:
		print project,[[alps,moly,sixth]]
		git_reset()
		main_modify_xls([project],[[alps,moly,sixth]])
		git_push()

