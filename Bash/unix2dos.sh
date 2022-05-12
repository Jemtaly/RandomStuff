#!/bin/bash
for file in "$@"
do
    sed -i 's/\r\?$/\r/g' "$file"
done
