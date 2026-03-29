#!/bin/bash
set -e

REPO_DIR="/opt/tapo/logs"
WATCH_DIR="/opt/tapo/logs/detections"
LOCK_FILE="/tmp/fire_git.lock"

cd "$REPO_DIR"

inotifywait -m -e create --format "%f" "$WATCH_DIR" | while read FILE
do
  # Sadece resimler
  if [[ "$FILE" =~ \.(jpg|jpeg|png)$ ]]; then

    # Cron ile çakışmayı önle
    (
      flock -n 9 || exit 0

      TS=$(date "+%Y-%m-%d %H:%M:%S")

      git add .
      git commit -m "🔥 FIRE DETECTED: $FILE @ $TS" || exit 0
      git push

    ) 9>"$LOCK_FILE"

  fi
done
