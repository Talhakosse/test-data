#!/usr/bin/env python3
import time
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
import psutil
import subprocess

# ---------------------------------------------------------
# LOG AYARLARI
# ---------------------------------------------------------
LOG_DIR = Path("/opt/tapo/logs")  # İstersen değiştir
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "system_monitor.log"

logger = logging.getLogger("system_monitor")
logger.setLevel(logging.INFO)

# Dosyaya dönen log (max 5 MB, 5 yedek)
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,
    backupCount=5,
    encoding="utf-8"
)

# Konsola da yazsın
console_handler = logging.StreamHandler()

fmt = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

file_handler.setFormatter(fmt)
console_handler.setFormatter(fmt)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


# ---------------------------------------------------------
# TEGRASTATS OKUMA (VARSA)
# ---------------------------------------------------------
def get_tegrastats_once():
    try:
        p = subprocess.Popen(
            ["tegrastats"],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        # 1 satır oku
        line = p.stdout.readline().strip()

        # hemen öldür
        p.terminate()

        return line
    except Exception as e:
        return f"tegrastats error: {e}"

def read_temperatures_sysfs():
    """
    Jetson thermal_zone sıcaklıklarını okur.
    /sys/devices/virtual/thermal/thermal_zone*/temp şeklinde çalışır.
    """
    import glob

    temp_data = {}
    zones = glob.glob("/sys/devices/virtual/thermal/thermal_zone*/")

    for z in zones:
        try:
            # label varsa oku
            label_file = Path(z) / "type"
            label = label_file.read_text().strip() if label_file.exists() else Path(z).name

            # sıcaklık
            temp_file = Path(z) / "temp"
            raw = temp_file.read_text().strip()
            temp_c = int(raw) / 1000  # genelde milideğer
            temp_data[label] = round(temp_c, 1)
        except:
            continue
  #  print(f"temp_data: {temp_data}")
    return temp_data

# ---------------------------------------------------------
# METRİK TOPLAMA
# ---------------------------------------------------------
def collect_metrics():
    # CPU
    cpu_total = psutil.cpu_percent(interval=1)  # 1 sn ölçüm
    cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)

    # RAM
    mem = psutil.virtual_memory()

    # SWAP
    swap = psutil.swap_memory()

    # Disk (/)
    disk_root = psutil.disk_usage("/")

    # Sıcaklıklar (destekliyorsa)
    temps_info = read_temperatures_sysfs()
    try:
        temps = psutil.sensors_temperatures()
        for name, entries in temps.items():
            temps_info[name] = [
                {"label": e.label, "current": e.current}
                for e in entries
            ]
    except (AttributeError, NotImplementedError):
         temps_info =read_temperatures_sysfs()

    # Tegrastats
    tegra = get_tegrastats_once()

    metrics = {
        "timestamp": datetime.now().isoformat(),
        "cpu_total_percent": cpu_total,
        "cpu_per_core_percent": cpu_per_core,
        "mem_total_mb": round(mem.total / (1024 ** 2), 1),
        "mem_used_mb": round(mem.used / (1024 ** 2), 1),
        "mem_percent": mem.percent,
        "swap_total_mb": round(swap.total / (1024 ** 2), 1),
        "swap_used_mb": round(swap.used / (1024 ** 2), 1),
        "swap_percent": swap.percent,
        "disk_root_total_gb": round(disk_root.total / (1024 ** 3), 2),
        "disk_root_used_gb": round(disk_root.used / (1024 ** 3), 2),
        "disk_root_percent": disk_root.percent,
        "temps": temps_info,
        "tegrastats": tegra,
    }

    return metrics


def format_metrics_for_log(m):
    parts = [
        f"CPU: {m['cpu_total_percent']}%  "
        f"(cores: {', '.join(f'{c}%' for c in m['cpu_per_core_percent'])})",

        f"MEM: {m['mem_used_mb']}/{m['mem_total_mb']} MB ({m['mem_percent']}%)",

        f"SWAP: {m['swap_used_mb']}/{m['swap_total_mb']} MB ({m['swap_percent']}%)",

        f"DISK /: {m['disk_root_used_gb']}/{m['disk_root_total_gb']} GB "
        f"({m['disk_root_percent']}%)",
    ]

    # --- Jetson sıcaklıkları (dict[str -> float]) ---
    if isinstance(m["temps"], dict) and m["temps"]:
        temp_strs = [f"{k}:{v}°C" for k, v in m["temps"].items()]
        parts.append("TEMP: " + ", ".join(temp_strs))

    # --- TegraStats ---
    if m["tegrastats"]:
        parts.append(f"TEGRASTATS: {m['tegrastats']}")

    return " | ".join(parts)



# ---------------------------------------------------------
# ANA DÖNGÜ (3 DK)
# ---------------------------------------------------------
def main():
    logger.info("System monitor basladi (3 dakikada bir ölçüm).")

    # 5 dk = 180 saniye
    interval_seconds = 180

    while True:
        try:
            metrics = collect_metrics()
            line = format_metrics_for_log(metrics)
            logger.info(line)
        except Exception as e:
            logger.exception(f"Metric toplarken hata: {e}")

        time.sleep(interval_seconds)


if __name__ == "__main__":
    main()
