#!/usr/bin/python
####################################
#build for sign apks
####################################

from Utils import *
import os
import sys

class sign_apk():
	tmpdir = ''
	def __init__(self,secchar,Project):
		print 'start ...'
		self.tmpdir = os.getcwd()
                self.secchar = secchar
                self.Project = Project
		print 'tmpdir=',self.tmpdir
	def replace(self):
		docmd('cp /local/int_jenkins/securityteam/%s/misc_sign_custpack_apks.py .'%(self.Project))
                docmd('mv build/target/product/security build/target/product/googlesecurity')
                docmd('mkdir -p build/target/product/security')
                os.chdir('build/target/product')
                #docmd('zip -r security_bc.zip security')
                os.chdir(self.tmpdir)
		#docmd('rm -rf build/target/product/security/*')
		docmd('cp /local/int_jenkins/securityteam/pixi3-55_3g-panasonic/TCL_ReleaseKeys.zip build/target/product/security/')
		os.chdir('build/target/product/security')
		docmd('unzip TCL_ReleaseKeys.zip')
	
	def build(self):
                os.chdir(self.tmpdir)
                #docmd('rm out/target/product/%s/system/plugin/Signatures/mplugin_guard.xml' %(self.Project))
                #docmd('cp /local/int_jenkins/securityteam/%s/mplugin_guard.xml out/target/product/%s/system/plugin/Signatures/mplugin_guard.xml' %(self.Project)  %(self.Project))
                #add by zhaoshie 2015-7-16
   		docmd('cp out/target/product/pixi3_55_panasonic/custpack.img out/target/product/pixi3_55_panasonic/custpack.img_unsign')
		docmd('cp out/target/product/pixi3_55_panasonic/system.img out/target/product/pixi3_55_panasonic/system.img_unsign')
		docmd('cp out/target/product/pixi3_55_panasonic/recovery.img out/target/product/pixi3_55_panasonic/recovery.img_unsign')
		docmd('cp out/target/product/pixi3_55_panasonic/boot.img out/target/product/pixi3_55_panasonic/boot.img_unsign')
		docmd('cp out/target/product/pixi3_55_panasonic/cache.img out/target/product/pixi3_55_panasonic/cache.img_unsign')
		docmd('cp out/target/product/pixi3_55_panasonic/userdata.img out/target/product/pixi3_55_panasonic/userdata.img_unsign')
                #end
                docmd('rm out/target/product/pixi3_55_panasonic/system/plugin/Signatures/mplugin_guard.xml')
                docmd('cp /local/int_jenkins/securityteam/pixi3-55_3g-panasonic/mplugin_guard.xml out/target/product/pixi3_55_panasonic/system/plugin/Signatures/mplugin_guard.xml')
		#docmd('source build/envsetup.sh && lunch full_pixi3_55_panasonic-user && make dist')
		docmd('make dist -j24')
		
	def signapk(self):
		pl = []
                pl.append('Enter\spassword\sfor\sbuild\/target\/product\/security\/media\skey>')
                pl.append('Enter\spassword\sfor\sbuild\/target\/product\/security\/platform\skey>')
                pl.append('Enter\spassword\sfor\sbuild\/target\/product\/security\/releasekey\skey>')
                pl.append('Enter\spassword\sfor\sbuild\/target\/product\/security\/shared\skey>')
                pl.append('done\.')

		os.chdir(self.tmpdir)
		print 'start sign the apks ..................'
		child = pexpect.spawn('./misc_sign_custpack_apks.py out/dist/full_pixi3_55_panasonic-target_*.zip out/dist/sign_target_apks.zip')
		child.logfile = sys.stdout
                cpl = child.compile_pattern_list(pl)
                flag = True
                while flag:
                        try:
                                index = child.expect_list(cpl,child.timeout)
                                if index == 0:
                                        child.sendline(self.secchar)
                                if index == 1:
                                        child.sendline(self.secchar)
                                if index == 2:
                                        child.sendline(self.secchar)
                                if index == 3:
                                        child.sendline(self.secchar)
                                if index == 4:
                                        continue
                        except pexpect.EOF:
                        	flag = False
                        except pexpect.TIMEOUT:
                                continue

		print 'start gen the imgs ...................'
		docmd('build/tools/releasetools/img_from_target_files out/dist/sign_target_apks.zip out/dist/signed-img.zip')
		os.chdir('out/dist')
		if os.path.exists('sign_img'):
			docmd('rm -rf sign_img')
		docmd('mkdir sign_img')
		os.chdir('sign_img')
		print('start unzip the imgs')
		docmd('unzip ../signed-img.zip')
		os.chdir(self.tmpdir)
		#docmd('mv out/target/product/pixi3_55_panasonic/custpack.img out/target/product/pixi3_55_panasonic/custpack.img_unsign')
		#docmd('mv out/target/product/pixi3_55_panasonic/system.img out/target/product/pixi3_55_panasonic/system.img_unsign')
		#docmd('mv out/target/product/pixi3_55_panasonic/recovery.img out/target/product/pixi3_55_panasonic/recovery.img_unsign')
		#docmd('mv out/target/product/pixi3_55_panasonic/boot.img out/target/product/pixi3_55_panasonic/boot.img_unsign')
		docmd('cp out/dist/sign_img/custpack.img out/target/product/pixi3_55_panasonic/')
		docmd('cp out/dist/sign_img/system.img out/target/product/pixi3_55_panasonic/')
		docmd('cp out/dist/sign_img/recovery.img out/target/product/pixi3_55_panasonic/')
		docmd('cp out/dist/sign_img/boot.img out/target/product/pixi3_55_panasonic/')
		#docmd('perl mediatek/build/tools/jrd_magic.pl pixi3_55_panasonic')
		docmd('perl vendor/jrdcom/build/jrdmagic/jrd_magic.pl pixi3_55_panasonic')
        
	def CheckSign(self):
		docmd("rm -rf /tmp/checksign && mkdir /tmp/checksign")
		docmd('unzip otacerts.zip -d /tmp/checksign')
	        f_key = open('/tmp/checksign/keys')
	        for line in f_key.readlines():
	                if line.find('1401033162') != -1:
	                        print "recovery.img is not signed with release key"
	                        sys.exit(1)
	                else:
	                        print "recovery.img has been signed with release key"
	        f_key.close()
	        docmd("unzip /tmp/checksign/otacerts.zip -d /tmp/checksign")
	        if os.path.isfile("/tmp/checksign/build/target/product/security/releasekey.x509.pem"):
	                print "system.img has been signed with release key"
	        else:
	                print "system.img is not signed with release key"
	                sys.exit(1)
	        docmd("rm -rf /tmp/checksign")

if __name__ == "__main__":
	#if len(sys.argv) != 2:
	#	print "You must give a argument!"
	#	sys.exit(1)
	dist = sign_apk(sys.argv[1],'pixi3-55_3g-panasonic')
	#dist = sign_apk('')
	dist.build()
	dist.replace()
	dist.signapk()
	#dist.CheckSign()
	os.chdir('build/target/product')
	docmd('rm -rf security')
	docmd('mv googlesecurity security')
	#docmd('mv build/target/product/googlesecurity build/target/product/security')
	#docmd('unzip -o security_bc.zip')
	#docmd('rm security_bc.zip')
