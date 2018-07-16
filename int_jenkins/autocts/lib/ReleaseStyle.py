#!/usr/bin/python

############################################################################
## Style be user to create Style for html
## need xlwt module
## add by xueqin.zhang for autocts modified 2016-03-29
############################################################################

import xlwt


def getDaulftBorder():
    borders = xlwt.Borders()
    borders.left = 1
    borders.right = 1
    borders.top = 1
    borders.bottom = 1
    return borders

def getSheetTitleStyle():
    return getTitleStyle(17)

def getItemTitleStyle():
    return getTitleStyle(5)

def getDeviceInfoItemKeyStyle():
    fnt = xlwt.Font()
    fnt.name = 'Arial'
    fnt.colour_index = 0
    fnt.bold = False
    fnt.height=230
    borders=getDaulftBorder()
    al = xlwt.Alignment()
    al.horz = xlwt.Alignment.HORZ_LEFT
    al.vert = xlwt.Alignment.VERT_CENTER
    style = xlwt.XFStyle()
    style.font = fnt
    style.borders = borders
    style.alignment = al
    return style

def getDeviceInfoItemValueStyle():
    fnt = xlwt.Font()
    fnt.name = 'Arial'
    fnt.colour_index = 0
    fnt.bold = True
    fnt.height=230
    borders=getDaulftBorder()
    al = xlwt.Alignment()
    al.horz = xlwt.Alignment.HORZ_LEFT
    al.vert = xlwt.Alignment.VERT_CENTER
    style = xlwt.XFStyle()
    style.font = fnt
    style.borders = borders
    style.alignment = al
    return style

def getSummaryItemKeyStyle():
    fnt = xlwt.Font()
    fnt.name = 'Arial'
    fnt.colour_index = 0
    fnt.bold = False
    fnt.height=230
    borders=getDaulftBorder()
    al = xlwt.Alignment()
    al.horz = xlwt.Alignment.HORZ_CENTER
    al.vert = xlwt.Alignment.VERT_CENTER
    pattern = xlwt.Pattern()
    pattern.pattern=1
    pattern.pattern_fore_colour=30
    pattern.pattern_back_colour=30
    style = xlwt.XFStyle()
    style.font = fnt
    style.borders = borders
    style.alignment = al
    style.pattern=pattern
    return style

def getSummaryItemValueStyle():
    fnt = xlwt.Font()
    fnt.name = 'Arial'
    fnt.colour_index = 0
    fnt.bold = False
    fnt.height=230
    borders=getDaulftBorder()
    al = xlwt.Alignment()
    al.horz = xlwt.Alignment.HORZ_CENTER
    al.vert = xlwt.Alignment.VERT_CENTER
    style = xlwt.XFStyle()
    style.font = fnt
    style.borders = borders
    style.alignment = al
    return style

def getPackSummaryItemKeyStyle():
    fnt = xlwt.Font()
    fnt.name = 'Arial'
    fnt.colour_index = 0
    fnt.bold = False
    fnt.height=230
    borders=getDaulftBorder()
    al = xlwt.Alignment()
    al.horz = xlwt.Alignment.HORZ_CENTER
    al.vert = xlwt.Alignment.VERT_CENTER
    pattern = xlwt.Pattern()
    pattern.pattern=1
    pattern.pattern_fore_colour=30
    pattern.pattern_back_colour=30
    style = xlwt.XFStyle()
    style.font = fnt
    style.borders = borders
    style.alignment = al
    style.pattern=pattern
    return style

def getPackSummaryItemValueStyle(horz = 2, color = 0):
    fnt = xlwt.Font()
    fnt.name = 'Arial'
    fnt.colour_index = 0
    fnt.bold = False
    fnt.height=230
    borders=getDaulftBorder()
    al = xlwt.Alignment()
    if horz == 1:
        al.horz = xlwt.Alignment.HORZ_LEFT
    elif horz == 2:
        al.horz = xlwt.Alignment.HORZ_CENTER
    else:
        al.horz = xlwt.Alignment.HORZ_RIGHT
    al.vert = xlwt.Alignment.VERT_CENTER
    pattern = xlwt.Pattern()
    pattern.pattern=1
    if color == 1:
        pattern.pattern_fore_colour=2
        pattern.pattern_back_colour=2
    elif color == 2:
        pattern.pattern_fore_colour=7
        pattern.pattern_back_colour=7
    elif color == 3:
        pattern.pattern_fore_colour=22
        pattern.pattern_back_colour=22
    else:
        pattern.pattern_fore_colour=0x2A
        pattern.pattern_back_colour=0x2A
    style = xlwt.XFStyle()
    style.font = fnt
    style.borders = borders
    style.alignment = al
    style.pattern=pattern
    return style

def getPackNameStyle():
    fnt = xlwt.Font()
    fnt.name = 'Georgia'
    fnt.colour_index = 0x0C #blue
    fnt.bold = False
    fnt.height=210
    borders=getDaulftBorder()
    al = xlwt.Alignment()
    al.horz = xlwt.Alignment.HORZ_LEFT
    al.vert = xlwt.Alignment.VERT_CENTER
    pattern = xlwt.Pattern()
    pattern.pattern=1
    pattern.pattern_fore_colour=0x2A	#light_green
    pattern.pattern_back_colour=0x2A
    style = xlwt.XFStyle()
    style.font = fnt
    style.borders = borders
    style.alignment = al
    style.pattern=pattern
    return style

def getPackFailuresPackNameStyle():
    fnt = xlwt.Font()
    fnt.name = 'Arial'
    fnt.colour_index = 0
    fnt.bold = False
    fnt.height=230
    borders=getDaulftBorder()
    al = xlwt.Alignment()
    al.horz = xlwt.Alignment.HORZ_LEFT
    al.vert = xlwt.Alignment.VERT_CENTER
    pattern = xlwt.Pattern()
    pattern.pattern=1
    pattern.pattern_fore_colour=0x11
    pattern.pattern_back_colour=0x11
    style = xlwt.XFStyle()
    style.font = fnt
    style.borders = borders
    style.alignment = al
    style.pattern=pattern
    return style

def getPackFailuresItemKeyStyle():
    fnt = xlwt.Font()
    fnt.name = 'Arial'
    fnt.colour_index = 0
    fnt.bold = False
    fnt.height=230
    borders=getDaulftBorder()
    al = xlwt.Alignment()
    al.horz = xlwt.Alignment.HORZ_CENTER
    al.vert = xlwt.Alignment.VERT_CENTER
    pattern = xlwt.Pattern()
    pattern.pattern=1
    pattern.pattern_fore_colour=30
    pattern.pattern_back_colour=30
    style = xlwt.XFStyle()
    style.font = fnt
    style.borders = borders
    style.alignment = al
    style.pattern=pattern
    return style

def getPackFailuresItemValueStyle(horz = 2, color = 0):
    fnt = xlwt.Font()
    fnt.name = 'Arial'
    fnt.colour_index = 0
    fnt.bold = False
    fnt.height=230
    borders=getDaulftBorder()
    al = xlwt.Alignment()
    if horz == 1:
        al.horz = xlwt.Alignment.HORZ_LEFT
    elif horz == 2:
        al.horz = xlwt.Alignment.HORZ_CENTER
    else:
        al.horz = xlwt.Alignment.HORZ_RIGHT
    al.vert = xlwt.Alignment.VERT_CENTER
    pattern = xlwt.Pattern()
    pattern.pattern=1
    if color == 1:
        pattern.pattern_fore_colour=2
        pattern.pattern_back_colour=2
    elif color == 2:
        pattern.pattern_fore_colour=7
        pattern.pattern_back_colour=7
    elif color == 3:
        pattern.pattern_fore_colour=22
        pattern.pattern_back_colour=22
    else:
        pattern.pattern_fore_colour=0x2A	#light_green
        pattern.pattern_back_colour=0x2A
    style = xlwt.XFStyle()
    style.font = fnt
    style.borders = borders
    style.alignment = al
    style.pattern=pattern
    return style

#private method
def getTitleStyle(color):
    fnt = xlwt.Font()
    fnt.name = 'Arial'
    fnt.colour_index = 0
    fnt.bold = True
    fnt.height=260
    borders=getDaulftBorder()
    al = xlwt.Alignment()
    al.horz = xlwt.Alignment.HORZ_CENTER
    al.vert = xlwt.Alignment.VERT_CENTER
    pattern = xlwt.Pattern()
    pattern.pattern=1
    pattern.pattern_fore_colour=color
    pattern.pattern_back_colour=color #17, 5
    style = xlwt.XFStyle()
    style.font = fnt
    style.borders = borders
    style.alignment = al
    style.pattern=pattern
    return style
