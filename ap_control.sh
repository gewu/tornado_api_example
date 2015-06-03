#!/bin/bash

PROGRAM_NAME="iu_api"

if [ $# -lt 1 ]
then
    echo "Usage - $0 debug|start|stop"
    echo "    Start or Stop $PROGRAM_NAME."
    exit 1
fi

ProgramStart () {
    nohup python core/$PROGRAM_NAME.py > /dev/null 2>./log/$PROGRAM_NAME.err &
    echo $! > $PROGRAM_NAME.pid
}

ProgramDebug () {
    nohup python core/$PROGRAM_NAME.py -D > /dev/null 2>./log/$PROGRAM_NAME.err &
    echo $! > $PROGRAM_NAME.pid
}

ProgramStop () {
    if [ -e $PROGRAM_NAME.pid ]; then
        prog_pid=`cat $PROGRAM_NAME.pid`
        echo "kill -9 $prog_pid"
        kill -9 $prog_pid
    else
        echo "$PROGRAM_NAME.pid does not exist. Try ps -ef."
        echo `ps -ef | grep "$PROGRAM_NAME" | grep -v "grep"`
    fi;
}

if [ "$1" = "start" ]; then
    ProgramStop
    ProgramStart
elif [ "$1" = "debug" ]; then
    ProgramDebug
elif [ "$1" = "stop" ]; then
    ProgramStop
fi
