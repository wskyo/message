#!/bin/sh

if [ $1 == "" ]; then
	echo "Please enter project_name."
	return
fi

PATH=$PATH:$PWD/mediatek/build/tools/
passwd=(beetle1009)
project_name=$1

#modify by jing.shen
#echo "copy SignMartell.py to current work folder ${passwd[0]}"
echo "copy SignMartell.py to current work folder"
cp /local/tools_int/securityteam/$project_name/SignMartell.py .

echo "copy Utils.py to current work folder"
cp /local/tools_int/lib/Utils.py .
 
chmod a+x SignMartell.py

if [ $project_name == "yarisl"   ];then
	./SignMartell.py ${passwd[0]} $2
	#exit $?
fi


