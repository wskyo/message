#!/usr/bin/python

############################################################################
## Style be user to create Style for html 
## add by jianbo.deng for superspam modified 2013-08-27
############################################################################

from pyExcelerator import *

class ReleaseStyle:

	def getDaulftBorder(self):
		borders = Borders()
		borders.left = 1
		borders.right = 1
		borders.top = 1
		borders.bottom = 1
		return borders
	
	def getReleaseNoteTitleStyle(self, color = 0):
		fnt = Font()
		fnt.name = 'Arial'
		fnt.colour_index = 0
		fnt.bold = True
		fnt.height=260
		borders=self.getDaulftBorder()
		al = Alignment()
		al.horz = Alignment.HORZ_CENTER
		al.vert = Alignment.VERT_CENTER
		pattern = Pattern()
		pattern.pattern=1
		pattern.pattern_fore_colour=color
		pattern.pattern_back_colour=color #17, 5
		fnt.height=280
		#fnt.height=220
		style = XFStyle()
		style.font = fnt
		style.borders = borders
		style.alignment = al
		style.pattern=pattern
	        return style
	
	def getHeadTitleItemStyle(self):
		fnt = Font()
		fnt.name = 'Arial'
		fnt.colour_index = 0
		fnt.bold = True
		fnt.height=200
		borders=self.getDaulftBorder()
		al = Alignment()
		al.horz = Alignment.HORZ_RIGHT
		al.vert = Alignment.VERT_CENTER
		style = XFStyle()
		style.font = fnt
		style.borders = borders
		style.alignment = al
		return style
	
	def getHeadTitleItemInfoStyle(self, big=False, bold=False, center=False):
		fnt = Font()
		fnt.name = 'Arial'
		fnt.colour_index = 0
		if big:
			fnt.height=250
		else:
			fnt.height=200
		fnt.bold = bold
		borders=self.getDaulftBorder()
		al = Alignment()
		if center:
			al.horz = Alignment.HORZ_CENTER
		else:
			al.horz = Alignment.HORZ_LEFT
		al.vert = Alignment.VERT_CENTER
		style = XFStyle()
		style.font = fnt
		style.borders = borders
		style.alignment = al
		return style
	
	def getBodyTitleStyle(self):
		fnt = Font()
		fnt.name = 'Arial'
		fnt.colour_index = 0
		fnt.bold = True
		fnt.height=200
		borders=self.getDaulftBorder()
		al = Alignment()
		al.horz = Alignment.HORZ_CENTER
		al.vert = Alignment.VERT_CENTER
		pattern = Pattern()
		pattern.pattern=1
		pattern.pattern_fore_colour=50
		pattern.pattern_back_colour=50
		style = XFStyle()
		style.font = fnt
		style.borders = borders
		style.alignment = al
		style.pattern=pattern
		return style

	# add by lyf  
	def getHighLightBodyStyle(self,color = 0):
		fnt = Font()
		fnt.name = 'Arial'
		fnt.colour_index = color
		fnt.bold = False
		fnt.height=200
		borders=self.getDaulftBorder()
		al = Alignment()
		al.horz = Alignment.HORZ_LEFT
		al.vert = Alignment.VERT_CENTER
		#pattern = Pattern()
		#pattern.pattern=1
		#pattern.pattern_fore_colour=color
		#pattern.pattern_back_colour=color
		style = XFStyle()
		style.font = fnt
		style.borders = borders
		style.alignment = al
		#style.pattern=pattern
		return style
	# end by lyf
	
	def getBodyInfoStyle(self, color = 0):
		fnt = Font()
		fnt.name = 'Arial'
		fnt.colour_index = color
		fnt.bold = False
		fnt.height=200
		borders=self.getDaulftBorder()
		al = Alignment()
		al.horz = Alignment.HORZ_LEFT
		al.vert = Alignment.VERT_CENTER
		style = XFStyle()
		style.font = fnt
		style.borders = borders
		style.alignment = al
		return style

	def getCheckListFont(self, height=200, bold=False, center=False, index=0):
		fnt = Font()	
		fnt.name = 'Arial'
		fnt.colour_index = index
		fnt.height = height
		fnt.bold = bold
		borders=self.getDaulftBorder()
		al = Alignment()
		if center:
			al.horz = Alignment.HORZ_CENTER
		else:
			al.horz = Alignment.HORZ_LEFT
		al.vert = Alignment.VERT_CENTER
		style = XFStyle()
		style.font = fnt
		style.borders = borders
		style.alignment = al
		return style
	
	def getCheckListColorFont(self, height=200, bold=False, center=False, color=0):
		fnt = Font()	
		fnt.name = 'Arial'
		fnt.colour_index = 0
		fnt.height = height
		fnt.bold = bold
		borders=self.getDaulftBorder()
		al = Alignment()
		if center:
			al.horz = Alignment.HORZ_CENTER
		else:
			al.horz = Alignment.HORZ_LEFT
		al.vert = Alignment.VERT_CENTER
		pattern = Pattern()
		pattern.pattern=1
		pattern.pattern_fore_colour = color
		pattern.pattern_back_colour = color
		style = XFStyle()
		style.font = fnt
		style.borders = borders
		style.alignment = al
		style.pattern=pattern
		return style
