#!/bin/bash
if [[ $# < 1 ]];then
echo "usage : $0 /path/to/package-files.zip  <out.zip>"
exit 0
fi

#parameters-start
input_package=$1

if [[ -n "$2" ]];then
output_package=$2
else
output_package=/tmp/out.zip
fi

path_to_key="build/target/product/security"
#
#list of custpack applications which need signing with 'platform' key
CustPackApkforPlatformKey="\
framework-res.apk \
Plugger.apk \
Provision.apk \
ActivityNetwork.apk \
MobileLog.apk \
SyncMLClient.apk \
JrdShared.apk"

#parameters-end

echo " exclude .apk file found in CUSTPACK :"
echo

#list all the applications in custpack
#CustpackApkList=$(unzip -l $1 | awk ' BEGIN {list="" } /CUSTPACK.*apk/ { res=gensub(/.*CUSTPACK.*\/(.*\.apk)/,"\\1 ","g"); list=res list } END{ print list }') #ubuntu11.10 &12.04 not support this format,modify it the following format
CustpackApkList=$(unzip -l $1 | awk '/CUSTPACK.*\.apk$/ {print $4}'|awk -F \/ '{print $NF}')
 
#build the script parameters for custpack apks
for apkname in $CustpackApkList
do
if [[ -n $(echo $CustPackApkforPlatformKey | grep -i $apkname) ]];then
  CustpackApkListCmd="$CustpackApkListCmd -e $apkname=$path_to_key/platform"
else
  CustpackApkListCmd="$CustpackApkListCmd -e $apkname= "
fi
done


echo "custpack list : $CustpackApkListCmd "

build/tools/releasetools/sign_target_files_apks \
  -o \
  -d $path_to_key \
$CustpackApkListCmd \
-e GoogleCheckin.apk=build/target/product/security/platform \
-e GooglePartnerSetup.apk=build/target/product/security/platform \
-e GoogleSubscribedFeedsProvider.apk=build/target/product/security/platform \
-e NetworkLocation.apk=build/target/product/security/shared \
-e Settings.apk=build/target/product/security/platform \
-e NotePad2.apk=build/target/product/security/platform \
-e AccountAndSyncSettings.apk=build/target/product/security/platform \
-e JrdUser2Root.apk=build/target/product/security/platform \
-e JrdAlcatelHelp.apk=build/target/product/security/platform \
-e JrdTethering.apk=build/target/product/security/platform \
-e SystemUI.apk=build/target/product/security/platform \
-e SettingsProvider.apk=build/target/product/security/platform \
-e EngineerModeSim.apk=build/target/product/security/platform \
-e VpnServices.apk=build/target/product/security/platform \
-e AccountAndSyncSettings.apk=build/target/product/security/platform \
-e MobileLog.apk=build/target/product/security/platform \
-e ActivityNetwork.apk=build/target/product/security/platform \
-e AcwfDialog.apk=build/target/product/security/platform \
-e ModemLog.apk=build/target/product/security/platform \
-e TelephonyProvider.apk=build/target/product/security/platform \
-e ChsHandWritePack.apk=build/target/product/security/platform \
-e CellConnService.apk=build/target/product/security/platform \
-e EngineerMode.apk=build/target/product/security/platform \
-e SystemServiceBackup-unsigned-1.1.0.110.apk=build/target/product/security/platform \
-e Stk1.apk=build/target/product/security/platform \
-e Sprite-Backup-ALCATEL-2.5.6.45.apk=build/target/product/security/platform \
-e Stk2.apk=build/target/product/security/platform \
-e Phone.apk=build/target/product/security/platform \
-e GoogleBackupTransport.apk=build/target/product/security/platform \
-e MediaTekLocationProvider.apk=build/target/product/security/platform \
-e TCLWatchDog.apk=build/target/product/security/platform \
-e MMITestdev.apk=build/target/product/security/platform \
-e WifiP2PWizardy.apk=build/target/product/security/platform \
-e onetouchCloudBackup_20121107_v2.5.6.42_Sprite.apk=build/target/product/security/platform \
-e JrdSetupWizard.apk=build/target/product/security/platform \
-e YGPS.apk=build/target/product/security/platform \
-e DeskClock.apk=build/target/product/security/platform \
-e VpnServices.apk=build/target/product/security/platform \
-e EngineerModeSim.apk=build/target/product/security/platform \
-e StartupWizard_320x480_Alcatel_20110523_A1.02.00_TCT_Plat_signed.apk=build/target/product/security/platform \
-e Swype.apk=build/target/product/security/platform \
-e JrdFotaService.apk=build/target/product/security/platform \
-e JrdApp2SDCard.apk=build/target/product/security/platform \
-e SystemUI.apk=build/target/product/security/platform \
-e Settings.apk=build/target/product/security/platform \
-e JrdPowerSaver.apk=build/target/product/security/platform \
-e JrdSalesTracker.apk=build/target/product/security/platform \
-e NmiAtv.apk=build/target/product/security/platform \
-e StkSelection.apk=build/target/product/security/platform \
-e Stk.apk=build/target/product/security/platform \
-e TouchPal_4.8.5.35857_20121010.apk=build/target/product/security/shared \
-e GoogleCalendarSyncAdapter.apk=build/target/product/security/shared \
-e GoogleContactsSyncAdapter.apk=build/target/product/security/shared \
-e GoogleServicesFramework.apk=build/target/product/security/shared \
-e Facebook_APKInstaller.apk=build/target/product/security/shared \
-e Talk.apk=build/target/product/security/shared \
-e SwiftKey_Flow_Public_Beta-4.0.0.54.apk=build/target/product/security/shared \
-e PinyinIME.apk=build/target/product/security/shared \
-e MtkWeatherProvider.apk=build/target/product/security/shared \
-e DownloadProvider.apk=build/target/product/security/media \
-e DownloadProviderUi.apk=build/target/product/security/media \
-e FMRadio.apk=build/target/product/security/media \
-e Gallery.apk=build/target/product/security/media \
-e DrmProvider.apk=build/target/product/security/media \
-e MusicWidget.apk=build/target/product/security/releasekey \
-e GmailProvider.apk,\
Street.apk,\
EnhancedGoogleSearchProvider.apk,\
MediaUploader.apk,\
TalkProvider.apk,\
YouTube.apk,Talk.apk,\
GoogleSettingsProvider.apk,\
SetupWizard.apk,\
Vending.apk,\
GoogleApps.apk,\
Gmail.apk,\
MarketUpdater.apk,\
HmAgent.apk,\
Maps.apk,\
VoiceSearch.apk= \
$input_package $output_package

echo "signed package written in $output_package"
