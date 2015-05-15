exec luajit -e 'dofile"plugins/eval/sandbox.lua".protect()' -e "$@" 0>&-
