#!/bin/sh
for file in `ls ./??_*.rb`; do
  echo $file
  ruby $file
  echo
done
