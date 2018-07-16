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
name1="2BZ"
name2="2BY"
name3="1AW"
name4="1AX"
name5="1AY"
name6="1AZ"
if echo ${version} | grep ${name1}; then
	project_name='5025E'
	echo ${project_name}
elif echo ${version} | grep ${name2}; then
	project_name='5025G'
	echo ${project_name}
elif echo ${version} | grep ${name3}; then
	project_name='5015A'
	echo ${project_name}
elif echo ${version} | grep ${name4}; then
	project_name='5015E'
	echo ${project_name}
elif echo ${version} | grep ${name5}; then
	project_name='5016J'
	echo ${project_name}
elif echo ${version} | grep ${name6}; then
	project_name='5016A'
	echo ${project_name}
	
else project_name="NONAME"

echo ${project_name}
fi
#newproject=`tr'[A-Z]''[a-z]'<<<"${project}"`
if [[ ${lastname} == "TYD0GH121661RA" ]]; then
	name=AMD0000406C1

elif [[ ${lastname} == "MT29TZZZ8D4BKFRL_125W_94K" ]]; then 
	name=AMD0000328C1
	
elif [[ ${lastname} == "KMQ72000SM-B316" ]]; then 
	name=AMD0000386C1
	
else name=000000

fi
rename=${project}_${project_name}_${band}_${version}_${sim}_${name}_${lastname}.mtx
mv ${i} ${rename}
done



