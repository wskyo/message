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

rm -rf out/dist/target_files_apks
mkdir out/dist/target_files_apks
cd out/dist/target_files_apks
unzip ../california-target_*.zip
tempdir=`mktemp -t -d signedinfoXXXXXX`
echo "tempdir:$tempdir"
/local/tools_int/misc/misc_signature_check.py CUSTPACK $tempdir

signed_apk="$tempdir/signedinfo.txt"
for apkname in $(cat $signed_apk)
do
    CustpackSignedApkListCmd="$CustpackSignedApkListCmd -e `basename $apkname`= "
done

/local/tools_int/misc/misc_signature_check.py SYSTEM $tempdir

signed_apk="$tempdir/signedinfo.txt"
for apkname in $(cat $signed_apk)
do
    CustpackSignedApkListCmd="$CustpackSignedApkListCmd -e `basename $apkname`= "
done

echo "CustpackSignedApk list : $CustpackSignedApkListCmd "
rm -rf $tempdir

cd -
build/tools/releasetools/sign_target_files_apks \
  -o \
  -d $path_to_key \
  -e JrdUser2Root.apk=build/target/product/security/platform \
$CustpackSignedApkListCmd \
$input_package $output_package

echo "signed package written in $output_package"
