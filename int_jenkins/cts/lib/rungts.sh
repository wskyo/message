#!/bin/bash

#./rungts.sh /local/tools/adt-bundle-linux-x86_64-20130917/sdk V5B1G-5

#set -x
shopt -s expand_aliases

if [ $# -lt 1 ];then
  echo "Usage: Need Param1 as version "
  exit
fi
CTS_PATH=$CTS_PACKAGE_PATH
VERSION=$1
DELERESULT=$2
RUNCOUNT=$3
PERSO=$VERSION
#SCRIPT_DIR=`pwd`
SCRIPT_DIR="/tmp/$VERSION-00"
if [[  -d $SCRIPT_DIR ]];then
    rm -rf $SCRIPT_DIR
fi

#CTS_PATH="/local/tools/adt-bundle-linux-x86_64-20130917/sdk"

CTS_TOOL_PATH=$CTS_PACKAGE_PATH/android-cts
RUNCTS="${CTS_TOOL_PATH}/tools/cts-tradefed"
#CTSAPK_PATH="${CTS_TOOL_PATH}/repository/testcases"
GTS_TOOL_PATH="${CTS_PATH}/android-xts"
CTSAPK_PATH="${GTS_TOOL_PATH}/repository/testcases"

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

function checkgtspatch()
{
    if [ ! -d "$GTS_TOOL_PATH" ]; then
        die "$GTS_TOOL_PATH is wrong!"
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

function auto_done_gts()
{

    expect -c"
    set timeout -1
    spawn $1
    expect "*TestResult.xml*"
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
    test -d $dir && echo "The result dir is:"$dir || unzip *.zip
    mkdir -vp $SCRIPT_DIR/${VERSION}/$var && \
    
    cp -r $result_path/repository/results $SCRIPT_DIR/${VERSION}/$var  && \
    cp -r $result_path/repository/logs $SCRIPT_DIR/${VERSION}/$var || die "move result failed"
}

function enpty_result_dir()
{
   if [ "$var" = "cts" ]; then
        result_path=$CTS_TOOL_PATH
    else
        result_path=$GTS_TOOL_PATH
    fi
    if [ "$1" = "YES" ]; then 
          #remove cts old result
          if [[  -d $result_path/repository/results ]];then
             test -d $result_path/repository/oldresult && echo "oldresult dir is exist" || \
                 mkdir -vp $result_path/repository/oldresult
             mv  $result_path/repository/results/* $result_path/repository/oldresult
             rm -rf $result_path/repository/logs/*
         fi
     fi
}

function run_gts()
{
    #remove gts old result

    check_adb_devices
    if [ "$1" = "YES" ]; then 
	    expect -c"
		    set timeout -1
		    spawn bash ${GTS_TOOL_PATH}/tools/xts-tradefed run xts --plan XTS
		    expect {
		        "*generated*" { send exit\r\n; send \003 ; interact }
		        eof { exit }
		    }
		    exit
		    "
    fi
    copy_result gts

    local fail_count
    if [ "$2" = "" ]; then
        fail_count=3
    else
        fail_count=$2
    fi	

    cp -r /local/int_jenkins/cts/lib/gthrun ${GTS_TOOL_PATH}/tools
    cd ${GTS_TOOL_PATH}/tools/gthrun
 #   sed -i 's/cts/xts/g'  ${GTS_TOOL_PATH}/tools/bthrun/*
 #   sed -i 's/testResult.xml/xtsTestResult.xml/g' ${GTS_TOOL_PATH}/tools/athrun/*
  #  cd ${GTS_TOOL_PATH}/tools/bthrun && mv runcts.py runxts.py
    i=0
    echo "runch Fail count is $fail_count"
    while [ $i -lt $fail_count ]
        do
        #    $SCRIPT_DIR/lib/runcts.py ${GTS_TOOL_PATH}/tools/bthrun runnotpasscts 
            check_adb_devices
            auto_done_gts "bash runnotpasscts.sh"
            i=`expr $i + 1`
        done
    

}


function main()
{
    checkgtspatch
    enpty_result_dir $DELERESULT  
    run_gts $DELERESULT $RUNCOUNT
    copy_result gts
}
main
