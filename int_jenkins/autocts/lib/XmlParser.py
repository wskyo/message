#!/usr/bin/python

############################################################################
## this class will read and analyse xml result.
## create by xueqin.zhang for autocts 2016-03-26
############################################################################

from xml.etree import ElementTree
from InterfaceUtils import *

class XmlParser():
    def __init__(self, file):
        self.file = file
        self.__total_testcase_methods_num = 0
        self.__fail_count = 0

    def get_result_devices_dic(self,file,conf):
        result_devices_dic = {}
        root = ElementTree.fromstring(open(file).read())
        result_devices_dic['Start Time'] = root.attrib['starttime']
        result_devices_dic['End Time'] = root.attrib['endtime']
        result_devices_dic['Plan Name'] = root.attrib['testPlan']
        result_devices_dic['Title'] = 'Test Report for Google %s test' %(root.attrib['testPlan'])
        testtype = conf.getConf('testtype', 'Test Type').upper()

        if testtype == 'CTS':
            for child in root:
                if child.tag == 'DeviceInfo':
                    listnode = child.getchildren()
                    for l_node in listnode:
                        if l_node.tag == 'BuildInfo':
                            result_devices_dic['DeviceId'] = l_node.attrib['deviceID']
                            result_devices_dic['Build Model'] = l_node.attrib['build_model']
                            result_devices_dic['Project Name'] = l_node.attrib['build_device']
                            result_devices_dic['Build Fingerprint'] = l_node.attrib['build_fingerprint']
                            result_devices_dic['Build Brand'] = l_node.attrib['build_brand']
                            result_devices_dic['Build Manufacturer'] = l_node.attrib['build_manufacturer']
                    return result_devices_dic

        elif testtype == 'GTS':
            for child in root:
                if child.tag == 'DeviceInfo':
                    listnode = child.getchildren()
                    for l_node in listnode:
                        if l_node.tag == 'BuildInfo':
                            result_devices_dic['DeviceId'] = l_node.attrib['deviceId']
                            result_devices_dic['Build Model'] = l_node.attrib['buildModel']
                            result_devices_dic['Project Name'] = l_node.attrib['buildDevice']
                            result_devices_dic['Build Fingerprint'] = l_node.attrib['buildFingerprint']
                            result_devices_dic['Build Brand'] = l_node.attrib['buildBrand']
                            result_devices_dic['Build Manufacturer'] = l_node.attrib['buildManufacturer']
                    return result_devices_dic


    def get_result_summary_dic(self,file):
        result_summary_dic = {}
        root = ElementTree.fromstring(open(file).read())
        for child in root:
            if child.tag == 'Summary':
                result_summary_dic = child.attrib
                return result_summary_dic


    def get_testpackage_result_dic(self,file):
        list_method_result = {}
        list_class_result = []
        list_package_result = []
        package_name = ''  
        testpackage_result_dic = {}

        root = ElementTree.fromstring(open(file).read())
        packagenode = root.getiterator('TestPackage')
        #print packagenode
        for package_node in packagenode:
            if package_node is not None:
                package_name = package_node.attrib['appPackageName']

                list_method_result = {}
                list_class_result = []
   
                for node in package_node:
                    str_tmp = ''
                    self.__read_node(node, str_tmp, list_method_result, list_class_result, list_package_result, package_name)
                    if list_method_result != {}:    
                        list_package_result.append(package_name)
                        testpackage_result_dic[package_name] =  list_method_result
        return testpackage_result_dic


    def __read_node(self, node, str_tmp, list_method_result, list_class_result, list_package_result, package_name):
        if node is not None:
            for node_item in node:
                if node_item.tag == 'TestSuite':
                    if str_tmp != '':
                        str_new = '%s.%s' %(str_tmp, node_item.attrib['name'])
                    else:
                        str_new = node_item.attrib['name']
                    self.__read_node(node_item.getchildren(), str_new, list_method_result, list_class_result, list_package_result, package_name)
                elif node_item.tag == 'TestCase':
                    str_new = '%s.%s' %(str_tmp, node_item.attrib['name'])
                    list_class_result.append(str_new)
                    self.__read_node(node_item.getchildren(), str_new, list_method_result, list_class_result, list_package_result, package_name)
                elif node_item.tag == 'Test':
                    if node_item.attrib.has_key("name") > 0:
                        if node_item.attrib['result'] == "fail":
                            key_item = '%s--%s' %(str_tmp, node_item.attrib['name'])

                            testnode = node_item.getchildren()
                            for littlenode in testnode:
                                if littlenode.tag == 'FailedScene':
                                    list_method_result[key_item] = littlenode.attrib['message']
                                    self.__fail_count += 1
                    else:
                        print "testresult xml error !!!"
                    self.__total_testcase_methods_num += 1

                else:
                    return ''

        else:
            return ''


    def get_total_testcase_methods_num(self):
        return self.__total_testcase_methods_num


    def get_total_fail_num(self):
        return self.__fail_count










        


