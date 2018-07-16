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


name1="3EV"
name2="3ES"
name3="3ET"

if echo ${version} | grep ${name1}; then
	project_name='4034G'
	echo ${project_name}
elif echo ${version} | grep ${name2}; then
	project_name='4034X'
	echo ${project_name}
elif echo ${version} | grep ${name3}; then
	project_name='4034D'
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

elif [[ ${lastname} == "MT29TZZZ8D5BKFAH_125W_95K" ]]; then 
	name=AMD0000350C1

elif [[ ${lastname} == "04EMCP04_NL3DM627" ]]; then 
	name=AMD0000557C1

elif [[ ${lastname} == "TYD0GH121661RA" ]]; then 
	name=AMD0000406C1

elif [[ ${lastname} == "KMQN1000SM_B316" ]]; then 
	name=AMD0000431C1
	lastname=SP35BMCB7-Sxxxx

elif [[ ${lastname} == "08EMCP04_NL3DT227" ]]; then 
       name=AMD0000594C1
else name=000000

fi
pj_rename='PIXI4_4_C'
rename=${pj_rename}_${project_name}_${band}_${version}_${sim}_${name}_${lastname}.mtx
mv ${i} ${rename}
done



