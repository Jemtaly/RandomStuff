#!/usr/bin/sh

begin() {
    sleep "$@" && echo "$@"
}

for it in "$@"; do
    begin "$it" &
done

wait
