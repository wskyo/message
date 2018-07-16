#!/bin/bash

################################################
## user to automent sign build

################################################
#set -x
set -e


E_BADARGS=65

## no input arg
if [ ! -n "$1" ]
then
   echo "Usage: `basename $0` argument1 etc."
   exit $E_BADARGS
fi 


###compare python path
if [ -x /opt/python-2.7.1/bin/python ]; then
	PYTHON=/opt/python-2.7.1/bin/python
else
	PYTHON=/usr/bin/python
fi

SIGNPW=""

## if add other project pls add code like this
if [ "$1" == "twin" ]
then
    SIGNPW="twin1401033162"

#elif [ "$1" == "pixi4-4-tf" ]
#then
#    SIGNPW="TF_0222"
elif [ "$1" == "pixi3-4" ]
then
    SIGNPW="TCL_1010"
else
    SIGNPW="TCL_1010"

fi

###start run signe module
if [ $2 ]; then
    exec $PYTHON signStart.py $SIGNPW $2
else
    exec $PYTHON signStart.py $SIGNPW
fi
