#!/bin/bash
#run gts at time
if [ -z "$1" ]; then
	echo "Please run on time,like 21:00"
	exit 1
fi

filename=./device.txt
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
    #set -x
    adb -s "$1" shell getprop | grep -rn "ro.build.fingerprint"
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


function checktorun(){
  time=$(echo $1|awk -F: '{print $1$2}') 
  nowtime=$(date |awk '{ print $4 }'|awk -F: '{print $1$2}')
  echo $nowtime
  if [[ "$time" == "$nowtime" ]];then
    i=1
    for deviceid in ${devices[@]}
    do
	if [ -n "$2" ]; then
		echo "start camera phone"
		start_camera_vedio $2
		sleep 30 

	fi
        deviceid=$(echo $deviceid|sed 's/"//g')
        echo $deviceid
        echo "====begin run $i gts now!!===="
        run_gts $deviceid
        if [ -n "$2" ]; then
            adb -s $2 shell input tap 290 730 #end video
            echo "wait to save video"
            sleep 60
            adb -s $2 reboot
        fi
        echo "====end run $i gts!!==="
        sleep 90
	i=`expr $i + 1`
    done
    break
  else
    echo "wait to run gts"
    sleep 20
  fi
}


function main(){
    #check_adb_devices
    i=0
    while read deviceid
    do  
	deviceid=$(echo $deviceid|sed 's/"//g')
	echo $deviceid
	devices[$i]=$deviceid
	i=`expr $i + 1`
    done <$filename
    while(true)
    do
        checktorun $1 $2
    done
    echo "====finish run all gts test!!==="
}


main $1 $2 $3

