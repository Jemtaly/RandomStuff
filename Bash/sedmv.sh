#!/bin/bash
CMD=$1
shift
for orig in "$@"
do
    dest=`echo $orig | sed "$CMD"`
    if [ "$orig" != "$dest" ]
    then
        mv "$orig" "$dest"
    fi
done
