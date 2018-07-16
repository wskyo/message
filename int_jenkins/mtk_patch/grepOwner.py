#!/usr/bin/python
# -*- coding: utf-8 -*-
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.switch_to import SwitchTo
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.common.exceptions import WebDriverException,NoSuchWindowException
import os,re
import imaplib
import email
import sys,locale
#sys.path.append('/local/int_jenkins/lib')
#sys.path.append('/local/int_jenkins/mtk_patch/lib')
import xlrd,xlwt
from xlutils.copy import copy
import commands
class login_mtk:
	def __init__(self,url="https://transfer.mediatek.com"):
		self.url = url
		self.firefox_profile = FirefoxProfile()
		self.set_profile(self.firefox_profile)
		self.driver = webdriver.Firefox(firefox_profile=self.firefox_profile)
		time.sleep(3)
		try:
			self.driver.get(self.url)
		except WebDriverException,e:
			print "--------------------"
			print e
			print "--------------------"
			time.sleep(10)
			self.driver.close()
			print "-----sys exit-------"
			sys.exit(1)
		except NoSuchWindowException,e:
			print "--------------"
			print e
			print "--------------"
			main_network_security()
			self.firefox_profile = FirefoxProfile()
			self.set_profile(self.firefox_profile)
			self.driver = webdriver.Firefox(firefox_profile=self.firefox_profile)
			time.sleep(3)
			self.driver.get(url)

		time.sleep(3)
		self.driver.maximize_window()
		self.email_text = []
		self.owner = []
		self.eserviceid = []
		self.patchs = []
		self.patch_downloaded = False
		self._releasetime = []
		self.releasetime = []
		self.href_list = []
		self._href_list = []
	def set_profile(self,profile):
		#profile.set_preference("browser.download.useDownloadDir",True)
		profile.set_preference("browser.download.dir","/local/sdb/mtk_patch_import/TODO")
		profile.set_preference("browser.download.folderList",2)
		profile.set_preference("browser.download.manager.showWhenStarting",False)
		profile.set_preference("plugin.disable_full_page_plugin_for_types","application/pdf")
		profile.set_preference("pdfjs.disabled",True)
		profile.set_preference("browser.helperApps.neverAsk.saveToDisk","application/x-gzip,application/zip,application/x-gtar,application/vnd.ms-excel,application/x-tar,application/octet-stream,text/csv,application/xml,application/vnd.ms-powerpoint,application/octet-stream,text/plain,video/x-msvideo,video/x-sgi-movie,video/mpeg,application/pdf,image/png,image/jpeg,image/bmp,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.presentationml.presentaton,audio/mpeg")
		profile.set_preference("layout.css.devPixelsPerPx","0.2")
	def login(self,user="susheng.ye.hz@tcl.com",passwd="yss5421789"):
		username = self.driver.find_element_by_name("ctl00$PlaceHolderBody$PlaceHolderMain$txtEmail")
		username.click()
		#time.sleep(1)
		username.send_keys(user)
		#time.sleep(3)
		password = self.driver.find_element_by_name("ctl00$PlaceHolderBody$PlaceHolderMain$txtPwd")
		password.click()
		#time.sleep(1)
		password.send_keys(passwd)
		#time.sleep(3)
		sign = self.driver.find_element_by_name("ctl00$PlaceHolderBody$PlaceHolderMain$btnSign")
		sign.click()
		time.sleep(3)
	def load_history_received(self,url="https://transfer.mediatek.com/History/Received"):
		self.driver.get(url)
		time.sleep(3)
	def grep_table(self):
		tables = self.driver.find_elements_by_css_selector("html body.page-header-fixed.page-footer-fixed.page-sidebar-closed-hide-logo.page-container-bg-solid div.page-container div.page-content-wrapper div.page-content div.portlet.light div.portlet-body div#ShareHistoryTable_wrapper.dataTables_wrapper.form-inline.dt-bootstrap.no-footer div.row div.col-sm-12 table#ShareHistoryTable.dt-responsive.dataTable.no-footer.table.table-bordered.table-striped.table-hover.dtr-inline tbody tr td.dt-fixwidth a")
		#print tables
		#print len(tables)
		for table in tables:
			href = table.get_attribute("href")
			if href not in self.href_list:
				self.href_list.append(href)
		self.href_list = self.href_list[::-1]
		print self.href_list
		assert len(self.href_list)==len(tables),"something wrong happened in access to datatables"
	def get_script(self):
		scripts = self.driver.find_elements_by_tag_name("script")
		for script in scripts:
			print script.get_attribute("type")
	def convert_href_to_get_email_text(self):
		for url in self.href_list:
			if not url:
				continue
			print '----',url,'-----'
			self.get_email_text(url)
			time.sleep(3)
			self.download_all()
	def get_email_text(self,url):
		self.driver.get(url)
		#time.sleep(1)
		
		emails = self.driver.find_elements_by_tag_name("pre")
		
		for email in emails:
			#print email
			
			#print email.text
			if email.text not in self.email_text:
				self.email_text.append(email.text)
		time_class = self.driver.find_element_by_css_selector("html body.page-header-fixed.page-footer-fixed.page-sidebar-closed-hide-logo.page-container-bg-solid div.page-container div.page-content-wrapper div.page-content div.note.note-warning p.font-yellow-gold.pull-right")	
		if time_class:
			print time_class.text
			self._releasetime.append(time_class.text.split()[0])
		#print len(self.email_text),len(self._releasetime)
		#assert len(self.email_text)==len(self._releasetime),'text number cannot equal to releasetime numbers'
	def get_classes(self):
		time_classes = self.driver.find_elements_by_tag_name("div")
		t_class = ''
		for time_class in time_classes:
			try:
				if time_class.get_attribute("class")=="note note-warning":
					print time_class.get_attribute("class")
					t_class = time_class
			except StaleElementReferenceException,e:
				self.get_classes()
		return t_class
	def get_owner_eserviceid(self):
		for i in xrange(0,len(self.email_text)):
			text = self.email_text[i]
			releasetime = self._releasetime[i]
			matchs = ''
			match = ''
			_eserviceid = ''
			_owner = ''
			_patchs = ''
			formate_eservice = r"In\sresponse\sto\seService\srequest\s(\w+)\."
			matchs = re.findall(formate_eservice,text)
			for match in matchs:
				print "In\sresponse\sto\seService\srequest\s(\w+)\.",match
				assert len(matchs)==1,"something wrong happened"
				_eserviceid = match
			matchs = ''
			match = ''
			formate_owner = r"EMAIL:\s(\w+\.?-?\w+?\.?\w+?@\w+\.com)"
			matchs = re.findall(formate_owner,text)
			if len(matchs)>=1:
				print "EMAIL:\s(\w+\.?-?\w+?\.?\w+?@\w+\.com)",matchs
				_owner = matchs[-1]
			matchs = ''
			match = ''
			formate_patchs = r"-\s(\w+_?\w+?\(\S+\)\.tar\.gz)"
			matchs = re.findall(formate_patchs,text)
			if matchs and matchs[0]:
				print "-\s(\w+_?\w+?\(\S+\)\.tar\.gz)",matchs
				assert len(matchs)>=1,"something wrong happened"
				matchs = self.grep_v_cmcc(matchs)
				_patchs = ','.join(matchs)
			if _eserviceid and _owner and _patchs:
				self.eserviceid.append(_eserviceid)
				self.owner.append(_owner)
				self.patchs.append(_patchs)
				self.releasetime.append(releasetime)
				self._href_list.append(self.href_list[i])
	def grep_v_cmcc(self,matchs):
		tmp = []
		for i in xrange(0,len(matchs)):
			#print i,matchs[i]
			if matchs[i].find("CMCC")==-1:
				tmp.append(matchs[i])
		print tmp
		return tmp
	def download(self,patch_list):
		download_buttons = self.driver.find_elements_by_xpath("//td/a[@data-original-title='Http']")
		print download_buttons
		#download_buttons = self.driver.find_elements_by_css_selector("html body.page-header-fixed.page-footer-fixed.page-sidebar-closed-hide-logo.page-container-bg-solid div.page-container div.page-content-wrapper div.page-content div.portlet.light div.portlet-body div.portlet-body div#FileTable_wrapper.dataTables_wrapper.form-inline.dt-bootstrap.no-footer div.row div.col-sm-12 table#FileTable.dt-responsive.dataTable.no-footer.dtr-inline.table.table-bordered.table-striped.table-hover tbody tr.odd td a.fa.fa-download.btn-action.download.http")
		if len(download_buttons)!=len(patch_list):
			print "wrong length of download button and patch list"
		for i in xrange(0,len(download_buttons)):
			if os.path.exists("/local/sdb/mtk_patch_import/TODO/"+patch_list[i]) and not os.path.exists("/local/sdb/mtk_patch_import/TODO/"+patch_list[i] + ".part"):
				continue
			download_buttons[i].click()
			time.sleep(5)
			agree_button = self.driver.find_element_by_xpath("//div[@class='modal-footer']/button[contains(text(),'Agree')]")
			#agree_button = self.driver.find_element_by_css_selector("html body.page-header-fixed.page-footer-fixed.page-sidebar-closed-hide-logo.page-container-bg-solid.modal-open div.page-container div.page-content-wrapper div.page-content div#legalModel.modal.in div.modal-dialog div.modal-content div.modal-footer button.btn.btn-primary.agree")
			time.sleep(3)
			agree_button.click()
			time.sleep(3)
			
	def download_all(self):
		_patch = []
		patch_tables_trs = self.driver.find_elements_by_xpath("//table[@id='FileTable']/tbody/tr")
		print "patch_tables_trs",patch_tables_trs
		for patch_tables_tr in patch_tables_trs:
			print "patch_tables_tr",patch_tables_tr
			patch_tables_tr.click()
			patch_tables_td = patch_tables_tr.find_element_by_xpath("child::td[2]")
			print "patch_tables_td",patch_tables_td
			print "patch_tables_td.text",patch_tables_td.text.encode('utf-8'),patch_tables_td.text.encode('utf-8').replace(" ","_").replace("@","%40").replace("#","%23").replace("[","%5b").replace("]","%5d").replace("–","%e2%80%93")
			if patch_tables_td.text:
				_patch.append(patch_tables_td.text.encode('utf-8').replace(" ","_").replace("@","%40").replace("#","%23").replace("[","%5b").replace("]","%5d").replace("–","%e2%80%93").replace("&","%26").replace("+","%2b"))
		self.is_patch_downloaded(_patch)
		current_driver = self.driver.current_window_handle
		if not self.patch_downloaded:
			self.download(_patch)
			for num in xrange(0,600): 
				if self.patch_downloaded:
					break
				self.is_patch_downloaded(_patch)
				time.sleep(6)
			time.sleep(3)
			self.close_other_windows(current_driver)

	def close_other_windows(self,current_driver):
		if current_driver:
			drivers = self.driver.window_handles
			for driver in drivers:
				print driver
				print driver.title
				if driver != current_driver:
					self.driver.switch_to.window(driver)
					#print "dir(other window)",dir(self.driver)
					time.sleep(1)
					self.driver.close()
			self.driver.switch_to.window(current_driver)					

	def is_patch_downloaded(self,_patchs):
		print "++++_patchs++++",_patchs
		if len(_patchs)==0:
			self.patch_downloaded = True
		for _patch in _patchs:
			print "====_patch====",_patchs
			if not _patch:
				continue
			if os.path.exists("/local/sdb/mtk_patch_import/TODO/"+_patch) and not os.path.exists("/local/sdb/mtk_patch_import/TODO/"+_patch + ".part"):
				self.patch_downloaded = True
			else:
				self.patch_downloaded = False
				break
	def echo_data(self):
		print self.eserviceid
		print self.owner
		print self.patchs
		print self.releasetime
#"In response to eService request ALPS03324166."
			#"EMAIL: kai.du.hz@tcl.com (Site:HZ)"
			#"The following files have been uploaded for you:"
#"- MOLY00257415_eServiceID(For_JHZ6737M_65_N_MOLY.LR9.W1444.MD.LWTG.MP.V110.5.P26).tar.gz"
#"- ALPS03324166(For_jhz6737m_65_n_alps-mp-n0.mp1-V1.0.2_P96).tar.gz"

#"Notes:"
	def getrandomnum(self,gap=10000):
		pass			
	def logout(self):		
		time.sleep(20)	
		self.driver.close()
def get_eserviceid_owner_patchs(text_list=[],eserviceid_list=[],owner_list=[],patchs_list=[]):
	if type(text_list) is str:
		text_list = [ text_list ]
	for text in text_list:
		#print "text====",text
		matchs = ''
		match = ''
		formate_eservice = r"In\sresponse\sto\seService\srequest\s(\w+)\."
		matchs = re.findall(formate_eservice,text)
		for match in matchs:
			print "In\sresponse\sto\seService\srequest\s(\w+)\.",match
			assert len(matchs)==1,"something wrong happened"
			eserviceid_list.append(match)
		matchs = ''
		match = ''
		formate_owner = r"EMAIL:\s(\w+\.?-?\w+?\.?\w+?@tcl\.com)"
		matchs = re.findall(formate_owner,text)
		if len(matchs)>=1:
			print "EMAIL:\s(\w+\.?-?\w+?\.?\w+?@tcl\.com)",matchs
			owner_list.append(matchs[-1])
		matchs = ''
		match = ''
		formate_patchs = r"-\s(\w+_?\w+?\(\S+\)\.tar\.gz)"
		matchs = re.findall(formate_patchs,text)
		if len(matchs)>=1:
			print "-\s(\w+_?\w+?\(\S+\)\.tar\.gz)",matchs
			patchs_list.append(','.join(matchs))
def main_mtk():
	mtk = login_mtk()
	mtk.login()
	mtk.load_history_received()
	mtk.grep_table()
	mtk.convert_href_to_get_email_text()
	mtk.get_owner_eserviceid()
	#mtk.download_all()
	mtk.echo_data()
	mtk.logout()
	return mtk.eserviceid,mtk.owner,mtk.patchs,mtk.releasetime
class imap_email:
	def __init__(self,host="mail.tcl.com"):
		self.conn = imaplib.IMAP4_SSL(host)
		self.datas = []
		self.eserviceid = []
		self.owner = []
		self.patchs = []
	def login(self,username="tct-hq/xiaodan.cheng",password="cxd@6235"):
		self.conn.login(username,password)
	def logout(self):
		self.conn.logout()
	def get_mail(self):
		result,message = self.conn.select()
		#print result,message
		typeq,self.datas = self.conn.search(None,"ALL")
		#print typeq,self.datas
	def fetch_mail(self):
		#import sys
		#reload(sys)
		#sys.setdefaultencoding('utf-8')
		for data in self.datas:
			msglist = data.split()
			for n in xrange(0,len(msglist)):
				typeq,tmp_datas = self.conn.fetch(msglist[n],'(RFC822)')
				#print typeq,tmp_datas
				msg = email.message_from_string(tmp_datas[0][1])
				#print 'msg.is_multipart()====',msg.is_multipart()
				#print msg.items()
				#print 'msg.get_params()====',msg.get_params()
				#[('multipart/related', ''), ('boundary', '_005_E19BF6D8FF2B2248A8A5E3793B23BEBAFF06C2CNSZEXMB02_'), ('type', 'text/html')]
				#print 'msg.get_content_type()====',msg.get_content_type()
				#multipart/mixed multipart/related
				#print msg.items()
				#[('Received', 'from CNSZEXMB02.TCT.TCL.com ([10.128.161.154]) by\r\n CNSZEXCH02.TCT.TCL.com ([10.128.161.151]) with mapi id 14.03.0123.003; Tue,\r\n 27 Jun 2017 08:33:28 +0800'), ('From', '"Yan, GONG(WMD PIC HZ SMO-HZ-TCT)" <yan.gong@tcl.com>'), ('To', 'SW-PL2-HZ <sw.pl2.hz@tcl.com>'), ('Subject', 'SW XR Status 20170627'), ('Thread-Topic', 'SW XR Status 20170627'), ('Thread-Index', 'AdLu3TP5bGdMR4yORcqqJY/L8bkb9g=='), ('Date', 'Tue, 27 Jun 2017 08:33:27 +0800'), ('Message-ID', '<E19BF6D8FF2B2248A8A5E3793B23BEBAFF06C2@CNSZEXMB02>'), ('Accept-Language', 'zh-CN, en-US'), ('Content-Language', 'zh-CN'), ('X-MS-Exchange-Organization-AuthAs', 'Internal'), ('X-MS-Exchange-Organization-AuthMechanism', '04'), ('X-MS-Exchange-Organization-AuthSource', 'CNSZEXCH02.TCT.TCL.com'), ('X-MS-Has-Attach', 'yes'), ('X-Auto-Response-Suppress', 'DR, OOF, AutoReply'), ('X-MS-Exchange-Organization-SCL', '-1'), ('X-MS-TNEF-Correlator', ''), ('Content-Type', 'multipart/related;\r\n\tboundary="_005_E19BF6D8FF2B2248A8A5E3793B23BEBAFF06C2CNSZEXMB02_";\r\n\ttype="text/html"'), ('MIME-Version', '1.0')]
				#print msg['from'],msg['to'],msg['subject'],msg['CC'],msg['Date']
				
				if not msg.is_multipart():
					payload = msg.get_payload(decode=True)
					name = msg.get_param("name")
					if name:
						print 'name====',name
					print payload
					get_eserviceid_owner_patchs(payload,self.eserviceid,self.owner,self.patchs)
				if msg.get(u'subject'):
					h = email.Header.Header(unicode(msg.get(u'subject'),'utf-8'))
					if h:
						dh = email.Header.decode_header(h)
						if dh[0][1]:
							subject = unicode(dh[0][0],dh[0][1]).encode('utf-8')
						print subject
		print self.eserviceid,self.owner,self.patchs
def main_email():
	__g_codeset = sys.getdefaultencoding()
	if "ascii"== __g_codeset:
		__g_codeset = locale.getdefaultlocale()[1]
	mail = imap_email()
	mail.login()
	mail.get_mail()
	mail.fetch_mail()
	time.sleep(10)
	mail.logout()
class jenkins:
	def __init__(self,url='http://10.92.35.20:8080/jenkins/view/tools/job/mtk-patch-import'):
		self.driver = webdriver.Firefox()
		time.sleep(3)
	def login(self,url='http://10.92.35.20:8080/jenkins/login?from=%2Fjenkins%2Fview%2Ftools%2Fjob%2Fmtk-patch-import%2F',username='xiaoli.luo',password='123'):
		try:
			self.driver.get(url)
		except NoSuchWindowException,e:
			print "--------------"
			print e
			print "--------------"
			main_network_security()
			self.driver = webdriver.Firefox()
			time.sleep(3)
			self.driver.get(url)
			
		time.sleep(3)
		user = self.driver.find_element_by_name("j_username")
		user.click()
		user.send_keys(username)
		passwd = self.driver.find_element_by_name("j_password")
		passwd.click()
		passwd.send_keys(password)
		bt_login = self.driver.find_element_by_name("Submit")
		bt_login.click()
		time.sleep(3)
	def release(self,prj,owner,eserviceid='',alps='',moly='',sixth='',has_drivonly=False,build=False,server='10.92.35.22--andoridL-108',url='http://10.92.35.20:8080/jenkins/view/tools/job/mtk-patch-import/release'):
		self.driver.get(url)
		
		patch_owner_email = self.driver.find_element_by_xpath("//input[@value='patch_owner_email']/parent::div/child::input[@type='text']")
		patch_owner_email.click()
		patch_owner_email.clear()
		patch_owner_email.send_keys(owner)
		alps_number = self.driver.find_element_by_xpath("//input[@value='alps_number']/parent::div/child::input[@type='text']")
		alps_number.click()
		alps_number.clear()
		alps_number.send_keys(alps)
		moly_number = self.driver.find_element_by_xpath("//input[@value='moly_number']/parent::div/child::input[@type='text']")
		moly_number.click()
		moly_number.clear()
		moly_number.send_keys(moly)
		sixth_number = self.driver.find_element_by_xpath("//input[@value='sixth_number']/parent::div/child::input[@type='text']")
		sixth_number.click()
		sixth_number.clear()
		sixth_number.send_keys(sixth)
		eservice_ID = self.driver.find_element_by_xpath("//input[@value='eservice_ID']/parent::div/child::input[@type='text']")
		eservice_ID.click()
		eservice_ID.clear()
		eservice_ID.send_keys(eserviceid)
		
		driveonly_import = self.driver.find_element_by_xpath("//input[@value='driveonly_import']/parent::div/child::input[@type='checkbox']")
		if  has_drivonly:
			if not driveonly_import.is_selected():
				driveonly_import.click()
			if build:
				driveonly_build = self.driver.find_element_by_xpath("//input[@value='driveonly_build']/parent::div/child::input[@type='checkbox']")
				if not driveonly_build.is_selected():
					driveonly_build.click()
		else: 
			if driveonly_import.is_selected():
				driveonly_import.click()
			if build:
				normalbranch_build = self.driver.find_element_by_xpath("//input[@value='normalbranch_build']/parent::div/child::input[@type='checkbox']")
				if not normalbranch_build.is_selected():
					normalbranch_build.click()
		project =  self.driver.find_element_by_xpath("//input[@value='project']/parent::div/child::select/option[@value='%s']"%prj)
		project.click()
		select = ''
		_selects = self.driver.find_elements_by_xpath("//input[@value='build_server']/parent::div/select/option")
		#print _selects
		for _select in _selects:
			_select.click()
			#time.sleep(3)
			str_select = _select.get_attribute("value").encode().split('-')[0]
			print str_select,type(str_select),server
			if str_select.find(server.split('-')[0])!=-1:
				print "select::",str_select
				select = _select
		if select:
			select.click()
		Schedule_Release_Build = self.driver.find_element_by_xpath("//button[contains(text(),'Schedule Release Build')]")
		#print Schedule_Release_Build,Schedule_Release_Build.get_attribute('id')
		Schedule_Release_Build.click()
		time.sleep(20)	
	def logout(self):
		self.driver.close()
def main_jenkins(project,owner,eserviceid,alps,moly,sixth,has_drivonly,build,server):
	jk = jenkins()
	jk.login()
	jk.release(project,owner,eserviceid,alps,moly,sixth,has_drivonly,build,server)
	time.sleep(10)
	jk.logout()
class read_prj_xls:
	def __init__(self,wb_file='/local/int_jenkins/mtk_patch/jb3-mp-import.xls'):
		self.project_message = {}
		wb = xlrd.open_workbook(wb_file)
		ap_st = wb.sheet_by_name(u'MTKInfo')
		mp_st = wb.sheet_by_name(u'ModemInfo')
		for row in xrange(0,ap_st.nrows):
			prj = ap_st.cell(row,0).value.strip()
			mtk_prj_alps = ap_st.cell(row,2).value.strip()
			mtk_release_alps = ap_st.cell(row,3).value.strip()
			current_alps_number = str(ap_st.cell(row,23).value)[:-2]
			has_driveonly = True if ap_st.cell(row,11).value.strip() else False
			import_branch = ap_st.cell(row,1).value.strip()
			download_type = ap_st.cell(row,27).value.strip()
			mtk_message = ap_st.cell(row,30).value
			platform = ap_st.cell(row,15).value.strip()
			if download_type == 'git':
				import_branch = 'JRD_' + import_branch
			self.project_message[prj] = {}
			self.project_message[prj]['mtk_prj_alps'] = mtk_prj_alps 
			self.project_message[prj]['mtk_release_alps'] = mtk_release_alps
			self.project_message[prj]['current_alps_number'] = current_alps_number
			self.project_message[prj]['has_driveonly'] = has_driveonly
			self.project_message[prj]['import_branch'] = import_branch
			self.project_message[prj]['download_type'] = download_type
			self.project_message[prj]['mtk_message'] = mtk_message
			self.project_message[prj]['platform'] = platform
		for row in xrange(0,mp_st.nrows):
			prj = mp_st.cell(row,0).value.strip()
			mtk_prj_moly = mp_st.cell(row,2).value.strip()
			mtk_release_moly = mp_st.cell(row,3).value.strip()
			mtk_prj_sixth = mp_st.cell(row,2).value.strip()
			mtk_release_sixth = mp_st.cell(row,4).value.strip()
			platform = ap_st.cell(row,16).value.strip()
			current_moly_number = str(mp_st.cell(row,20).value)[:-2]
			current_sixth_number = str(mp_st.cell(row,21).value)[:-2]
			self.project_message[prj]['mtk_prj_moly'] = mtk_prj_moly
			self.project_message[prj]['mtk_release_moly'] = mtk_release_moly
			self.project_message[prj]['mtk_prj_sixth'] = mtk_prj_sixth
			self.project_message[prj]['mtk_release_sixth'] = mtk_release_sixth
			self.project_message[prj]['current_moly_number'] = current_moly_number
			self.project_message[prj]['current_sixth_number'] = current_sixth_number
			self.project_message[prj]['platform'] = platform
def main_read_xls():
	xls = read_prj_xls()
	print xls.project_message
	#sys.exit(1)
	return xls.project_message
class patchs_reconise:
	def __init__(self,patchs,project_message=''):
		self.patch_list = []
		#print type(patchs),patchs
		if type(patchs) is unicode:
			self.patch_list = patchs.encode().split(',')
		elif type(patchs) is str:
			self.patch_list = patchs.split(',')
		else:
			print "type(patch) error!!!"
			sys.exit(1)
		self._project = ''
		self._patchnum_alps = ''
		self._patchnum_moly = ''
		self._patchnum_sixth = ''
		self.project_message = project_message if project_message else {}
		if not project_message:
			self.read_xls()
	def read_xls(self):
		wb = xlrd.open_workbook('/local/int_jenkins/mtk_patch/jb3-mp-import.xls')
		ap_st = wb.sheet_by_name(u'MTKInfo')
		mp_st = wb.sheet_by_name(u'ModemInfo')
		for row in xrange(0,ap_st.nrows):
			prj = ap_st.cell(row,0).value.strip()
			mtk_prj_alps = ap_st.cell(row,2).value.strip()
			mtk_release_alps = ap_st.cell(row,3).value.strip()
			current_alps_number = str(ap_st.cell(row,23).value)[:-2]
			has_driveonly = True if ap_st.cell(row,11).value.strip() else False
			import_branch = ap_st.cell(row,1).value.strip()
			download_type = ap_st.cell(row,27).value.strip()
			if download_type == 'git':
				import_branch = 'JRD_' + import_branch
			self.project_message[prj] = {}
			self.project_message[prj]['mtk_prj_alps'] = mtk_prj_alps 
			self.project_message[prj]['mtk_release_alps'] = mtk_release_alps
			self.project_message[prj]['current_alps_number'] = current_alps_number
			self.project_message[prj]['has_driveonly'] = has_driveonly
			self.project_message[prj]['import_branch'] = import_branch
		for row in xrange(0,mp_st.nrows):
			prj = mp_st.cell(row,0).value.strip()
			mtk_prj_moly = mp_st.cell(row,2).value.strip()
			mtk_release_moly = mp_st.cell(row,3).value.strip()
			mtk_prj_sixth = mp_st.cell(row,2).value.strip()
			mtk_release_sixth = mp_st.cell(row,4).value.strip()
			current_moly_number = str(mp_st.cell(row,20).value)[:-2]
			current_sixth_number = str(mp_st.cell(row,21).value)[:-2]
			self.project_message[prj]['mtk_prj_moly'] = mtk_prj_moly
			self.project_message[prj]['mtk_release_moly'] = mtk_release_moly
			self.project_message[prj]['mtk_prj_sixth'] = mtk_prj_sixth
			self.project_message[prj]['mtk_release_sixth'] = mtk_release_sixth
			self.project_message[prj]['current_moly_number'] = current_moly_number
			self.project_message[prj]['current_sixth_number'] = current_sixth_number
		
	def echo(self):
		print self.project_message
	def get_number(self,patch):
		match = re.findall(r'[._]P([0-9]+)\)\.tar\.gz',patch)
		if match:
			print match
			assert len(match)==1,"wrong length of patch number"
			return match[-1]
		else:
			match = re.findall(r'\.?([0-9]+)\.xml',patch)
			print 'match,patch',match,patch
			if match:
				print match
				assert len(match)==1,"wrong length of patch number"
				return match[-1]
			else:
				print "something wrong was found on patch number"
				return ''
	def get_project_number(self):
		patch_prj_name = ''
		patch_release_name = ''
		project = ''
		number = ['','','']
		driveonly = False
		#print 'self.patch_list',self.patch_list
		for patch in self.patch_list:
			pt = ''
			if patch.find('SIXTH')!=-1:
				pt = 'SIXTH'
				patch_prj_name = 'mtk_prj_sixth'
				patch_release_name = 'mtk_release_sixth'
			elif patch.find('MOLY')!=-1 and patch.find('CMCC')==-1:
				pt = 'MOLY'
				patch_prj_name = 'mtk_prj_moly'
				patch_release_name = 'mtk_release_moly'
			elif patch.find('ALPS')!=-1 or patch.find('alps')!=-1:
				pt = 'ALPS'
				patch_prj_name = 'mtk_prj_alps'
				patch_release_name = 'mtk_release_alps'
			else:
				print "can not find key words SIXTH OR MOLY OR ALPS"
				continue
			assert patch_prj_name and patch_release_name,"NULL were found on patch_prj_name or patch_release_name"
			for prj in self.project_message.keys():
				_prj_name = self.project_message[prj][patch_prj_name] if self.project_message[prj].has_key(patch_prj_name) else ''
				_release_name = self.project_message[prj][patch_release_name] if self.project_message[prj].has_key(patch_release_name) else ''
				mtk_message = self.project_message[prj]['mtk_message']
				if _prj_name and _release_name and patch.find(_prj_name)!=-1 and patch.find(_release_name)!=-1 and not mtk_message:
					project = prj
					driveonly = self.project_message[prj]['has_driveonly']
					_number = self.get_number(patch)
					if pt=='SIXTH':
						number[2] = _number
					elif pt=='MOLY':
						number[1] = _number
					elif pt=='ALPS':
						number[0] = _number
					else:
						pass
		print "project,number",project,number,driveonly
		return project,number,driveonly
	def reconise_number(self,project='',number=''):
		patch_type=['current_alps_number','current_moly_number','current_sixth_number']
		assert len(number)==len(patch_type),"wrong length of patch number"
		if project and number:
			for n in xrange(0,len(number)):
				if number[n]:
					print patch_type[n],self.project_message[project][patch_type[n]]
					if int(number[n])<=int(self.project_message[project][patch_type[n]]) :
						number = ''
						break
		return project,number
	def is_downloaded(self):
		_downloaded = False
		for patch in self.patch_list:
			print "patch====/local/mtk_patch_import/TODO/%s" % patch
			if os.path.exists("/local/mtk_patch_import/TODO/"+patch):
				_downloaded = True
			if patch.find('.xml')!=-1:
				_downloaded = True
		return _downloaded
	def get_opt_server(self,prj):
		
		opt_servers = []
		if prj:
			import_branch = self.project_message[prj]['import_branch']
			if os.path.exists("/local/mtk_patch_import/%s"%import_branch):
				opt_servers.append("10.92.35.22--androdL-108")
			status = commands.getoutput('if ssh int@10.92.35.24 test -e "/local/mtk_patch_import/%s"; then echo True; else echo False; fi'%import_branch)
			print "status=",status,'if ssh int@10.92.35.24 test -e "/local/mtk_patch_import/%s"; then echo True; else echo False; fi'%import_branch
			if status == "True":
				opt_servers.append("10.92.35.24--MTKpatch")
		return ','.join(opt_servers)

def main_paths_reconise(patchs,project_message):
	patchs = patchs_reconise(patchs,project_message)
	patchs.echo()
	_downloaded = patchs.is_downloaded()
	print "is_downloaded====",_downloaded
	project,number,driveonly = patchs.get_project_number()
	#print project,number
	project,number = patchs.reconise_number(project,number)
	#print project,number
	opt_servers = patchs.get_opt_server(project)
	return project,number,driveonly,_downloaded,opt_servers			
def utf8_to_mbs(s,__g_codeset):
	return s.decode("utf-8").encode(__g_codeset)
def mbs_to_utf8(s,__g_codeset):
	return s.decode(__g_codeset).encode("utf-8")
def pop_item(i,eserviceid=[],owner=[],patchs=[],releasetime=[],project=[],number=[],build=[]):
	assert len(eserviceid)==len(owner)==len(patchs)==len(releasetime),"wrong of list length"
	assert i<len(eserviceid),"pop index out of range"
	eserviceid.pop(i)
	owner.pop(i)
	patchs.pop(i)
	releasetime.pop(i)
	project.pop(i)
	number.pop(i)
	build.pop(i)
def get_build(project,number,build):
	tmp_prj = []
	tmp_num = []
	tmp_i = ''
	for i in xrange(0,len(project)):
		build.append(False)
	for i in xrange(0,len(project)):
		if not project[i] or not number[i]:
			continue
		elif number[i] and not number[i][0]:
			build[i] = False
			continue
		else:
			build[i] = True
			tmp_prj = project[i]
			tmp_num = number[i][0]
			tmp_i = i
		tmp = tmp_i+1
		for j in xrange(tmp,len(project)):
			if tmp_prj and tmp_prj == project[j]:
				if  str(tmp_num) < str(number[j][0]):
					build[tmp_i] = False
					build[j] = True
					tmp_num = number[j][0]
					tmp_i = j
	return build	
def switch_server(server='',opt_servers=[]):
	
	if len(opt_servers)== 1 and opt_servers[0]:
		server = opt_servers[0]
	if len(opt_servers)!= 1 :
		if server == '10.92.35.22--androdL-108':
			server = '10.92.35.24--MTKpatch'
		elif server == '10.92.35.24--MTKpatch':
			server = '10.92.35.22--androdL-108'
		else:
			server = '10.92.35.22--androdL-108'
	return server
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
class Network_security:

	def __init__(self,url="https://10.92.63.254/auth.html"):
		self.url = url
		self.driver = WebDriver()
		time.sleep(3)
		self.driver.get(self.url)
		time.sleep(1)	
	def login(self):
		self.driver.switch_to.frame(self.driver.find_element_by_xpath("/html/frameset/frame[@id='authFrm']"))
		username = self.driver.find_element_by_css_selector("html body form div#login_box div#username_line div.fieldValue input#userName")
		username.click()
		username.clear()
		username.send_keys("xiaodan.cheng")
		passwd = self.driver.find_element_by_css_selector("#password_line > div:nth-child(2) > input:nth-child(1)")
		passwd.click()
		passwd.clear()
		passwd.send_keys("cxd@6235")
		submit = self.driver.find_element_by_css_selector(".button")
		time.sleep(3)
		submit.click()
		self.driver.switch_to.default_content()
	def logout(self):
		time.sleep(3)
		print self.driver.window_handles
		drivers = self.driver.window_handles
		for driver in drivers:
			self.driver.switch_to.window(driver)
			print self.driver
			print self.driver.title
			self.driver.close()

def main_network_security():
	ns = Network_security()
	ns.login()
	ns.logout()
class git_update:
	def __init__(self,project_message={}):
		self.project_message = project_message
		self.git_update_prj = []
		self.import_branch = []
		self.patchs = []
	def get_newest_patch(self,codedir,project):
		pwd = os.getcwd()
		if os.path.exists(codedir+'/.repo/manifests'):
			print "change dir====",codedir
			os.chdir(codedir)
			os.system("git pull")
			_patchs = commands.getoutput("ls ./release_version/%s -t1 | grep %s" %(self.project_message[project]['platform'], self.project_message[project]['mtk_release_alps'])).split('\n')[0]
			print _patchs
			if _patchs:
				self.patchs.append( _patchs )
		else:
			status = commands.getoutput('if ssh int@10.92.35.24 test -e "%s/.repo/manifests"; then echo True; else echo False; fi'%codedir)
			if status:
				print "ssh int@10.92.35.24 'cd %s/.repo/manifests/ ;git pull'" % codedir
				os.system("ssh int@10.92.35.24 'cd %s/.repo/manifests/ ;git pull'" % codedir)
				print "ssh int@10.92.35.24 'cd %s/.repo/manifests/ ;ls ./release_version/%s -t1 | grep %s'" % (codedir,self.project_message[project]['platform'],self.project_message[project]['mtk_release_alps'])
				_patchs = commands.getoutput("ssh int@10.92.35.24 'cd %s/.repo/manifests/ ;ls ./release_version/%s -t1 | grep %s'" % (codedir,self.project_message[project]['platform'],self.project_message[project]['mtk_release_alps'])).split('\n')[0]
				time.sleep(3)
				print '_patchs',_patchs
				if _patchs:
					self.patchs.append( _patchs )
		print "change dir====",pwd
		os.chdir(pwd)
	def get_git_prj(self):
		for prj in self.project_message.keys():
			if self.project_message[prj]['download_type']=='git' and not self.project_message[prj]['mtk_message'] :
				self.git_update_prj.append(prj)
				print "project_message[prj]['import_branch']",project_message[prj]['import_branch']
				self.import_branch.append(project_message[prj]['import_branch'])
		print 'self.git_update_prj',self.git_update_prj
		print 'self.import_branch',self.import_branch
	def get_patchs(self):
		assert len(self.git_update_prj)==len(self.import_branch),"wrong length of git_update_prj and import_branch"
		for i in xrange(0,len(self.git_update_prj)):
			codedir = '/local/mtk_patch_import/'+self.import_branch[i]
			self.get_newest_patch(codedir,self.git_update_prj[i])
		print 'self.git_update_prj',self.git_update_prj
		print 'self.import_branch',self.import_branch
		print 'self.patchs',self.patchs
		assert len(self.git_update_prj)==len(self.import_branch)==len(self.patchs),"wrong length of git_update_prj and import_branch"
		
def main_git_update(project_message,eserviceid=[],owner=[],patchs=[],releasetime=[]):
	gp = git_update(project_message)
	gp.get_git_prj()
	gp.get_patchs()
	for _patch in gp.patchs:
		eserviceid.append('')
		owner.append('xiaodan.cheng@tcl.com')
		patchs.append(_patch)
		releasetime.append('')
	return eserviceid,owner,patchs,releasetime
		
if __name__ == '__main__' :
	print 'start'
	print time.ctime(time.time())
	project = []
	number = []
	driveonly = []
	build = []
	job_list = []
	job_number_list = []
	downloaded = []
	opt_servers = []
	server = ''
	patch_type=['current_alps_number','current_moly_number','current_sixth_number']
	project_message = main_read_xls()
	main_network_security()
	eserviceid,owner,patchs,releasetime = main_mtk()
	#eserviceid,owner,patchs,releasetime = main_git_update(project_message,eserviceid,owner,patchs,releasetime)
	for i in xrange(0,len(patchs)):
		_project,_number,_driveonly,_downloaded,_opt_servers = main_paths_reconise(patchs[i],project_message)
		if _project and _number and (_number[0] or _number[1] or _number[2]):
			project.append(_project)
			number.append(_number)
			driveonly.append(_driveonly)
			
		else:
			project.append('')
			number.append('')
			driveonly.append('')
		downloaded.append(_downloaded)
		opt_servers.append(_opt_servers)
	build = get_build(project,number,build)
	server = switch_server(server)
	print project
	print number
	print driveonly
	print build
	print downloaded
	print opt_servers
	assert len(eserviceid)==len(owner)==len(patchs)==len(releasetime)==len(project)==len(number)==len(driveonly)==len(build)==len(downloaded)==len(opt_servers),"wrong of list length"
	main_network_security()
	for i in xrange(0,len(number)):
		if number[i] and project[i] not in job_list and downloaded[i] and ((number[i][0] and (int(number[i][0])==int(project_message[project[i]][patch_type[0]]) + 1)) or (number[i][1] and int(number[i][1])==int(project_message[project[i]][patch_type[1]]) + 1) or (number[i][2] and int(number[i][2])==int(project_message[project[i]][patch_type[2]]) + 1)) :
			server = switch_server(server,opt_servers[i].split(','))
			print 'server===',server
			main_jenkins(project[i],owner[i],eserviceid[i],number[i][0],number[i][1],number[i][2],driveonly[i],build[i],server)
			job_list.append(project[i])
			job_number_list.append(number[i])
			
	print job_list,job_number_list
	#if len(job_list)!=0:
		#main_modify_xls(job_list,job_number_list)
		#git_push()

	print time.ctime(time.time())
	print 'end'
