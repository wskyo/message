#!/bin/sh

if [ -z "$1" ]; then
	echo "Please give the key"
	exit 1
fi
if [ -z "$2" ]; then
	echo "Please give the platform name"
	exit 1
fi

if [ -z "$3" ]; then
	echo "Please give the directory name"
	exit 1
fi
cd ../../
echo "source envsetup"
source build/envsetup.sh
cd -
processApk() {
    if [ -f ../../out/target/product/$4/custpack/$1 ]
    then
	touch ../../out/target/product/$4/custpack/$1.signed
	chmod 777 ../../out/target/product/$4/custpack/$1.signed
	./signapk.sh $1 $2 $3 $4

	touch ../../out/target/product/$4/custpack/$1.signed_aligned
	chmod 777 ../../out/target/product/$4/custpack/$1.signed_aligned
	../../out/host/linux-x86/bin/zipalign -f 4 ../../out/target/product/$4/custpack/$1.signed ../../out/target/product/$4/custpack/$1.signed_aligned

	mv ../../out/target/product/$4/custpack/$1.signed_aligned ../../out/target/product/$4/custpack/$1
	
	rm ../../out/target/product/$4/custpack/$1.signed
    else
        echo "out/target/product/$4/custpack/$1 not found"
    fi
}
echo "$3/perso/ac/releasesign.sh"
source $3/perso/ac/releasesign.sh

echo "start search apk"
for apkfile in ${extra_platform_apkfiles[*]}
do
processApk $apkfile platform $1 $2
done

GenricMkfile=$(find ../../*_wimdata_ng/wprocedures/plf-base/plf/ -name Android.mk)
GenricApk=$(grep "INDEPENDENT_APP_OVERLAY_MODULE" $GenricMkfile|grep -v ^#|grep -v "#"|awk -F ":=" '{print $2}' |sed 's/^ *\| *$//g')
GenricCertificate=$(grep "OVERLAY_CERTIFICATE" $GenricMkfile|grep -v ^#|grep -v "#"|awk -F ":= " '{print $2}'|sed 's/^ *\| *$//g')
echo $GenricApk
echo $GenricCertificate

for apk in $GenricApk
do
flag_string=''
common_apk_cer=''
line_infor1=0
echo "apk is $apk"
while read line
do
line_infor1=`expr ${line_infor1} + 1`
#echo "line_infor1 is $line_infor1"
#echo "GenricMkfile is $GenricMkfile"
if [[ $line == *$apk* ]];then
flag_string='ok'
echo "flag_string is $flag_string"
echo "00 line_infor1 is $line_infor1"
fi
if [[ -n $flag_string ]] && [[ $line == *OVERLAY_CERTIFICATE* ]];then
common_apk_cer=${line#*=}
echo "common_apk_cer is $common_apk_cer"
echo "11 line_infor1 is $line_infor1"
fi
if [[ -n $flag_string ]] && [[ $line == *###* ]];then
echo "22 line_infor1 is $line_infor1"
break
fi
done < $GenricMkfile
if [ -z $common_apk_cer ];then
processApk "JRD_custres/overlay/$apk-overlay.apk" platform $1 $2
echo "11 processApk "JRD_custres/overlay/$apk-overlay.apk" platform $1 $2"
else
processApk "JRD_custres/overlay/$apk-overlay.apk" $common_apk_cer $1 $2
echo "22 processApk "JRD_custres/overlay/$apk-overlay.apk" $common_apk_cer $1 $2"
fi
done

# find all of the Android.mk that defined "LOCAL_MODULE_PATH" in packages/
if [ -d ../../packages ];then
MKFILES=$(find ../../packages -name Android.mk |xargs grep "LOCAL_MODULE_PATH" | grep -i CUSTPACK |grep -v ^#|grep -v "#"| awk -F ":" '{print $1}')
# grep the information in the files
for MKFILE in $MKFILES
do
MODULE_PATH=$(grep "LOCAL_MODULE_PATH" $MKFILE |grep -v ^#|grep -v "#"|head -1|awk -F "app" '{print $2}' |sed 's/^ *\| *$//g')
PACKAGE_NAME=$(grep "LOCAL_PACKAGE_NAME" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}'|sed 's/^ *\| *$//g')
CERTIFICATE=$(grep "LOCAL_CERTIFICATE" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}')
if [ -z "$CERTIFICATE" ]; then
CERTIFICATE="releasekey"
fi
if [ -n "$PACKAGE_NAME" ]; then
PACKAGE_NAME=` echo $PACKAGE_NAME | tr -d ' ' `
fi
if [ -n "$MODULE_PATH" ]; then
MODULE_PATH=` echo $MODULE_PATH | tr -d ' ' `
fi
processApk "app$MODULE_PATH/$PACKAGE_NAME/$PACKAGE_NAME.apk" $CERTIFICATE $1 $2
done
fi

if [ -d ../../packages ];then
MKFILES=$(find ../../packages -name Android.mk |xargs grep "LOCAL_PACKAGE_NAME" | grep -i := |grep -v ^#|grep -v "#"| awk -F ":" '{print $1}')
# grep the information in the files
for MKFILE in $MKFILES
do
PACKAGE_NAME=$(grep "LOCAL_PACKAGE_NAME" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}'|sed 's/^ *\| *$//g')
CERTIFICATE=$(grep "LOCAL_CERTIFICATE" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}')
if [ -z "$CERTIFICATE" ]; then
CERTIFICATE="releasekey"
fi
if [ -n "$PACKAGE_NAME" ]; then
PACKAGE_NAME=` echo $PACKAGE_NAME | tr -d ' ' `
fi
processApk "JRD_custres/overlay/$PACKAGE_NAME-overlay.apk" $CERTIFICATE $1 $2
done
fi

# find all of the Android.mk that defined "LOCAL_MODULE_PATH" in packages/
# Add by zxliu for apk under mediatek
if [ -d ../../mediatek/source/packages ];then
MKFILES=$(find ../../mediatek/source/packages -name Android.mk |xargs grep "LOCAL_MODULE_PATH" | grep -i CUSTPACK |grep -v ^#|grep -v "#"| awk -F ":" '{print $1}')
# grep the information in the files
for MKFILE in $MKFILES
do
MODULE_PATH=$(grep "LOCAL_MODULE_PATH" $MKFILE |grep -v ^#|grep -v "#"|head -1|awk -F "app" '{print $2}' |sed 's/^ *\| *$//g')
PACKAGE_NAME=$(grep "LOCAL_PACKAGE_NAME" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}'|sed 's/^ *\| *$//g')
CERTIFICATE=$(grep "LOCAL_CERTIFICATE" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}')
if [ -z "$CERTIFICATE" ]; then
CERTIFICATE="releasekey"
fi
if [ -n "$PACKAGE_NAME" ]; then
PACKAGE_NAME=` echo $PACKAGE_NAME | tr -d ' ' `
fi
if [ -n "$MODULE_PATH" ]; then
MODULE_PATH=` echo $MODULE_PATH | tr -d ' ' `
fi
processApk "app$MODULE_PATH/$PACKAGE_NAME/$PACKAGE_NAME.apk" $CERTIFICATE $1 $2
done
fi

# find all of the Android.mk that defined "LOCAL_MODULE_PATH" in packages/
# Add by zxliu for apk under mediatek
if [ -d ../../mediatek/packages ];then
MKFILES=$(find ../../mediatek/packages -name Android.mk |xargs grep "LOCAL_MODULE_PATH" | grep -i CUSTPACK |grep -v ^#|grep -v "#"|  awk -F ":" '{print $1}')
# grep the information in the files
for MKFILE in $MKFILES
do
MODULE_PATH=$(grep "LOCAL_MODULE_PATH" $MKFILE |grep -v ^#|grep -v "#"|head -1|awk -F "app" '{print $2}' |sed 's/^ *\| *$//g')
PACKAGE_NAME=$(grep "LOCAL_PACKAGE_NAME" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}'|sed 's/^ *\| *$//g')
CERTIFICATE=$(grep "LOCAL_CERTIFICATE" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}')
if [ -z "$CERTIFICATE" ]; then
CERTIFICATE="releasekey"
fi
if [ -n "$PACKAGE_NAME" ]; then
PACKAGE_NAME=` echo $PACKAGE_NAME | tr -d ' ' `
fi
if [ -n "$MODULE_PATH" ]; then
MODULE_PATH=` echo $MODULE_PATH | tr -d ' ' `
fi
processApk "app$MODULE_PATH/$PACKAGE_NAME/$PACKAGE_NAME.apk" $CERTIFICATE $1 $2
done
fi


# find all of the Android.mk that defined "LOCAL_MODULE_PATH" in packages/
# Add by zxliu for apk under mediatek
if [ -d ../../mediatek/frameworks ];then
MKFILES=$(find ../../mediatek/frameworks -name Android.mk |xargs grep "LOCAL_MODULE_PATH" | grep -i CUSTPACK |grep -v ^#|grep -v "#"|  awk -F ":" '{print $1}')
# grep the information in the files
for MKFILE in $MKFILES
do
MODULE_PATH=$(grep "LOCAL_MODULE_PATH" $MKFILE |grep -v ^#|grep -v "#"|head -1|awk -F "app" '{print $2}' |sed 's/^ *\| *$//g')
PACKAGE_NAME=$(grep "LOCAL_PACKAGE_NAME" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}'|sed 's/^ *\| *$//g')
CERTIFICATE=$(grep "LOCAL_CERTIFICATE" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}')
if [ -z "$CERTIFICATE" ]; then
CERTIFICATE="releasekey"
fi
if [ -n "$PACKAGE_NAME" ]; then
PACKAGE_NAME=` echo $PACKAGE_NAME | tr -d ' ' `
fi
if [ -n "$MODULE_PATH" ]; then
MODULE_PATH=` echo $MODULE_PATH | tr -d ' ' `
fi
processApk "app$MODULE_PATH/$PACKAGE_NAME/$PACKAGE_NAME.apk" $CERTIFICATE $1 $2
done
fi

# find all of the Android.mk that defined "LOCAL_MODULE_PATH" in packages/
# Add by zxliu for apk under mediatek
if [ -d ../../vendor/jrdcom ];then
MKFILES=$(find ../../vendor/jrdcom -name Android.mk |xargs grep "LOCAL_MODULE_PATH" | grep -i CUSTPACK |grep -v ^#|grep -v "#"| awk -F ":" '{print $1}')
# grep the information in the files 
for MKFILE in $MKFILES
do
MODULE_PATH=$(grep "LOCAL_MODULE_PATH" $MKFILE |grep -v ^#|grep -v "#"|head -1|awk -F "app" '{print $2}' |sed 's/^ *\| *$//g')
PACKAGE_NAME=$(grep "LOCAL_PACKAGE_NAME" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}'|sed 's/^ *\| *$//g')
CERTIFICATE=$(grep "LOCAL_CERTIFICATE" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}')
if [ -z "$CERTIFICATE" ]; then
CERTIFICATE="releasekey"
fi
if [ -n "$PACKAGE_NAME" ]; then
PACKAGE_NAME=` echo $PACKAGE_NAME | tr -d ' ' `
fi
if [ -n "$MODULE_PATH" ]; then
MODULE_PATH=` echo $MODULE_PATH | tr -d ' ' `
fi
processApk "app$MODULE_PATH/$PACKAGE_NAME/$PACKAGE_NAME.apk" $CERTIFICATE $1 $2
done
fi

if [ -d ../../vendor/jrdcom ];then
MKFILES=$(find ../../vendor/jrdcom -name Android.mk |xargs grep "LOCAL_PACKAGE_NAME" | grep -i := |grep -v ^#|grep -v "#"| awk -F ":" '{print $1}')
# grep the information in the files
for MKFILE in $MKFILES
do
PACKAGE_NAME=$(grep "LOCAL_PACKAGE_NAME" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}'|sed 's/^ *\| *$//g')
CERTIFICATE=$(grep "LOCAL_CERTIFICATE" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}')
if [ -z "$CERTIFICATE" ]; then
CERTIFICATE="releasekey"
fi
if [ -n "$PACKAGE_NAME" ]; then
PACKAGE_NAME=` echo $PACKAGE_NAME | tr -d ' ' `
fi
processApk "JRD_custres/overlay/$PACKAGE_NAME-overlay.apk" $CERTIFICATE $1 $2
done
fi

# find all of the Android.mk that defined "LOCAL_MODULE_PATH" in packages/
# Add by zxliu for apk under mediatek
if [ -d ../../vendor/mediatek ];then
MKFILES=$(find ../../vendor/mediatek -name Android.mk |xargs grep "LOCAL_MODULE_PATH" | grep -i CUSTPACK |grep -v ^#|grep -v "#"| awk -F ":" '{print $1}')
# grep the information in the files 
for MKFILE in $MKFILES
do
MODULE_PATH=$(grep "LOCAL_MODULE_PATH" $MKFILE |grep -v ^#|grep -v "#"|head -1|awk -F "app" '{print $2}' |sed 's/^ *\| *$//g')
PACKAGE_NAME=$(grep "LOCAL_PACKAGE_NAME" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}'|sed 's/^ *\| *$//g')
CERTIFICATE=$(grep "LOCAL_CERTIFICATE" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}')
if [ -z "$CERTIFICATE" ]; then
CERTIFICATE="releasekey"
fi
if [ -n "$PACKAGE_NAME" ]; then
PACKAGE_NAME=` echo $PACKAGE_NAME | tr -d ' ' `
fi
if [ -n "$MODULE_PATH" ]; then
MODULE_PATH=` echo $MODULE_PATH | tr -d ' ' `
fi
processApk "app$MODULE_PATH/$PACKAGE_NAME/$PACKAGE_NAME.apk" $CERTIFICATE $1 $2
done
fi

if [ -d ../../vendor/mediatek ];then
MKFILES=$(find ../../vendor/mediatek -name Android.mk |xargs grep "LOCAL_PACKAGE_NAME" | grep -i := |grep -v ^#|grep -v "#"| awk -F ":" '{print $1}')
# grep the information in the files
for MKFILE in $MKFILES
do
PACKAGE_NAME=$(grep "LOCAL_PACKAGE_NAME" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}'|sed 's/^ *\| *$//g')
CERTIFICATE=$(grep "LOCAL_CERTIFICATE" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}')
if [ -z "$CERTIFICATE" ]; then
CERTIFICATE="releasekey"
fi
if [ -n "$PACKAGE_NAME" ]; then
PACKAGE_NAME=` echo $PACKAGE_NAME | tr -d ' ' `
fi
processApk "JRD_custres/overlay/$PACKAGE_NAME-overlay.apk" $CERTIFICATE $1 $2
done
fi

if [ -d ../../frameworks ];then
MKFILES=$(find ../../frameworks -name Android.mk |xargs grep "LOCAL_PACKAGE_NAME" | grep -i := |grep -v ^#|grep -v "#"| awk -F ":" '{print $1}')
# grep the information in the files
for MKFILE in $MKFILES
do
PACKAGE_NAME=$(grep "LOCAL_PACKAGE_NAME" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}'|sed 's/^ *\| *$//g')
CERTIFICATE=$(grep "LOCAL_CERTIFICATE" $MKFILE|grep -v ^#|grep -v "#"|head -1|awk -F ":= " '{print $2}')
if [ -z "$CERTIFICATE" ]; then
CERTIFICATE="releasekey"
fi
if [ -n "$PACKAGE_NAME" ]; then
PACKAGE_NAME=` echo $PACKAGE_NAME | tr -d ' ' `
fi
processApk "JRD_custres/overlay/$PACKAGE_NAME-overlay.apk" $CERTIFICATE $1 $2
done
fi
