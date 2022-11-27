#!/bin/sh
for x in `ls /var/log/dpkg.log*`
do
    zcat -f $x | tac | grep -e " install " -e " upgrade " -e " remove " -e " purge "
done | awk -F ":a" '{print $1 " :a" $2}' | column -t
