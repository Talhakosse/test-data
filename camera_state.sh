#!/bin/bash

CAM_IP="192.168.10.2"
STATE_FILE="/opt/fire/logs/detections/camera_state.txt"

LAST=""

while true; do
    if ping -c 1 -W 1 "$CAM_IP" >/dev/null 2>&1; then
        NOW="ACTIVE"
    else
        NOW="DEACTIVE"
    fi

    if [ "$NOW" != "$LAST" ]; then
        echo "$NOW" > "$STATE_FILE"
        LAST="$NOW"
    fi

    sleep 2
done
