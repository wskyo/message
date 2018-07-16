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

name1="3DU"
name2="3DV"
name3="3DW"
name4="3DX"
name5="3DY"
name6="3DZ"
name7="3DP"
name8="3DQ"
name9="3DN"
name10="3DS"
name11="3DT"

if echo ${version} | grep ${name1}; then
	project_name='4034X'
	echo ${project_name}
elif echo ${version} | grep ${name2}; then
	project_name='4034D'
	echo ${project_name}
elif echo ${version} | grep ${name3}; then
	project_name='4034G-4034A'
	echo ${project_name}
elif echo ${version} | grep ${name4}; then
	project_name='4034E'
	echo ${project_name}
elif echo ${version} | grep ${name5}; then
	project_name='4034X'
	echo ${project_name}
elif echo ${version} | grep ${name6}; then
	project_name='4034D'
	echo ${project_name}
elif echo ${version} | grep ${name7}; then
	project_name='4034M'
	echo ${project_name}
elif echo ${version} | grep ${name8}; then
	project_name='4034F-4034N'
	echo ${project_name}
elif echo ${version} | grep ${name9}; then
	project_name='A466T'
	echo ${project_name}
elif echo ${version} | grep ${name10}; then
	project_name='4034G'
	echo ${project_name}
elif echo ${version} | grep ${name11}; then
	project_name='4034F'
	echo ${project_name}
	
else project_name="NONAME"

echo ${project_name}
fi

#newproject=`tr'[A-Z]''[a-z]'<<<"${project}"`
if [[ ${lastname} == "KMFJ20005A_B213" ]]; then
	name=AMD0000396C1

elif [[ ${lastname} == "KMFN10012M_B214" ]]; then
	name=AMD0000415C1

elif [[ ${lastname} == "TYC0FH121642RA" ]]; then
	name=AMD0000375C1

elif [[ ${lastname} == "MT29TZZZ4D4BKERL_125W_94M" ]]; then
	name=AMD0000410C1

elif [[ ${lastname} == "MT29TZZZ8D4BKFRL_125W_94K" ]]; then 
	name=AMD0000402C1

elif [[ ${lastname} == "MT29TZZZ8D5BKFAH_125W_95K" ]]; then 
	name=AMD0000350C1

elif [[ ${lastname} == "04EMCP04_NL3DM627" ]]; then 
	name=AMD0000557C1

elif [[ ${lastname} == "TYD0GH121661RA" ]]; then 
	name=AMD0000406C1

elif [[ ${lastname} == "KMQN1000SM_B316" ]]; then 
	name=AMD0000431C1
	lastname=SP35BMCB7-Sxxxx

elif [[ ${lastname} == "KMFNX0012M_B214" ]]; then 
	name=AMD0000479C1

elif [[ ${lastname} == "H9TQ64A8GTCCUR_KUM" ]]; then 
	name=AMD0000520C1

else name=000000

fi
pj_rename='PIXI4_4'
rename=${pj_rename}_${project_name}_${band}_${version}_${sim}_${name}_${lastname}.mtx
mv ${i} ${rename}
done



