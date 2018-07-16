#!/usr/bin/python

############################################################################
## From teleweb,get the last version,and calulate the next version num
## add by renzhi.yang for superspam create 2014-12-26
###########################################################################
class  GetVesion(conf):
	## get the apk version number from teleweb
	def getVerNumber(self,conf,appname):
		TelewebApk = getoutput("ssh sl_hz_hran@10.92.32.26 ls /mfs/teleweb/genericapp/%s | grep '0' | sort | tail -1" % appname)
		match = re.match('.*\.(\d+)\.(\d+)$',TelewebApk)
		lastversion = match.group(1)
		if re.match('^000(\d)',lastversion):
			match = re.match('^000(\d)',lastversion)
			num = (int(match.group(1))+1)
			if num==10:
				curversion = "0010"
			else:
				curversion = ("000"+ "%s") % num

		elif re.match('^00(\d\d)',lastversion):
			match = re.match('^00(\d\d)',lastversion)
			num = (int(match.group(1))+1)
			if num==100:
				curversion = "0100"
			else:
				curversion = ("00"+ "%s") % num

		elif re.match('^0(\d\d\d)',lastversion):
			match = re.match('^0(\d\d\d)',lastversion)
			num = (int(match.group(1))+1)
			if num==1000:
				curversion = "1000"
			else:
				curversion = "%s" % num

		NextTelewebApk = TelewebApk.replace(lastversion,curversion)
		print "The lastversion is %s" % TelewebApk
		print "The current version is %s" % NextTelewebApk

		match = re.match('v(.*)',TelewebApk)
		if match:
			TelewebApk = match.group(1)

		match = re.match('v(.*)',NextTelewebApk)
		if match:
			NextTelewebApk = match.group(1)
		print [NextTelewebApk,TelewebApk]		
		return [NextTelewebApk,TelewebApk]


