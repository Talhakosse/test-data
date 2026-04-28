#!/bin/bash
cd /opt/fire || exit 1

git add -f logs/

if git diff --cached --quiet; then
    exit 0
fi

git commit -m "Auto log update: $(date '+%Y-%m-%d %H:%M:%S')"
git push origin master --force
