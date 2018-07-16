#!/bin/bash
#run gts at time

if [ -z "$1" ]; then
	echo "Please input test Phone deviceId"
	exit 1
fi
if [ -z "$2" ]; then
	echo "Please input Camera Phone deviceId"
	exit 1
fi

if [ -z "$3" ]; then
	echo "Please run on time,like 21:00"
	exit 1
fi
source /local/int_jenkins/cts/lib/menvsetup.sh
GTS_TOOL_PATH="${CTS_PACKAGE_PATH}/android-xts"
echo $GTS_TOOL_PATH 

function check_adb_devices()
{
    adbdvices=`adb devices | sed -n 2p`
    if [ "$adbdvices" = "" ];then
        die "NO adb devices"
    fi
}

function start_camera_vedio()
{
    echo "start camera phone $1"
    adb -s $1 shell am start -n com.jrdcom.android.gallery3d/com.android.jrdcamera.Camera #start camera
    sleep 5 
    adb -s $1 shell input tap 420 750 #move camera to video
    sleep 5 
    adb -s $1 shell input tap 245 735 #start video
    sleep 1 
    echo "now  camera recodeing .... $1"
}

function run_gts()
{
    #check_adb_devices
    clear
    set -x
    adb -s $1 shell getprop | grep -rn "ro.build.fingerprint"
    sleep 5
    expect -c"
		    set timeout -1
		    spawn bash ${GTS_TOOL_PATH}/tools/xts-tradefed run xts -s $1 --plan XTS
		    expect {
		        "*generated*" { send exit\r\n; send \003 ; interact }
		        eof { exit }
		    }
		    exit
		    "
}


function checktime(){
  time=$(echo $3|awk -F: '{print $1$2}') 
  nowtime=$(date |awk '{ print $4 }'|awk -F: '{print $1$2}')
  echo $nowtime
  if [[ "$time" == "$nowtime" ]];then
    echo "start camera phone"
    start_camera_vedio $2
    sleep 30 
    echo "====begin run gts now!!===="
    run_gts $1
    adb -s $2 shell input tap 290 730 #end video
    sleep 60
    adb -s $2 reboot
    echo "====end run gts now!!==="
    break
  else
    echo "wait to run gts"
    sleep 20
  fi
}

function main(){
    check_adb_devices
    while(true)
    do
        checktime $1 $2 $3
    done
}


main $1 $2 $3

