#!/bin/bash

pythoncmd=$1
script=$2
mode=$3

pwd
CMD_TO_RUN="$pythoncmd $script runserver"

FILE="pid.run"

if [ -f $FILE ]
then
    while read line;
    do
        echo "Killing process " $line
        kill $line
    done
    echo "Deleting PID file"
    rm -f $FILE
fi  < $FILE

if [ ! -z "$mode" ]
then
	$CMD_TO_RUN 2>&1 > run.log &
	echo "PID number: " $!
	echo $! >> ${FILE}
	sleep 2
	cat run.log
fi

exit 0
