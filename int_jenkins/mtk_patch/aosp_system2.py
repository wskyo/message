#!/usr/bin/python
#coding=utf-8
#
#aosp system.img 2
#

###
#GSI刷机步骤如下：
#1	adb reboot-bootloader
#2	long press Volume up key
'''	
=> FASTBOOT mode...
'''
#3	fastboot flashing unlock
'''
Unlock bootloader?

If you unlock the bootloader,you will be able to install cus
tom operating
system software on this phone.

A custom OS is not subject to the same testing as the origin
al OS, and can 
cause your phone and installed applications to stop working 
properly.

To prevent unauthorized accesss to your personal data,unlocki
ng the bootloader
will also delete all personal data from your phone(a "factor
y data reset").

Press the Volum UP/Down buttons to select Yes or No.

Yes (Volume UP):Unlock(may void warranty).

No (Volume Down):Do not unlock bootloader.
'''
#4	Press Volume up key
'''
Select Boot Mode:
[VOLUME_UP to select.VOLUME_DOWN is OK.]

[Recovery 	Mode]
[Fastboot 	Mode]		<<==
[Normal 	Boot]
=> FASTBOOT mode...
'''
#5	fastboot flash system /home/swd3/android-sdk-linux/GSIs/system_aosp_arm_a/system_aosp_arm_a_20180205.img
'''
USB Transferring...
'''
'''
USB Transferring...
USB Transmission OK Time:-296030ms Vel:0KB/s

Writing Flash
Write Data > 100% Time: 3s Vel:202796KB/s/s

OK
'''
#6	fastboot reboot

#img_dir			aosp img director
#sdk_platform_tools_dir 	sdk platform-tools director
#adb
import os,sys
import commands
import time

class operation_state(object):
	def __init__(self,img_dir):
		self.img_dir = img_dir
	def handle(self):
		pass
class reboot_bootloader(operation_state):
	def handle(self):
		while True:
			enable = raw_input("Please enable OEM unlocking and USB debugging in settings.Y|N:\n")
			if enable == "Y" or enable =="y" or enable== "":
				print "adb reboot-bootloader"
				os.system("adb reboot-bootloader")
				print "Long press Volume up key into FASTBOOT mode.And then you will see this at the bottom of the phone:"
				print "=> FASTBOOT mode..."
				#time.sleep(10)
				break
			elif enable == "N" or enable =="n":
				print "wait for 1s"
				time.sleep(1)
			else:
				print "invalid input!!!system exit."
				sys.exit(2)
	
class flashing_unlock(operation_state):
	def handle(self):
		while True:
			enable = raw_input("Do you see 'FASTBOOT mode...'?Y|N:\n")
			if enable == "Y" or enable =="y" or enable== "":
				print "fastboot flashing unlock"
				tmp_strs = \
'''
Unlock bootloader?

If you unlock the bootloader,you will be able to install cus
tom operating
system software on this phone.

A custom OS is not subject to the same testing as the origin
al OS, and can 
cause your phone and installed applications to stop working 
properly.

To prevent unauthorized accesss to your personal data,unlocki
ng the bootloader
will also delete all personal data from your phone(a "factor
y data reset").

Press the Volum UP/Down buttons to select Yes or No.

Yes (Volume UP):Unlock(may void warranty).

No (Volume Down):Do not unlock bootloader.
'''
				print "you will see something like this:"
				print tmp_strs
				print "Press Volum UP to unlock the bootloader."
				os.system("fastboot flashing unlock")
				enable = raw_input("Do you do this?Y|N:\n")
				while True:
					if enable == "Y" or enable =="y" or enable== "":
						print "you will see something like this:"
						tmp_strs = \
'''
Select Boot Mode:
[VOLUME_UP to select.VOLUME_DOWN is OK.]

[Recovery 	Mode]
[Fastboot 	Mode]		<<==
[Normal 	Boot]
=> FASTBOOT mode...
'''
						print tmp_strs
						time.sleep(1)
						break
					elif enable == "N" or enable =="n":
						print "wait for 1s"
						time.sleep(1)
					else:
						print "invalid input!!!system exit."
						sys.exit(2)
				break
			elif enable == "N" or enable =="n":
				print "wait for 1s"
				time.sleep(1)
			else:
				print "invalid input!!!system exit."
				sys.exit(2)

class flash(operation_state):
	def handle(self):
		print "fastboot flash system '%s'" % self.img_dir
		print "you will see something like this:"
		print "USB Transferring..."
		print "after fastboot flash finished,you will see something like this:"
		tmp_strs = \
'''
USB Transferring...
USB Transmission OK Time:-296030ms Vel:0KB/s

Writing Flash
Write Data > 100% Time: 3s Vel:202796KB/s/s

OK
'''
		print tmp_strs
		os.system("fastboot flash system '%s'" % self.img_dir)
		
		

class reboot(operation_state):
	def handle(self):
		print "fastboot reboot"
		os.system("fastboot reboot")
		print "All operation has been completed.Wait for the phone to reboot."

class environment(object):
	
	def __init__(self,dir_list):
		if type(dir_list) is str:
			dir_list = [dir_list]
		if len(dir_list) <= 0:
			print "env list memeber must be larger than 0"
			sys.exit(1)
		self._dir = ":".join(dir_list)
	def check_env(self,env_list = ['adb','fastboot']):
		if type(env_list) is str:
			env_list = [env_list]
		if len(env_list) <= 0:
			print "env list memeber must be larger than 0"
			sys.exit(1)
		assert type(env_list) is list,"env list must be string or list"
		env_ok = True	
		for env in env_list:
			#print "which %s" % env
			result = commands.getoutput("which %s" % env)
			#print result
			if len(result) > 0:
				env_ok = env_ok & True
			else:
				env_ok = env_ok & False
		#print env_ok
		#print self._dir
		#print commands.getoutput("echo $PATH")
		if not env_ok:
			os_path = os.getenv("PATH")
			os_path = os_path + ':' + self._dir
			os.putenv("PATH",os_path)	
		#print commands.getoutput("echo $PATH")
		#for env in env_list:
			#print "which %s" % env
			#result = commands.getoutput("which %s" % env)
			#print result


class contextFactory(object):
	def __init__(self,operations_list,img_dir):
		if type(operations_list) is str:
			operations_list = [operations_list]
		if type(operations_list) is list:
			self.operations_list = operations_list
		self.state = ''
		self.img_dir = img_dir
	def __next__(self):
		if len(self.operations_list) >0:
			self.operations_list.remove(self.operations_list[0])
			return True
		return False
	def __gene_state__(self):
		if len(self.operations_list)<=0:
			return ''
		_oper = self.check_expression(self.operations_list[0])
		if _oper:
			self.state = getattr(aosp,_oper)(img_dir)
			_next = self.__next__()
			if _next:
				return self.state
			else:
				return ''
		return ''
	def check_expression(self,operation):
		if operation:
			return 	operation
		return ''
	def operate(self):
		_state = self. __gene_state__()
		if _state:
			self.state.handle()
	def check_fish(self):
		if len(self.operations_list) > 0:
			return True
		return False

if __name__ == '__main__':
	
	operations = ['reboot_bootloader','flashing_unlock','flash','reboot']
	#img_dir	the img director of GSI IMG
	#img_dir = '/home/swd3/android-sdk-linux/GSIs/system-aosp_arm_a-4632655/system-aosp_arm_a-2018-02-05.img'
	#img_dir = '/home/swd3/android-sdk-linux/GSIs/system-aosp_arm_a-4632655/system-aosp_arm_a-2018-04-05.img'
	#img_dir = '/home/swd3/android-sdk-linux/GSIs/system-aosp_arm_a-4632655/system-aosp_arm_a-2018-05-05.img'
	#img_dir = '/home/swd3/android-sdk-linux/GSIs/system-aosp_arm_a-4632655/system-aosp_arm_a-2018-06-05.img'
	#img_dir = '/home/swd3/android-sdk-linux/GSIs/8.1_r4_arm_a/system-aosp_arm_a-2018-07-05.img'
	img_dir = '/home/swd3/android-sdk-linux/GSIs/8.1_r4_arm_a/system-aosp_arm_a-2018-08-05.img'
	pwd = os.getcwd()
	sys.path.append(pwd)
	aosp = __import__('aosp_system2')
	#env_dir	the platform-tools of the sdk director in your system
	env_dir = '/local/tools/adt-bundle-linux-x86_64-20151030/sdk/platform-tools'
	env = getattr(aosp,'environment')(env_dir)
	env.check_env()
	factory = contextFactory(operations,img_dir)
	while factory.check_fish():
		factory.operate()




