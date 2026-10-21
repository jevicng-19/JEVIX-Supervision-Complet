"""JEVIX client agent. Configuration lives beside the script or executable."""

import argparse
import getpass
import json
import os
import platform
import socket
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import psutil
import requests


DEFAULT_INTERVAL_SECONDS = 5
CONFIG_FILENAME = "agent_config.json"


def application_directory():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def load_configuration(args):
    config_path = application_directory() / CONFIG_FILENAME
    config = {}
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"Configuration illisible ({config_path}) : {exc}")

    server_url = args.server_url or os.environ.get("JEVIX_SERVER_URL") or config.get("server_url")
    if not server_url:
        raise SystemExit(
            f"Adresse du serveur manquante. Renseignez server_url dans {config_path} "
            "ou lancez l'agent avec --server-url http://ADRESSE_DU_SERVEUR:5000/metrics."
        )

    parsed_url = urlparse(server_url)
    if parsed_url.scheme not in ("http", "https") or not parsed_url.hostname:
        raise SystemExit("server_url doit être une URL http:// ou https:// valide.")

    interval = config.get("interval_seconds", DEFAULT_INTERVAL_SECONDS)
    try:
        interval = max(1, int(interval))
    except (TypeError, ValueError):
        raise SystemExit("interval_seconds doit être un nombre entier positif.")
    return server_url, interval


def local_ip_for_server(server_url):
    parsed_url = urlparse(server_url)
    port = parsed_url.port or (443 if parsed_url.scheme == "https" else 80)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as connection:
            connection.connect((parsed_url.hostname, port))
            return connection.getsockname()[0]
    except OSError:
        return "Inconnue"


def collect_metrics(server_url):
    network = psutil.net_io_counters()
    battery = psutil.sensors_battery()
    ram = psutil.virtual_memory()
    system_drive = os.environ.get("SystemDrive", "C:")
    disk_path = system_drive + "\\" if platform.system() == "Windows" else "/"
    disk = psutil.disk_usage(disk_path)

    return {
        "hostname": socket.gethostname(),
        "username": getpass.getuser(),
        "ip": local_ip_for_server(server_url),
        "os": platform.system(),
        "os_version": platform.release(),
        "architecture": platform.machine(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "cpu_cores": psutil.cpu_count(),
        "ram_total_gb": round(ram.total / (1024 ** 3), 2),
        "ram_used_percent": ram.percent,
        "ram_available_gb": round(ram.available / (1024 ** 3), 2),
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "disk_used_percent": disk.percent,
        "disk_free_gb": round(disk.free / (1024 ** 3), 2),
        "bytes_sent": network.bytes_sent,
        "bytes_recv": network.bytes_recv,
        "process_count": len(psutil.pids()),
        "battery_percent": battery.percent if battery else None,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def main():
    parser = argparse.ArgumentParser(description="Agent de supervision JEVIX")
    parser.add_argument("--server-url", help="URL complète du endpoint /metrics")
    args = parser.parse_args()
    server_url, interval = load_configuration(args)

    while True:
        machine_info = collect_metrics(server_url)
        try:
            response = requests.post(server_url, json=machine_info, timeout=10)
            response.raise_for_status()
            print(f"[{machine_info['timestamp']}] Données envoyées - Code : {response.status_code}")
        except requests.exceptions.RequestException as exc:
            print(f"[{machine_info['timestamp']}] Envoi impossible : {exc}")
        time.sleep(interval)


if __name__ == "__main__":
    main()
