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

name1="5EU"
name2="5EV"
name3="5EW"
name4="5EX"
name5="5EY"

if echo ${version} | grep ${name1}; then
	project_name='5010X'
	echo ${project_name}
elif echo ${version} | grep ${name2}; then
	project_name='5010D'
	echo ${project_name}
elif echo ${version} | grep ${name3}; then
	project_name='5010G'
	echo ${project_name}
elif echo ${version} | grep ${name4}; then
	project_name='5010E'
	echo ${project_name}
elif echo ${version} | grep ${name5}; then
	project_name='5010S' 
	echo ${project_name}	
else project_name="NONAME"

echo ${project_name}
fi
namecopy=0
#newproject=`tr'[A-Z]''[a-z]'<<<"${project}"`
if [[ ${lastname} == "KMF720012M_B214" ]]; then
	name=806710000271

elif [[ ${lastname} == "08EMCP08_EL3CV100" ]]; then 
	name=806700000241

elif [[ ${lastname} == "KHN6405FS-HKc1" ]]; then 
	name=NID

elif [[ ${lastname} == "H9TP64A8JDMCPR_KGM" ]]; then 
	name=NID

elif [[ ${lastname} == "KMQ72000SM-B316" ]]; then 
	name=NID

elif [[ ${lastname} == "08EMCP08_EL3BT227" ]]; then 
	name=NID

elif [[ ${lastname} == "KMQN1000SM_B316" ]]; then
        name=AMD0000431C1
	lastname=SP35BMCB7-Sxxxx

elif [[ ${lastname} == "GPBD81S42MFLB_T3E" ]]; then
        name=806700000331

elif [[ ${lastname} == "H9TQ64A8GTMCUR_KUM" ]]; then
        name=806700000121
        namecopy=AMD0000388C1

elif [[ ${lastname} == "KMFNX0012M_B214" ]]; then
        name=806700000431
        namecopy=AMD0000538C1

else name=000000

fi
rename=${project}_${project_name}_${band}_${version}_${sim}_${name}_${lastname}.mtx
mv ${i} ${rename}
if [[ ${namecopy} != "0" ]]; then
  cp ${rename} ${project}_${project_name}_${band}_${version}_${sim}_${namecopy}_${lastname}.mtx
fi

done



