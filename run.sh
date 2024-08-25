#!/bin/bash

while true; do
    python bot.py
    if [ $? -ne 0 ]; then
        echo "Bot crashed with exit code $?. Restarting..." >&2
        sleep 1
    else
        break
    fi
done
