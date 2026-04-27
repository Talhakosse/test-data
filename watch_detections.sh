#!/bin/bash

WATCH_DIR="/opt/fire/logs/detections"   # detection klasörün buysa değiştir
REPO_DIR="/opt/fire"

inotifywait -m -e close_write,create,moved_to "$WATCH_DIR" |
while read path action file; do
    cd "$REPO_DIR" || exit 1

    git add .

    if git diff --cached --quiet; then
        continue
    fi

    git commit -m "FİREEE Auto detection: $file - $(date '+%Y-%m-%d %H:%M:%S')"
    git push origin master
done
