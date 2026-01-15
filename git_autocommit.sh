#!/bin/bash
set -e

# Repo dizini (logların olduğu yer)
REPO_DIR="/opt/tapo"

cd "$REPO_DIR"

# Değişiklik yoksa çık
if [[ -z "$(git status --porcelain)" ]]; then
  exit 0
fi

# Timestamp
TS=$(date "+%Y-%m-%d %H:%M:%S")

git add .
git commit -m "test-logs: auto commit @ $TS"
git push
