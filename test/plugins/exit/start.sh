#!/bin/bash
read -r LINE
CMD=$(echo $LINE | json_pp | grep "^ ")
ARG=$(echo $CMD | cut -d\  -f 3)
case $CMD in
  *exit*) exit $ARG ;;
*stdout*) echo $ARG ;;
*stderr*) >&2 echo $ARG ;;
esac


