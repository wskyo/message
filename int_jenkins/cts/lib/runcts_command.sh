#!/bin/bash

#./runcts.sh /local/tools/adt-bundle-linux-x86_64-20130917/sdk V2C1F
#./runcts.sh V2C1F
#set -x
shopt -s expand_aliases

if [ $# -lt 1 ];then
  echo "Usage: Need Param1 as version "
  exit
fi
CTS_PATH=$CTS_PACKAGE_PATH
VERSION=$1
PACKAGE=$2
CLASS=$3
CASE=$5
RUNCOUNT=$5
PERSO=$VERSION
#SCRIPT_DIR=`pwd`
SCRIPT_DIR="/tmp/$VERSION-00"
if [[  -d $SCRIPT_DIR ]];then
    rm -rf $SCRIPT_DIR
fi

#CTS_PATH="/local/tools/adt-bundle-linux-x86_64-20130917/sdk"

CTS_TOOL_PATH=$CTS_PACKAGE_PATH/android-cts
RUNCTS="${CTS_TOOL_PATH}/tools/cts-tradefed"
CTSAPK_PATH="${CTS_TOOL_PATH}/repository/testcases"
GTS_TOOL_PATH="${CTS_PATH}/android-xts"

alias die='_die "[Error $BASH_SOURCE->$FUNCNAME:$LINENO]"'
# This function is used to cleanly exit any script. It does this showing a
# given error message, and exiting with an error code.
function _die
{
    echo -e "\033[31;1m==================================\033[0m"
    echo -e "\033[31;1m$@\033[0m"
    echo -e "\033[31;1m==================================\033[0m"
    exit 1
}

function checkctspatch()
{
    if [ ! -d "$CTS_TOOL_PATH" ]; then
        die "$CTS_TOOL_PATH is wrong!"
        exit
    fi 
}

function check_adb_devices()
{
    adbdvices=`adb devices | sed -n 2p`
    if [ "$adbdvices" = "" ];then
        die "NO adb devices"
    fi
}

function auto_done_cts()
{

    expect -c"
    set timeout -1
    spawn $1
    expect "*testResult.xml*"
    exec sleep 60
    send \"exit\r\"
    send \"\003\"
    expect eof
    exit
    "
}

function auto_done_ctsA()
{

    expect -c"
    set timeout -1
    spawn $1
    expect "*1.*"
    send \"1\r\"
    expect "*Choose*"
    send \"3\r\"
    expect "*Choose*"
    send \"1\r\"
    expect eof
    exit
    "
}



function copy_result()
{
    var=$1
    if [ "$var" = "cts" ]; then
        result_path=$CTS_TOOL_PATH
    else
        result_path=$GTS_TOOL_PATH
    fi

    cd $result_path/repository/results
    dir=`ls *.zip | sed -r 's/(.*).zip/\1/g'`
    echo $dir
    test -d $dir && echo "The result dir is:"$dir 
    mkdir -vp $SCRIPT_DIR/$var && \
    #cp -r $result_path/repository/results/$dir $SCRIPT_DIR/${VERSION}/$var  && \
    cp -r $result_path/repository/results $SCRIPT_DIR/$var  && \
    cp -r $result_path/repository/logs $SCRIPT_DIR/$var || die "copy result failed"
}

function enpty_result_dir()
{    if [ "$1" = "YES" ]; then 
          #remove cts old result
          if [[  -d $CTS_TOOL_PATH/repository/results ]];then
             test -d $CTS_TOOL_PATH/repository/oldresult && echo "oldresult dir is exist" || \
                 mkdir -vp $CTS_TOOL_PATH/repository/oldresult
             mv  $CTS_TOOL_PATH/repository/results/* $CTS_TOOL_PATH/repository/oldresult
             rm -rf $CTS_TOOL_PATH/repository/logs/*
         fi
     fi
}

function run_cts()
{
    #run cts test
    check_adb_devices
    if [ "$1" = "YES" ]; then 
        auto_done_cts "bash ${CTS_TOOL_PATH}/tools/cts-tradefed run cts --plan CTS"
    fi
    echo 'sleep 40'
    sleep 40
    copy_result cts

    adb reboot
    sleep 90
    cp -r /local/int_jenkins/cts/lib/bthrun ${CTS_TOOL_PATH}/tools
    cd ${CTS_TOOL_PATH}/tools/bthrun
    i=0
    local fail_count
    if [ "$2" = "" ]; then
        fail_count=3
    else
        fail_count=$2
    fi	
    echo "runch Fail count is $fail_count"
    
    while [ $i -lt $fail_count ]
        do
            check_adb_devices
            auto_done_cts "bash runnotpasscts.sh"
            i=`expr $i + 1`
        done
}

function run_cts_command()
{
    #run cts test
    check_adb_devices
    i=0
    if [ "$4" = "" ]; then
        fail_count=1
    else
        fail_count=$4
    fi
    while [ $i -lt $fail_count ]
        do
            if [ "$1" = "package" ] || [ "$1" = "class" ]; then 
	        if [ ! -z "$2" ]; then 
	            auto_done_cts "bash ${CTS_TOOL_PATH}/tools/cts-tradefed run cts -p $2"
	        fi
	    elif [ "$1" = "case" ]; then 
	            if [ ! -z "$2" ] && [ ! -z "$3" ]; then 
		        auto_done_cts "bash ${CTS_TOOL_PATH}/tools/cts-tradefed run cts -c $2 -m $3"
		    fi
	    fi
        i=`expr $i + 1`
        done

}

function main()
{
    checkctspatch
    #enpty_result_dir $DELERESULT  
    run_cts_command $PACKAGE $CLASS $CASE $RUNCOUNT
    copy_result cts
}
main
