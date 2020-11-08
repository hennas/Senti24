#!/bin/bash

# Code used to automate extraction of data for 2009-2017

echo "Starting automatic extraction process"
for ((i=2009;i<=2017;i=i+1)); do
  unzip -j suomi24-2001-2017-vrt-v1-1.zip "suomi24-2001-2017-vrt-v1-1/vrt/s24_$i.vrt" -d .
  python3 vrt_extract2.py "s24_$i.vrt"
  rm "s24_$i.vrt"
done
echo "Done!"
