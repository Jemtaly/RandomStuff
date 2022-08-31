#!/bin/bash
push() {
    sleep "$@" && echo "$@"
}
for i in "$@"
do
    push "$i" &
done
wait
