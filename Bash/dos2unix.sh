#!/bin/sh
for file in "$@"
do
    sed -i 's/\r$//g' "$file"
    last=`tail -c1 "$file" | od -An -tu`
    test ! -z $last && test $last -ne 10 && echo >>"$file"
done
