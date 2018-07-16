#!/bin/bash

#./runcts.sh /local/tools/adt-bundle-linux-x86_64-20130917/sdk V2C1F
#./runcts.sh V2C1F
#set -x
shopt -s expand_aliases

if [ $# -lt 4 ];then
  echo "Usage: Need 4 Params!!!! "
  exit
fi
CTS_PATH=$CTS_PACKAGE_PATH
VERSION=$1
DELERESULT=$2
RUNCOUNT=$3
DEVICEID=$4
RESOUT_DIR=$5
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
    local goin=0
    adbdvices=`adb devices | sed 1d `
    if [ "$adbdvices" = "" ];then
        die "NO adb devices"
    else
        arr=(${adbdvices//"devices"/})
        for deviceid in ${arr[@]}
        do
            if [ "$deviceid" = "$1" ];then
              let "goin = 1"
            fi
        done
        if((goin == 0)); then
              die "The devices is error"
        fi
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
    #check_adb_devices $3
    if [ "$1" = "YES" ]; then 
    	tmpdirname=(16#`dd if=/dev/urandom bs=1 count=4 2>/dev/null| od -A n -t x4|sed s/[^1-9a-fA-F]//g`)
	echo $tmpdirname
        #auto_done_cts "bash ${CTS_TOOL_PATH}/tools/cts-tradefed run cts --plan CTS"
 	auto_done_cts "bash ${CTS_TOOL_PATH}/tools/cts-tradefed run cts -s $3 --plan CTS" 2>&1 |tee  /tmp/$tmpdirname.log
	echo "get dir name"
	getresultname $tmpdirname
    fi
    echo 'sleep 90'
    #sleep 40
    #copy_result cts

    #adb -s $3 reboot
    sleep 90
    cp -r /local/int_jenkins/cts/lib/athrun ${CTS_TOOL_PATH}/tools
    cd ${CTS_TOOL_PATH}/tools/athrun
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
            #check_adb_devices $3
            auto_done_cts "bash runnotpasscts.sh $3 $RESOUT_DIR"
            i=`expr $i + 1`
        done
}

function checktmplog()
{
    if [ -s /tmp/$1.log ]; then
	rm -rf /tmp/$1.log
    fi
}

function getresultname()
{
    echo "/tmp/$1.log"
    if [ -s /tmp/$1.log ]; then
	line=`sed -n '1,20p' /tmp/$1.log |grep '[0-9]\{4\}\.[0-9]\{2\}\.[0-9]\{2\}_[0-9]\{2\}.[0-9]\{2\}\.[0-9]\{2\}'`
	RESOUT_DIR=$(echo $line | sed '/.*Created result dir.\(.*\)/ s//\1/')
	echo $RESOUT_DIR
    else
	echo "Can't get cts result dir!!!"
	exit 1;
    fi
}

function main()
{
    checkctspatch
    #enpty_result_dir $DELERESULT  
    run_cts $DELERESULT $RUNCOUNT $DEVICEID $RESOUT_DIR
    #copy_result cts
}
main
