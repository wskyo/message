#!/usr/bin/python
import re
import os
import sys
import commands
import xml.dom.minidom

def __checkFrameworkRes(dirA, dirB, path):
	isCompatible = True
	if path == 'frameworks/base':
		dirBack = os.getcwd()
		os.chdir(dirA)
		fileInA = commands.getoutput('find').split('\n')
		os.chdir(dirB)
		fileInB = commands.getoutput('find').split('\n')
		os.chdir(dirBack)
		for line in fileInB:
			if line not in fileInA:
				fileInA.append(line)
		for line in fileInA:
			line = re.sub('^\./', '', line)
			if re.match('core/res/AndroidManifest.xml', line) or re.match('core/res/assets/', line) or re.match('core/res/plf/', line):
				print 'Perso incompatible <phase checkFrameworkRes>: %s -> %s' % (path, line)
				isCompatible = False
			if re.match('core/res/res/', line) and not re.match('core/res/res/value-', line):
				print 'Perso incompatible <phase checkFrameworkRes>: %s -> %s' % (path, line)
				isCompatible = False
	return isCompatible

def __checkJrdRes(dirA, dirB, path):
	isCompatible = True
	if path == 'vendor/jrdcom':
		dirBack = os.getcwd()
		os.chdir(dirA)
		fileInA = commands.getoutput('find').split('\n')
		os.chdir(dirB)
		fileInB = commands.getoutput('find').split('\n')
		os.chdir(dirBack)
		for line in fileInB:
			if line not in fileInA:
				fileInA.append(line)
		for line in fileInA:
			line = re.sub('^\./', '', line)
			if re.match('jrdres/AndroidManifest.xml', line) or re.match('jrdres/assets/', line) or re.match('jrdres/plf/', line):
				print 'Perso incompatible <phase checkJrcRes>: %s -> %s' % (path, line)
				isCompatible = False
			if re.match('jrdres/res/', line) and not re.match('jrdres/res/value-', line):
				print 'Perso incompatible <phase checkJrcRes>: %s -> %s' % (path, line)
				isCompatible = False
	return isCompatible

def __checkRingTone(dirA, dirB, path):
	isCompatible = True
	if path == 'brandy_wimdata_ng/wcustores':
		dirBack = os.getcwd()
		os.chdir(dirA)
		fileInA = commands.getoutput('find').split('\n')
		os.chdir(dirB)
		fileInB = commands.getoutput('find').split('\n')
		os.chdir(dirBack)
		for line in fileInB:
			if line not in fileInA:
				fileInA.append(line)
		for line in fileInA:
			line = re.sub('^\./', '', line)
			if line == 'Audios/audio.zip':
				print 'Perso incompatible <phase checkRingTone>: %s -> %s' % (path, line)
				isCompatible = False
	return isCompatible

def __checkKeyLayout(dirA, dirB, path):
	isCompatible = True
	if path == 'device/qcom/msm7627_ffa':
		dirBack = os.getcwd()
		os.chdir(dirA)
		fileInA = commands.getoutput('find').split('\n')
		os.chdir(dirB)
		fileInB = commands.getoutput('find').split('\n')
		os.chdir(dirBack)
		for line in fileInB:
			if line not in fileInA:
				fileInA.append(line)
		for line in fileInA:
			line = re.sub('^\./', '', line)
			if line == 'plf/isdm_KeypadLayout.plf':
				print 'Perso incompatible <phase checkKeyLayout>: %s -> %s' % (path, line)
				isCompatible = False
	return isCompatible

def __checkSystemProperty(dirA, dirB, path):
	isCompatible = True
	if re.match('brandy_wimdata_ng', path):
		dirBack = os.getcwd()
		os.chdir(dirA)
		fileInA = commands.getoutput('find').split('\n')
		os.chdir(dirB)
		fileInB = commands.getoutput('find').split('\n')
		os.chdir(dirBack)
		for line in fileInB:
			if line not in fileInA:
				fileInA.append(line)
		for line in fileInA:
			line = re.sub('^\./', '', line)
			if re.search('\.plf$', line):
				print 'Perso incompatible <phase checkSystemProperty>: %s -> %s' % (path, line)
				isCompatible = False
	return isCompatible

def __checkShareLibrary(dirA, dirB, path):
	isCompatible = True
	if path == 'brandy_wimdata_ng/wcustores':
		dirBack = os.getcwd()
		os.chdir(dirA)
		fileInA = commands.getoutput('find').split('\n')
		os.chdir(dirB)
		fileInB = commands.getoutput('find').split('\n')
		os.chdir(dirBack)
		for line in fileInB:
			if line not in fileInA:
				fileInA.append(line)
		for line in fileInA:
			line = re.sub('^\./', '', line)
			if re.search('\.so$', line):
				print 'Perso incompatible <phase checkShareLibrary>: %s -> %s' % (path, line)
				isCompatible = False
	return isCompatible

def __checkGMS(dirA, dirB, path):
	isCompatible = True
	if path == 'vendor/aosp':
		dirBack = os.getcwd()
		os.chdir(dirA)
		fileInA = commands.getoutput('find').split('\n')
		os.chdir(dirB)
		fileInB = commands.getoutput('find').split('\n')
		os.chdir(dirBack)
		for line in fileInB:
			if line not in fileInA:
				fileInA.append(line)
		for line in fileInA:
			line = re.sub('^\./', '', line)
			if re.match('google/', line) and not re.search('\.apk$', line):
				print 'Perso incompatible <phase checkGMS>: %s -> %s' % (path, line)
				isCompatible = False
	return isCompatible

def __checkFont(dirA, dirB, path):
	isCompatible = True
	if path == 'brandy_wimdata_ng/wcustores':
		dirBack = os.getcwd()
		os.chdir(dirA)
		fileInA = commands.getoutput('find').split('\n')
		os.chdir(dirB)
		fileInB = commands.getoutput('find').split('\n')
		os.chdir(dirBack)
		for line in fileInB:
			if line not in fileInA:
				fileInA.append(line)
		for line in fileInA:
			line = re.sub('^\./', '', line)
			if re.match('font/', line):
				print 'Perso incompatible <phase checkFont>: %s -> %s' % (path, line)
				isCompatible = False
	return isCompatible

def __checkPlf(dirA, dirB, path):
	isCompatible = True
	dirBack = os.getcwd()
	os.chdir(dirA)
	fileInA = commands.getoutput('find').split('\n')
	os.chdir(dirB)
	fileInB = commands.getoutput('find').split('\n')
	os.chdir(dirBack)
	for line in fileInB:
		if line not in fileInA:
			fileInA.append(line)
	for line in fileInA:
		line = re.sub('^\./', '', line)
		if re.search('\.plf$', line):
			print 'Perso incompatible <phase checkPLF>: %s -> %s' % (path, line)
			isCompatible = False
	return isCompatible

def checkPersoCompatible(dirA, dirB, path):
	'''
	isCompatible = True
	if not __checkFrameworkRes(dirA, dirB, path):
		isCompatible = False
	if not __checkJrdRes(dirA, dirB, path):
		isCompatible = False
	if not __checkRingTone(dirA, dirB, path):
		isCompatible = False
	if not __checkKeyLayout(dirA, dirB, path):
		isCompatible = False
	if not __checkSystemProperty(dirA, dirB, path):
		isCompatible = False
	if not __checkShareLibrary(dirA, dirB, path):
		isCompatible = False
	if not __checkGMS(dirA, dirB, path):
		isCompatible = False
	if not __checkFont(dirA, dirB, path):
		isCompatible = False
	if not __checkPlf(dirA, dirB, path):
		isCompatible = False
	return isCompatible
	'''
	return False

def checkPersoIncompatible(dirA, dirB, path):
	return not checkPersoCompatible(dirA, dirB, path)
