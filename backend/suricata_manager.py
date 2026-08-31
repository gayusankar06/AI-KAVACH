import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

SURICATA_PORT = 5636
SURICATA_URL = f"http://127.0.0.1:{SURICATA_PORT}"
BACKEND_DIR = Path(__file__).resolve().parent
LITE_SERVER = BACKEND_DIR / "tools" / "suricata" / "suricata_server_lite.py"

_process = None


def _is_up():
    try:
        with urllib.request.urlopen(f"{SURICATA_URL}/health", timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def ensure_suricata_server():
    global _process
    if _is_up():
        return True
    if not LITE_SERVER.exists():
        return False
    try:
        _process = subprocess.Popen(
            [sys.executable, str(LITE_SERVER)],
            cwd=str(BACKEND_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    except Exception:
        return False
    for _ in range(20):
        time.sleep(0.5)
        if _is_up():
            return True
    return False


def stop_suricata_server():
    global _process
    if _process is not None:
        _process.terminate()
        _process = None