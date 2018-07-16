checkDir() {
    if [ ! -d $1 ]; then
        echo "$2"
        exit
    fi;
}


checkFile() {
    if [ ! -f "$1" ]; then
        echo "Unable to locate $1."
        exit
    fi;
}

CTS_ROOT=./../..
RUNCTS=${CTS_ROOT}/tools/cts-tradefed
PARSECTS_ROOT=$CTS_ROOT/tools/athrun
DEVICESID=$1
CHOOSERESULT=$2
checkDir ${PARSECTS_ROOT} "Error: Cannot locate parse file in \"${PARSECTS_ROOT}\". Please check your configuration in $0"
checkDir ${CTS_ROOT} "Error: Cannot locate startcts in \"${CTS_ROOT}\". Please check your configuration in $0"
checkFile ${RUNCTS}

_xarray=(a b c)
if [ -z "${_xarray[${#_xarray[@]}]}" ]
then
    _arrayoffset=1
else
    _arrayoffset=0
fi

TESTRESULT=
function chooseresult()
{
    # Find the makefiles that must exist for a product.
    # Send stderr to /dev/null in case partner isn't present.
    local -a choices
    choices=(`/bin/ls ${CTS_ROOT}/repository/results/*/testResult.xml`)

    local choice
    local -a prodlist

    for choice in ${choices[@]}
    do
        # The product name is the name of the directory containing
        # the makefile we found, above.
        prodlist=(${prodlist[@]} `dirname ${choice} | xargs basename`)
    done

    local index=1
    local p
    local default_value=0
    echo "Session choices are:"

    for p in ${prodlist[@]}
    do
        echo "     $index. $p"
        let "index = $index + 1"
        if [ "$p" = "$CHOOSERESULT" ] ; then
           let "default_value = $index - 1"
        fi
    done

    if ((index == 1)) || ((default_value == 0)) ; then
       echo "No session exists!";
       exit
    fi

    local ANSWER

    while [ -z "$TESTRESULT" ]
    do
        echo -n "Which session would you like? [$default_value] "

        #if [ -z "$1" ] ; then
            #read ANSWER
        #else
            #echo $1
            #ANSWER=$1
        #fi
        if [ -n "$1" ] ; then
            ANSWER=$1
        fi

        if [ -z "$ANSWER" ] ; then
           ANSWER=$default_value
        fi

        if (echo -n $ANSWER | grep -q -e "^[0-9][0-9]*$") ; then
            local poo=`echo -n $ANSWER`
            if [ $poo -le ${#prodlist[@]} ] ; then
                TESTRESULT=${CTS_ROOT}/repository/results/${prodlist[$(($ANSWER-$_arrayoffset))]}/testResult.xml

                if (($index > 2)) ; then
                    let "SESSION = $ANSWER - 1"
                fi

            else
                echo "** Bad session selection: $ANSWER"
            fi
        else
            echo "** Bad session selection: $ANSWER"
       	fi

    done

}
chooseresult
checkFile ${TESTRESULT}
MODIFYTYPE=

function choosetype()
{
    echo "Choose type of cases:"
    echo "    1.Fail"
    echo "    2.Timeout"
    echo "    3.Fail & Timeout"
    echo "Note: All notExcute cases will also be run."
    local default_value=3
    local ANSWER

    while [ -z "$MODIFYTYPE" ]
    do
        echo -n "Which type would you like? [$default_value] "

        if [ -z "$1" ] ; then
            read ANSWER
        else
            echo $1
            ANSWER=$1
        fi

        if [ -z "$ANSWER" ] ; then
           ANSWER=$default_value
        fi

        case $ANSWER in
            1)
                MODIFYTYPE="failed"
                ;;
            2)
                MODIFYTYPE="timeout"
                ;;
            3)
                MODIFYTYPE="all"
                ;;
            *)
                echo
                echo "I didn't understand your response.  Please try again."
                echo
                ;;
            esac

        if [ -n "$1" ] ; then
            break
        fi
    done

}

choosetype 3

RUNMODE=

function choosemode()
{
    echo "Choose mode of cases:"
    echo "    1.Quick"
    local default_value=1
    local ANSWER

    while [ -z "$RUNMODE" ]
    do
        echo -n "Which mode would you like? [$default_value] "
        if [ -z "$1" ] ; then
            read ANSWER
        else
            echo $1
            ANSWER=$1
        fi
        if [ -z "$ANSWER" ] ; then
           ANSWER=$default_value
        fi

        case $ANSWER in
            1)
                RUNMODE="quick"
                ;;
            *)
                echo
                echo "I didn't understand your response.  Please try again."
                echo
                ;;
            esac

        if [ -n "$1" ] ; then
            break
        fi
    done

}

choosemode 1

if [ "$RUNMODE" = "quick" ]; then
    PARSECTSXML=${PARSECTS_ROOT}/modifyresult.py
    checkFile ${PARSECTSXML}
    $PARSECTSXML $TESTRESULT $MODIFYTYPE
    echo "RUMMODE = quick"
fi

if [ -n "$SESSION" ]; then
    ./runcts.py ${RUNCTS} ${SESSION} ${DEVICESID}
else
    ./runcts.py ${RUNCTS} ${DEVICESID}
fi
