#!/usr/bin/bash
#coding=utf-8
#set up enviroment for android development
#android开发环境配置
#

#java setup
#
function java_home_setup
{
   export JAVA_HOME=/home/oem/tools/java/jdk1.8.0_181/bin
   export JAVA_LIB=/home/oem/tools/java/jdk1.8.0_181/lib
   export JAVA_BIN=/home/oem/tools/java/jdk1.8.0_181/bin
   export CLASSPATH=.:$JAVA_LIB/tools.jar:$JAVA_LIB/dt.jar
   export PATH=$PATH:$JAVA_HOME
}

java_home_setup
