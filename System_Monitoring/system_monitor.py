#!/usr/bin/env python3
import time
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import subprocess

# ---------------------------------------------------------
# LOG AYARLARI
# ---------------------------------------------------------
LOG_DIR = Path("/opt/fire/logs") 
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "system_monitor.log"

logger = logging.getLogger("system_monitor")
logger.setLevel(logging.INFO)

# Dosyaya yazma ayarı: Max 5 MB, 5 yedek dosya 
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)

# İstediğin tarih formatı: 04-03-2026 13:04:02
fmt = logging.Formatter("%(asctime)s %(message)s", datefmt="%d-%m-%Y %H:%M:%S")
file_handler.setFormatter(fmt)

logger.addHandler(file_handler)

# ---------------------------------------------------------
# TEGRASTATS OKUMA
# ---------------------------------------------------------
def get_tegrastats_line():
    """
    Tegrastats çıktısını ham satır olarak yakalar.
    """
    try:
        # Jetson üzerinde tegrastats'ı bir anlık çalıştırıp ilk satırı alır
        process = subprocess.Popen(
            ["tegrastats"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True
        )
        line = process.stdout.readline().strip()
        process.terminate()
        return line
    except Exception as e:
        return f"Hata: {str(e)}"

# ---------------------------------------------------------
# ANA DÖNGÜ
# ---------------------------------------------------------
def main():
    # Döngü aralığı: 180 saniye (3 dakika) 
    interval = 600

    while True:
        try:
            raw_output = get_tegrastats_line()
            if raw_output:
                # Log dosyasına yazdırır
                logger.info(raw_output)
        except Exception as e:
            logger.error(f"Beklenmedik hata: {e}")

        time.sleep(interval)

if __name__ == "__main__":
    main()
