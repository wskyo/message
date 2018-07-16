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

name1="BLU"
name2="BLV"
name3="BLW"
name4="BLX"
name5="BLY"
name6="BLZ"

if echo ${version} | grep ${name1}; then
	project_name='4017X'
	echo ${project_name}
elif echo ${version} | grep ${name2}; then
	project_name='4017D'
	echo ${project_name}
elif echo ${version} | grep ${name3}; then
	project_name='4017A'
	echo ${project_name}
elif echo ${version} | grep ${name4}; then
	project_name='4017F'
	echo ${project_name}
elif echo ${version} | grep ${name5}; then
	project_name='4017E'
	echo ${project_name}
elif echo ${version} | grep ${name6}; then
	project_name='4017S'
	echo ${project_name}
	
else project_name="NONAME"

echo ${project_name}
fi

#newproject=`tr'[A-Z]''[a-z]'<<<"${project}"`
if [[ ${lastname} == "04EMCP04_NL2AS100" ]]; then
        name=806710000161

elif [[ ${lastname} == "KMN5X000ZM_B209" ]]; then
	name=AMD0000414C1

elif [[ ${lastname} == "TYC0FH121638RA" ]]; then
	name=806710000201

elif [[ ${lastname} == "KMNJ2000ZM_B207" ]]; then
	name=806700000361

elif [[ ${lastname} == "H9TP32A4GDDCPR_KGM" ]]; then 
	name=AMD0000378C1

else name=000000

fi

rename=${project}_${project_name}_${band}_${version}_${sim}_${name}_${lastname}.mtx
mv ${i} ${rename}
done



