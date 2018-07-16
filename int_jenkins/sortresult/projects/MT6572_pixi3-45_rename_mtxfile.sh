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
if [[ ${lastname} == "TYC0FH121660RA" ]]; then
	ln -s ${i} MT6572.TYD0FH221641RA.mtx
	ln -s ${i} MT6572.TYC0FH121638RA.mtx
fi
done

all=`ls ${dir_name}`
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
name1="6DU"
name2="6DV"
name3="6DW"
name4="6DX"
name5="6DY"
name6="6DZ"
name7="6DT"
#name8="6DV"
#name9="6DW"
#name10="6DZ" 

if echo ${version} | grep ${name1}; then
	project_name='4027X'
	echo ${project_name}
elif echo ${version} | grep ${name2}; then
	project_name='4027D'
	echo ${project_name}
elif echo ${version} | grep ${name3}; then
	project_name='4027A'
	echo ${project_name}
elif echo ${version} | grep ${name4}; then
	project_name='4028A'
	echo ${project_name}
elif echo ${version} | grep ${name5}; then
	project_name='4028E-4028J'
	echo ${project_name}
elif echo ${version} | grep ${name6}; then
	project_name='4027N'
	echo ${project_name}
elif echo ${version} | grep ${name7}; then
	project_name='4028S'
	echo ${project_name}
#elif echo ${version} | grep ${name8}; then
	#project_name='4013D'
	#echo ${project_name}
#elif echo ${version} | grep ${name9}; then
	#project_name='4013E'
	#echo ${project_name}
#elif echo ${version} | grep ${name10}; then
	#project_name='4013J\4013K'
	#echo ${project_name}
#else project_name="NONAME"

echo ${project_name}
fi

#newproject=`tr'[A-Z]''[a-z]'<<<"${project}"`
if [[ ${lastname} == "TYC0FH121638RA" ]]; then
	name=AMD0000370C1

elif [[ ${lastname} == "H9TP32A4GDDCPR_KGM" ]]; then
	name=AMD0000378C1
	
elif [[ ${lastname} == "TYD0FH221641RA" ]]; then
	name=AMD0000371C1
	
elif [[ ${lastname} == "MT29PZZZ8D4BKFSK_18W_94L" ]]; then
	name=AMD0000352C1
	
elif [[ ${lastname} == "MT29PZZZ4D4BKESK_18W_94H" ]]; then
	name=AMD0000341C1

elif [[ ${lastname} == "KMN5X000ZM_B209" ]]; then
	name=NID

elif [[ ${lastname} == "TYC0FH121660RA" ]]; then
	name=NID
	
else name=000000
fi

echo ${name}
rename=${project}_${project_name}_${band}_${version}_${sim}_${name}_${lastname}.mtx
if [[ ${rename} =~ "TYC0FH121638RA" ]]; then
	ra=${rename}
elif [[ ${rename} =~ "TYD0FH221641RA" ]]; then
	raTwo=${rename}
fi
mv ${i} ${rename}	
done

all=`ls ${dir_name}`
cd ${dir_name}
for i in $all
do
if [[ ${i} =~ "TYC0FH121660RA" ]]; then
	rm -rf ${ra}
	rm -rf ${raTwo}
	echo ${ra}
	echo "test"
	echo ${raTwo} 
	ln -s ${i} ${ra}
	ln -s ${i} ${raTwo} 
fi
done



