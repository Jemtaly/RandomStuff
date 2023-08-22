#!/bin/bash
for arg in "$@"; do
    case $arg in
    -t)
        TEST=1
        shift
        ;;
    -s)
        SILENT=1
        shift
        ;;
    *)
        break
        ;;
    esac
done
if [ $# -lt 2 ]; then
    echo "Usage: $0 [-t] [-s] <sed command> <file>..."
    exit 1
fi
CMD=$1
shift
for orig in "$@"; do
    dest=$(echo $orig | sed "$CMD")
    if [ "$orig" != "$dest" ]; then
        if [ -z "$SILENT" ]; then
            echo "$orig -> $dest"
        fi
        if [ -z "$TEST" ]; then
            mv "$orig" "$dest"
        fi
    fi
done
