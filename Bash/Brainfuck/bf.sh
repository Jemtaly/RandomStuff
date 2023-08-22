#!/bin/bash
if [ $# -ne 1 ]; then
    echo "Usage: $0 <file>"
    exit 1
fi
func=$(
    for ch in $(sed 's/\s*/ /g' "$1"); do
        case $ch in
        '+')
            echo -n '((arr[ptr] = arr[ptr] + 1 & 255)); '
            ;;
        '-')
            echo -n '((arr[ptr] = arr[ptr] - 1 & 255)); '
            ;;
        '<')
            echo -n '((ptr = ptr - 1 & 65535)); '
            ;;
        '>')
            echo -n '((ptr = ptr + 1 & 65535)); '
            ;;
        '[')
            echo -n 'until ((arr[ptr] == 0)); do :; '
            ;;
        ']')
            echo -n 'done; '
            ;;
        ',')
            echo -n 'arr[$ptr]=$(head -c1 | od -An -tu); '
            ;;
        '.')
            echo -n 'printf %b \\x$(printf %02x ${arr[$ptr]}); '
            ;;
        esac
    done | sed 's/^/unset arr ptr; /'
)
stty=$(stty -g 2>/dev/null)
stty -echo -icanon &>/dev/null
eval $func
stty $stty &>/dev/null
