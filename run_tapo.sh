#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/tapo"
ENV_FILE="${APP_DIR}/.env"
LEASE_FILE="/var/lib/misc/dnsmasq.leases"

# venv varsa PATH'e ekle
if [ -d "/home/fire/Desktop/tapo_last2/Tapo/OneDrive/Masaüstü/SanfireCode/Last2/tapo_fire_v2/venv/bin" ]; then
  export PATH="/home/fire/Desktop/tapo_last2/Tapo/OneDrive/Masaüstü/SanfireCode/Last2/tapo_fire_v2/venv/bin:$PATH"
fi

# .env varsa yükle
if [ -f "${ENV_FILE}" ]; then
  set -a
  source "${ENV_FILE}"
  set +a
fi

# CAM_IP yoksa lease dosyasından çek
CAM_IP=10.42.0.116
if [ -z "${CAM_IP}" ] && [ -f "${LEASE_FILE}" ]; then
  CAM_IP=$(awk '/dc:62:79:41:24:05/ {print $3}' "${LEASE_FILE}" | tail -n1 || true)
fi

if [ -z "${CAM_IP}" ]; then
  echo "HATA: CAM_IP bulunamadı. dnsmasq.leases içinde MAC satırı yok veya IP çözülemedi." >&2
  exit 1
fi

: "${TAPO_USER:?TAPO_USER yok}"
: "${TAPO_PASS:?TAPO_PASS yok}"

export RTSP_URL="rtsp://${TAPO_USER}:${TAPO_PASS}@${CAM_IP}:554/stream1"

cd /home/fire/tapo
exec python -u tapo_track_ptz_abs.py

