#!/usr/bin/env bash
#
# Deploy the hello_neopixel package to your ESP board.
# Assumes the MicroPython firmware is already installed
# and that the board is properly configured.

# Usage:
# $ sh delploy.sh [-p <port>]
#
# Arguments:
#   - p <port> : the port to connect over. Default is /dev/ttyUSB0
#

port=/dev/ttyUSB0
while getopts ":hp:" arg; do
  case ${arg} in
    h )
      echo "Usage:"
      echo "    sh delploy.sh [-p <port>]"
      exit 0
      ;;
    p )
      port=$OPTARG
      ;;
    : )
      echo "Option requires value: -$OPTARG" 1>&2
      exit 1
      ;;
    * )
      echo "Invalid Option: -$OPTARG" 1>&2
      exit 1
      ;;
  esac
done
python setup.py build
cd build/lib || exit
echo "Contents of file system:"
ampy --port "$port" ls || exit
ampy --port "$port" rmdir hello_neopixel
ampy --port "$port" put hello_neopixel
