#!/usr/bin/bash

port=4096
enc=""
server=1
client=1

while getopts ":p:e:sc" opt; do
    case $opt in
    p)
        port="$OPTARG"
        ;;
    e)
        enc="--enc"
        ;;
    s)
        server=1
        client=
        ;;
    c)
        client=1
        server=
        ;;
    \?)
        echo "Invalid option: -$OPTARG" >&2
        ;;
    esac
done

if [ "$client" ]; then
    echo "Starting client on port $port"
    python3 ./imftp.py --client localhost --port "$port" --chat $enc &
fi
if [ "$server" ]; then
    echo "Starting server on port $port"
    python3 ./imftp.py --server localhost --port "$port" --chat $enc &
fi

wait
