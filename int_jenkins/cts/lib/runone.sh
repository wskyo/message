#!/bin/bash

#./runone.sh cts case android.hardware.camera2.cts.RecordingTest testBurstVideoSnapshot 3
#./runone.sh gts case android.hardware.camera2.cts.RecordingTest testBurstVideoSnapshot 3

CTS_TOOL_PATH=/local/tools/androidL/android-cts
GTS_TOOL_PATH=/local/tools/androidL/android-xts
#if [ -z "$1" ]; then
#	echo "Please input class or package or case "
#	exit 1
#fi



function auto_done_cts()
{

    expect -c"
    set timeout -1
    spawn $1
    expect "*generated*"
    exec sleep 60
    send \"exit\r\"
    send \"\003\"
    expect eof
    exit
    "
}

function run_gts_command()
{
    #run cts test
    #check_adb_devices
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
	            auto_done_cts "bash ${GTS_TOOL_PATH}/tools/xts-tradefed run xts -p $2"
	        fi
	    elif [ "$1" = "case" ]; then 
	            if [ ! -z "$2" ] && [ ! -z "$3" ]; then 
		        auto_done_cts "bash ${GTS_TOOL_PATH}/tools/xts-tradefed run xts -c $2 -m $3"
		    fi
	    fi
            i=`expr $i + 1`
        done

}

function run_cts_command()
{
    #run cts test
    #check_adb_devices
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

if [[ "$1" == "cts" ];then
    run_cts_command $2 $3 $4 $5
else
    run_gts_command $2 $3 $4 $5
fi
#run_cts_command 'case' android.hardware.camera2.cts.RecordingTest testBurstVideoSnapshot 100
#run_cts_command 'case' android.hardware.camera2.cts.RecordingTest testVideoSnapshot 100
#run_cts_command 'case' android.hardware.camera2.cts.RobustnessTest testMandatoryOutputCombinations 100
   


