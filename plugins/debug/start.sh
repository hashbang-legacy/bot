#!/bin/bash
while read -r line
do
  echo $line | python3 -u -m json.tool 1>&2
done
