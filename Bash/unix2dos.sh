#!/bin/bash
for file in "$@"
do
    sed -i 's/$/\r/g' "$file"
    last=`tail -c1 "$file" | od -An -tu`
    test ! -z $last && test $last -eq 13 && echo >>"$file"
done
