#!/bin/sh
for x in $(ls /var/log/dpkg.log*); do
    zcat -f $x | tac | grep -e " install " -e " upgrade " -e " remove " -e " purge "
done | column -t
