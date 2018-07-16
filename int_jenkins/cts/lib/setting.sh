set -x
shopt -s expand_aliases

if [ $# -lt 5 ];then
  echo "Usage: Need 5 Params!!!! "
  exit
fi
CTS_PATH=$CTS_PACKAGE_PATH
CTS_TOOL_PATH="${CTS_PATH}/android-cts"
CTSAPK_PATH="${CTS_TOOL_PATH}/repository/testcases"
#CONNECT_WIFI_APK_PATH="${SCRIPT_DIR}/misc"
CTS_MEDIA_PATH=$CTS_MEDIA_PATH


VERSION="$2"
PERSO="$3"
PROJECT="$1"
PPLATFORM="$4"
DEVICESID="$5"


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

#./setting.sh pixi3-4 5B1N-1 5B1N
#./setting.sh pixi3-45 6D18 6D18
function auto_setting() 
{
    #check_adb_devices

    adb -s $1 install -r  $CTSAPK_PATH/CtsDeviceAdmin.apk
	
    if [ ${#VERSION} == "4" ] && [ "$PPLATFORM" == "KK" ]; then
        adb -s $1 install -r APK/AutoSettingForCTS_5F_Signed.apk
    elif [ ${#VERSION} == "4" ] && [ "$PPLATFORM" == "androidL" ]; then
        adb -s $1 install -r APK/AutoSettingForCTS_androidL_Signed.apk
    elif [ ${#VERSION} == "4" ] && [ "$PPLATFORM" == "androidM" ]; then
	if [ "$PROJECT" == "pixi4-4-tf" ]; then
	    adb -s $1 install -r APK/AutoSettingForCTS_TF_Signed.apk
	else
            adb -s $1 install -r APK/AutoSettingForCTS_androidM_Signed.apk
	fi
    elif [ ${#VERSION} == "6" ] && [ "$PPLATFORM" == "KK" ]; then
        adb -s $1 install -r APK/AutoSettingForCTS_5F.apk
    elif [ ${#VERSION} == "6" ] && [ "$PPLATFORM" == "androidL" ]; then
        adb -s $1 install -r APK/AutoSettingForCTS_androidL.apk
    elif [ ${#VERSION} == "6" ] && [ "$PPLATFORM" == "androidM" ]; then
	if [ "$PROJECT" == "pixi4-4-tf" ]; then
	    adb -s $1 install -r APK/AutoSettingForCTS_TF.apk
	else
	    adb -s $1 install -r APK/AutoSettingForCTS_androidM.apk
        fi
    else
        adb -s $1 install -r APK/AutoSettingForCTS_5F_Signed.apk
    fi

    sleep 30
    adb -s $1 push APK/CalculatorAutoTest.jar /data/local/tmp
    adb -s $1 shell uiautomator runtest CalculatorAutoTest.jar -c CalTest
   
    #delete sdcard file
    #adb -s $1 shell < command_del 

    #copy media file 
    if [ "$PROJECT" == "pixi4-4_3g" ] && [[ ${VERSION:2:1} =~ [1] ]]; then
	echo "-------copy 1280X720 media file--------"
        #cd $CTS_MEDIA_PATH && bash copy_media.sh 1280x720
        cd $CTS_MEDIA_PATH && bash copy_media.sh all -s $1 
    else
	echo "-------copy all media file--------"
        cd $CTS_MEDIA_PATH && bash copy_media.sh all -s $1 
    fi

    #uninstall AutoSettingForCTS.apk
    adb -s $1 uninstall com.cts.settings 

}

function check_adb_devices()
{
    adbdvices=`adb devices | sed -n 2p`
    if [ "$adbdvices" = "" ];then
        die "NO adb devices"
    fi
    sleep 2
}

function main()
{   
    auto_setting $DEVICESID
}
main $1 $2 $3
