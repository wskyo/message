#!/usr/bin/python
####################################
#build for sign apks
####################################

from Utils import *
import os
import sys
import commands

class sign_apk():
	tmpdir = ''
	def __init__(self,secchar,Project,mtkProject):
		print 'start ...'
		self.tmpdir = os.getcwd()
                self.secchar = secchar
                self.Project = Project
                self.mtkProject = mtkProject
		print 'tmpdir=',self.tmpdir
	def replace(self):
		docmd('cp /local/int_jenkins/securityteam/%s/misc_sign_custpack_apks.py .'%(self.Project))
                docmd('mv build/target/product/security build/target/product/googlesecurity')
                docmd('mkdir -p build/target/product/security')
                os.chdir('build/target/product')
                #docmd('zip -r security_bc.zip security')
                os.chdir(self.tmpdir)
		#docmd('rm -rf build/target/product/security/*')
		docmd('cp /local/int_jenkins/securityteam/pixi4-4_3g/TCL_ReleaseKeys.zip build/target/product/security/')
		os.chdir('build/target/product/security')
		docmd('unzip TCL_ReleaseKeys.zip')
	
	def build(self):
                os.chdir(self.tmpdir)
                #docmd('rm out/target/product/%s/system/plugin/Signatures/mplugin_guard.xml' %(self.mtkProject))
                #docmd('cp /local/int_jenkins/securityteam/%s/mplugin_guard.xml out/target/product/%s/system/plugin/Signatures/mplugin_guard.xml' %(self.Project)  %(self.mtkProject))
                #add by zhaoshie 2015-7-16
   		#docmd('cp out/target/product/%s/custpack.img out/target/product/%s/custpack.img_unsign' %(self.mtkProject,self.mtkProject))
		docmd('cp out/target/product/%s/system.img out/target/product/%s/system.img_unsign' %(self.mtkProject,self.mtkProject))
		docmd('cp out/target/product/%s/recovery.img out/target/product/%s/recovery.img_unsign' %(self.mtkProject,self.mtkProject))
		docmd('cp out/target/product/%s/boot.img out/target/product/%s/boot.img_unsign' %(self.mtkProject,self.mtkProject))
		docmd('cp out/target/product/%s/cache.img out/target/product/%s/cache.img_unsign' %(self.mtkProject,self.mtkProject))       
		docmd('cp out/target/product/%s/userdata.img out/target/product/%s/userdata.img_unsign' %(self.mtkProject,self.mtkProject))
                #end
                docmd('rm out/target/product/%s/system/plugin/Signatures/mplugin_guard.xml' %(self.mtkProject))
                docmd('cp /local/int_jenkins/securityteam/pixi4-4_3g/mplugin_guard.xml out/target/product/%s/system/plugin/Signatures/mplugin_guard.xml' %(self.mtkProject))
		#docmd('source build/envsetup.sh && lunch full_%s-user && make dist')
		#docmd('make dist -j24')
		cpunum = self.countcpu()
		#docmd('make dist -j24')
		docmd('make dist -j%d' %cpunum)
		#if os.path.isfile("out/dist/full_%s-target_*.zip"):
			#print "make dist success!!!!"
		#else:
			#print "make dist Fail!!!!"
	                #sys.exit(1)

	def countcpu(self):
		resHeadList = commands.getstatusoutput("cat /proc/cpuinfo |grep 'physical id' |wc -l")
		if resHeadList[0] >> 8 != 0:
			print 'Error getting cpu number,so return defaut cpu number 16'
			return 16
		if (int(resHeadList[1]) >= 8):
			return int(resHeadList[1])
		else:
			return 8
			
	def signapk(self):
		pl = []
                pl.append('Enter\spassword\sfor\sbuild\/target\/product\/security\/media\skey>')
                pl.append('Enter\spassword\sfor\sbuild\/target\/product\/security\/platform\skey>')
                pl.append('Enter\spassword\sfor\sbuild\/target\/product\/security\/releasekey\skey>')
                pl.append('Enter\spassword\sfor\sbuild\/target\/product\/security\/shared\skey>')
                pl.append('done\.')

		os.chdir(self.tmpdir)
		print 'start sign the apks ..................'
		child = pexpect.spawn('./misc_sign_custpack_apks.py out/dist/full_%s-target_*.zip out/dist/sign_target_apks.zip' %(self.mtkProject))
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
		#docmd('mv out/target/product/%s/custpack.img out/target/product/%s/custpack.img_unsign' %(self.mtkProject,self.mtkProject))
		#docmd('mv out/target/product/%s/system.img out/target/product/%s/system.img_unsign'%(self.mtkProject,self.mtkProject))
		#docmd('mv out/target/product/%s/recovery.img out/target/product/%s/recovery.img_unsign' %(self.mtkProject,self.mtkProject))
		#docmd('mv out/target/product/%s/boot.img out/target/product/%s/boot.img_unsign' %(self.mtkProject,self.mtkProject))
		#docmd('cp out/dist/sign_img/custpack.img out/target/product/%s/' %(self.mtkProject))
		docmd('cp out/dist/sign_img/system.img out/target/product/%s/' %(self.mtkProject))
		docmd('cp out/dist/sign_img/recovery.img out/target/product/%s/' %(self.mtkProject))
		docmd('cp out/dist/sign_img/boot.img out/target/product/%s/' %(self.mtkProject))
                docmd('cp out/dist/sign_img/cache.img out/target/product/%s/' %(self.mtkProject))
                #2015-12-12 for pixi4-4 GMS move to data
                docmd('cp out/dist/sign_img/userdata.img out/target/product/%s/' %(self.mtkProject))
		#docmd('perl mediatek/build/tools/jrd_magic.pl %s' %(self.mtkProject))
		docmd('perl vendor/jrdcom/build/jrdmagic/jrd_magic.pl %s' %(self.mtkProject))
        
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
	if len(sys.argv)==3:
		dist = sign_apk(sys.argv[1],'pixi4-4_3g',sys.argv[2])
	else:
		dist = sign_apk(sys.argv[1],'pixi4-4_3g','pixi4_4')
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
