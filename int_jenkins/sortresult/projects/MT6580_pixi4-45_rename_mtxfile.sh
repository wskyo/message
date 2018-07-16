#!/bin/bash
#/local/build/pixi4-35_3g-lite-release/v9JV1/out/target/product/pixi4_35/MTXGen/output
#/local/build/pixi4-4_3g-release/v3DX0/out/target/product/pixi4_4/MTXGen/output
#bash ./rename_mtxfile.sh pixi4_35 US1 9JV1 1SIM pixi4-35_3g-lite-release
#MT6580.KMFJ20005A_B213.mtx MT6580.TYD0GH121661RA.mtx

project=$1
band=$2
version=$3
sim=$4
JOB_NAME=$5
dir_name="/local/build/${JOB_NAME}/v$version/out/target/product/$project/MTXGen/.\output/"
all=`ls ${dir_name}`
cd ${dir_name}
for i in $all
do
echo "=====>[$i]"
filename=${i%.*}
echo "=====>[$filename]"
lastname=${filename#*.}
#lastname=${i#*.}
echo "=====>[$lastname]"
declare -u project
project=$1
echo ${project}
name1="2CU"
name2="2CV"
name3="2CW"
name4="2CX"
#name5="2CY"
#name6="2CZ"
if echo ${version} | grep ${name1}; then
	project_name='4041X'
	echo ${project_name}
elif echo ${version} | grep ${name2}; then
	project_name='4041D'
	echo ${project_name}
elif echo ${version} | grep ${name3}; then
	project_name='4041G'
	echo ${project_name}
elif echo ${version} | grep ${name4}; then
	project_name='4041E'
	echo ${project_name}
#elif echo ${version} | grep ${name5}; then
	#project_name='5016J'
	#echo ${project_name}
#elif echo ${version} | grep ${name6}; then
	#project_name='5016A'
	#echo ${project_name}
	
else project_name="NONAME"

echo ${project_name}
fi
#newproject=`tr'[A-Z]''[a-z]'<<<"${project}"`
if [[ ${lastname} == "KMFJ20005A_B213" ]]; then
	name=AMD0000396C1

elif [[ ${lastname} == "TYD0GH121661RA" ]]; then
	name=AMD0000406C1

elif [[ ${lastname} == "MT29TZZZ8D4BKFRL_125W_94K" ]]; then 
	name=AMD0000402C1
	
elif [[ ${lastname} == "MT29TZZZ4D4BKERL_125W_94M" ]]; then 
	name=AMD0000410C1
	
elif [[ ${lastname} == "KMFN10012M_B214" ]]; then 
	name=AMD0000415C1
	
elif [[ ${lastname} == "TYC0FH121642RA" ]]; then 
	name=AMD0000375C1

elif [[ ${lastname} == "H9TQ64A8GTMCUR_KUM" ]]; then 
	name=AMD0000388C1

else name=000000

fi
rename=${project}_${project_name}_${band}_${version}_${sim}_${name}_${lastname}.mtx
mv ${i} ${rename}
done



