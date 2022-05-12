#!/bin/bash
for file in "$@"
do
    tail -c1 "$file" | grep -aq '.' && echo -e '\r' >> "$file"
    sed -i 's/\r$//g' "$file"
done
