import os
import sys
import time
import webbrowser
import threading
import traceback
from pathlib import Path


def get_base_dir():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent

    return Path(__file__).parent


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    return Path(__file__).parent / relative_path


BASE_DIR = get_base_dir()
LOG_FILE = BASE_DIR / "VideoDownloader_error.log"

# Pentru Playwright ambalat local
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"


def write_log_header():
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n\n==============================\n")
        f.write("Pornire VideoDownloader\n")
        f.write(f"Folder aplicatie: {BASE_DIR}\n")
        f.write(f"Python exe: {sys.executable}\n")
        f.write(f"Frozen: {getattr(sys, 'frozen', False)}\n")
        f.write("==============================\n")


def open_browser_later():
    time.sleep(3)
    webbrowser.open("http://localhost:8501")


if __name__ == "__main__":
    try:
        write_log_header()

        sys.stdout = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
        sys.stderr = sys.stdout

        import streamlit.web.cli as stcli

        app_path = resource_path("app.py")

        print(f"app.py path: {app_path}")
        print(f"app.py exists: {app_path.exists()}")

        if not app_path.exists():
            raise FileNotFoundError(f"Nu gasesc app.py la: {app_path}")

        threading.Thread(target=open_browser_later, daemon=True).start()

        sys.argv = [
            "streamlit",
            "run",
            str(app_path),
            "--server.headless=true",
            "--server.port=8501",
            "--browser.gatherUsageStats=false"
        ]

        sys.exit(stcli.main())

    except Exception:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write("\nEROARE:\n")
            f.write(traceback.format_exc())

        try:
            input(f"A aparut o eroare. Verifica fisierul: {LOG_FILE}\nApasa Enter pentru inchidere...")
        except Exception:
            pass
