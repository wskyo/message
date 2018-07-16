#!/usr/bin/python

############################################################################
## this python will auto generate cts/gts test report.
## create by xueqin.zhang for autocts 2016-03-28
############################################################################
''' this class use to create report for test result, !!!'''

import ReleaseStyle

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import xlwt

row = 0
detail_row = 0
wight = 12

def create_testcase_report(worksheet, fail_count, title_dic=None, report_dic=None, body_dic=None):
    _create_title(worksheet, title_dic)
    _create_summary(worksheet, report_dic)
    _create_boby(worksheet, fail_count, body_dic, title_dic)



''' create report title use this method !!!'''
def _create_title(worksheet, title_dic=None):
    if title_dic != None and title_dic.__len__() != 0:
        keyStyle = ReleaseStyle.getDeviceInfoItemValueStyle()
        valueStyle = ReleaseStyle.getDeviceInfoItemKeyStyle()
        worksheet.write_merge(0, 1, 0, wight, title_dic.get('Title'), ReleaseStyle.getSheetTitleStyle())
        worksheet.col(0).width = 4000
        worksheet.write_merge(2, 2, 0, 1, 'Build Model', keyStyle)
        worksheet.col(1).width = 4000
        worksheet.write_merge(2, 2, 2, 3, title_dic.get('Build Model'), valueStyle)
        worksheet.col(2).width = 4000
        worksheet.col(3).width = 4000
        worksheet.write_merge(2, 2, 4, 5, 'Project Name', keyStyle)
        worksheet.col(4).width = 4000
        worksheet.col(5).width = 4000
        worksheet.write_merge(2, 2, 6, 7, title_dic.get('Project Name'), valueStyle)
        worksheet.col(6).width = 4000
        worksheet.col(7).width = 4000
        worksheet.write_merge(2, 2, 8, 9, 'Build Brand', keyStyle)
        worksheet.col(8).width = 4000
        worksheet.col(9).width = 4000
        worksheet.write_merge(2, 2, 10, 12, title_dic.get('Build Brand'), valueStyle)
        worksheet.col(10).width = 4000
        worksheet.col(11).width = 4000
        worksheet.col(12).width = 4000
        worksheet.write_merge(3, 3, 0, 1, 'DeviceId', keyStyle)
        worksheet.write_merge(3, 3, 2, 3, title_dic.get('DeviceId'), valueStyle)
        worksheet.write_merge(3, 3, 4, 5, 'Build Fingerprint', keyStyle)
        worksheet.write_merge(3, 3, 6, 12, title_dic.get('Build Fingerprint'), valueStyle)
        worksheet.write_merge(4, 4, 0, 1, 'Build Manufacturer', keyStyle)
        worksheet.write_merge(4, 4, 2, 3, title_dic.get('Build Manufacturer'), valueStyle)
        worksheet.write_merge(4, 4, 4, 5, 'Start Time', keyStyle)
        worksheet.write_merge(4, 4, 6, 7, title_dic.get('Start Time'), valueStyle)
        worksheet.write_merge(4, 4, 8, 9, 'End Time', keyStyle)
        worksheet.write_merge(4, 4, 10, 12, title_dic.get('End Time'), valueStyle)
    else:
        pass

''' create report sum use this method !!!'''
def _create_summary(worksheet, sum_dic=None):
    if sum_dic != None and sum_dic.__len__() != 0:
        sumTitleStyle = ReleaseStyle.getItemTitleStyle()
        sumItemStyle = ReleaseStyle.getPackSummaryItemKeyStyle()
        sumItemValueStyle = ReleaseStyle.getPackSummaryItemValueStyle()
        worksheet.write_merge(5, 6, 2, 9, 'Test Summary', sumTitleStyle)
        worksheet.write_merge(7, 7, 2, 3, "Tests Passed", sumItemStyle)
        worksheet.write_merge(7, 7, 4, 5, "Tests Failed", sumItemStyle)
        worksheet.write_merge(7, 7, 6, 7, "Tests Timed out", sumItemStyle)
        worksheet.write_merge(7, 7, 8, 9, "Tests Not Executed", sumItemStyle)

        worksheet.write_merge(8, 8, 2, 3, sum_dic.get('pass'), sumItemValueStyle)
        worksheet.write_merge(8, 8, 4, 5, sum_dic.get('failed'), sumItemValueStyle)
        worksheet.write_merge(8, 8, 6, 7, sum_dic.get('timeout'), sumItemValueStyle)
        worksheet.write_merge(8, 8, 8, 9, sum_dic.get('notExecuted'), sumItemValueStyle)


''' create report body !!! '''
def _create_boby(worksheet, count, body_dic=None, title_dic=None):
    detail_row = 9
    if body_dic != None and body_dic.__len__() != 0 and  count != 0:
        worksheet.write_merge(detail_row, detail_row+1, 0, 12, 'Test Failures (%d)' % count, ReleaseStyle.getItemTitleStyle())
        worksheet.row(detail_row+2).height = 350
        worksheet.write_merge(detail_row+2, detail_row+2, 0, 4, 'Test', ReleaseStyle.getPackFailuresItemKeyStyle())
        worksheet.write(detail_row+2, 5, 'Result', ReleaseStyle.getPackFailuresItemKeyStyle())
        worksheet.write_merge(detail_row+2, detail_row+2, 6, 12, 'Detail', ReleaseStyle.getPackFailuresItemKeyStyle())

        detail_row = detail_row + 3
        for key, value in body_dic.items():
            if value.__len__() != 0:
                detail_row = __create_body(worksheet, detail_row, key, value, title_dic)


''' create report fail test case detail message for search !!! '''
def __create_body(worksheet, row_detail, package_name, body_error_dic={}, title_dic=None):
    if body_error_dic != None and body_error_dic.__len__() != 0:
        worksheet.row(row_detail).height = 350
        worksheet.write_merge(row_detail, row_detail, 0, 12, 'Test Package: %s' %package_name, ReleaseStyle.getPackFailuresPackNameStyle())
    else:
        return row_detail
    row_detail = row_detail + 1

    for key, value in body_error_dic.items():
        color = 1

        worksheet.row(row_detail).height = 450
        worksheet.write_merge(row_detail, row_detail, 0, 4, key, ReleaseStyle.getPackFailuresItemValueStyle(1))
        worksheet.write(row_detail, 5, 'fail', ReleaseStyle.getPackFailuresItemValueStyle(2, color))
        worksheet.write_merge(row_detail, row_detail, 6, 12, unicode(value,'utf-8'), ReleaseStyle.getPackFailuresItemValueStyle(1))
        row_detail = row_detail + 1
    return row_detail





