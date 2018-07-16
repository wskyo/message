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
name1="5BY"
name2="5BT"
name3="5BS"
name4="5BR"
name5="5BP"
name6="5BQ"
name7="5BU"
name8="5BV"
name9="5BW"
name10="5BZ" 

if echo ${version} | grep ${name1}; then
	project_name='4013M-4003M-4003A-4003J'
	echo ${project_name}
elif echo ${version} | grep ${name2}; then
	project_name='4014E'
	echo ${project_name}
elif echo ${version} | grep ${name3}; then
	project_name='4014A'
	echo ${project_name}
elif echo ${version} | grep ${name4}; then
	project_name='4014M'
	echo ${project_name}
elif echo ${version} | grep ${name5}; then
	project_name='4014X'
	echo ${project_name}
elif echo ${version} | grep ${name6}; then
	project_name='4014K'
	echo ${project_name}
elif echo ${version} | grep ${name7}; then
	project_name='4014X-4013X'
	echo ${project_name}
elif echo ${version} | grep ${name8}; then
	project_name='4013D'
	echo ${project_name}
elif echo ${version} | grep ${name9}; then
	project_name='4013E'
	echo ${project_name}
elif echo ${version} | grep ${name10}; then
	project_name='4013J-4013K'
	echo ${project_name}
else project_name="NONAME"

echo ${project_name}
fi

#newproject=`tr'[A-Z]''[a-z]'<<<"${project}"`
if [[ ${lastname} == "KMFJ20005A_B213" ]]; then
	name=AMD0000396C1

elif [[ ${lastname} == "KMF5X0005C_B211" ]]; then
	name=AMD0000334C1

elif [[ ${lastname} == "MT29TZZZ4D4BKERL_125W_94M" ]]; then 
	name=AMD0000410C1

elif [[ ${lastname} == "KMFN10012M_B214" ]]; then 
	name=AMD0000415C1

elif [[ ${lastname} == "TYC0FH121642RA" ]]; then 
	name=NID

else name=000000
fi
echo ${name}
rename=${project}_${project_name}_${band}_${version}_${sim}_${name}_${lastname}.mtx
mv ${i} ${rename}
done



