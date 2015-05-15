#!/usr/bin/env bash
echo "PID:"
cat .connector.pid
if [[ -n $( xargs -a .connector.pid ps --no-headers ) ]]
then
  echo "Connector running."
else
  echo "Connector not running. starting."
  python3 connector.py >/dev/null 2>&1 &
  echo $! > .connector.pid
fi

./bot.py

