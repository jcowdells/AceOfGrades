#!/bin/bash

HOST_ADDRESS="$(hostname -I | grep -o '^[^ ]*')"
if [ -z "${HOST_ADDRESS}" ]; then
    HOST_ADDRESS=127.0.0.1
fi
python3 -m flask run --host=$HOST_ADDRESS

read -p "Press any key to continue..."
