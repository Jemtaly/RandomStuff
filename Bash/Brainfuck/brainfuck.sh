#!/bin/bash
func=$(
    for ch in `test $# -gt 0 && sed 's/\s*/ /g' "$1" || sed 's/\s*/ /g'`
    do
        case $ch in
            '+') echo -n '((arr[$ptr]++)); '
        ;;
            '-') echo -n '((arr[$ptr]--)); '
        ;;
            '<') echo -n '((ptr--)); '
        ;;
            '>') echo -n '((ptr++)); '
        ;;
            '[') echo -n 'until [ -z ${arr[$ptr]} ] || [ `expr ${arr[$ptr]} % 256` -eq 0 ]; do :; '
        ;;
            ']') echo -n 'done; '
        ;;
            ',') echo -n 'arr[$ptr]=`head -c1 | od -An -tu`; '
        ;;
            '.') echo -n 'printf %b \\`printf %03o ${arr[$ptr]}`; '
        esac
    done | sed 's/^/ptr=0; /g'
)
stty=`stty -g`
stty -echo -icanon
eval $func
stty $stty
