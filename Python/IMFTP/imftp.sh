#!/usr/bin/bash
port=4096
enc=""
while getopts ":s:r:p:e" opt; do
    case $opt in
    s)
        send="$OPTARG"
        ;;
    r)
        recv="$OPTARG"
        ;;
    p)
        port="$OPTARG"
        ;;
    e)
        enc="--enc"
        ;;
    \?)
        echo "Invalid option -$OPTARG" >&2
        ;;
    esac
done
if [ -z "$send" ] || [ -z "$recv" ]; then
    echo "Usage: imftp.sh -s <send> -r <recv> [-p <port>] [-e]" >&2
    exit 1
fi
python3 ./imftp.py --server localhost --port "$port" --send "$send" $enc &
python3 ./imftp.py --client localhost --port "$port" --recv "$recv" $enc &
wait
if cmp -s "$send" "$recv"; then
    echo "Success!"
else
    echo "Failure!"
fi
