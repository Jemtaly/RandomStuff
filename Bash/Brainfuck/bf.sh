#!/bin/bash
func=$(
    for ch in `test $# -gt 0 && sed 's/\s*/ /g' "$1" || sed 's/\s*/ /g'`
    do
        case $ch in
        '+')
            echo -n '((arr[ptr] = arr[ptr] == 255 ? 0 : arr[ptr] + 1)); '
            ;;
        '-')
            echo -n '((arr[ptr] = arr[ptr] == 0 ? 255 : arr[ptr] - 1)); '
            ;;
        '<')
            echo -n '((ptr = ptr == 0 ? 65535 : ptr - 1)); '
            ;;
        '>')
            echo -n '((ptr = ptr == 65535 ? 0 : ptr + 1)); '
            ;;
        '[')
            echo -n 'until [ -z ${arr[$ptr]} ] || [ ${arr[$ptr]} -eq 0 ]; do :; '
            ;;
        ']')
            echo -n 'done; '
            ;;
        ',')
            echo -n 'arr[$ptr]=`head -c1 | od -An -tu`; '
            ;;
        '.')
            echo -n 'printf %b \\`printf %03o ${arr[$ptr]}`; '
            ;;
        esac
    done | sed 's/^/ptr=0; /g'
)
stty=`stty -g`
stty -echo -icanon
eval $func
stty $stty
