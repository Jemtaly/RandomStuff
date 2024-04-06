#!/usr/bin/bash
port=4096
enc=""
while getopts ":p:e" opt; do
    case $opt in
    p)
        port="$OPTARG"
        ;;
    e)
        enc="--enc"
        ;;
    \?)
        echo "Invalid option: -$OPTARG" >&2
        ;;
    esac
done
python3 ./imftp.py --server localhost --port "$port" --chat $enc &
python3 ./imftp.py --client localhost --port "$port" --chat $enc &
wait
