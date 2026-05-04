import os
import sys
import time
import webbrowser
import threading
import traceback
from pathlib import Path


VERSION = "RUN_APP_FIX_NO_PORT_2026_05_04"


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

# Incercam sa fortam Streamlit sa nu fie in development mode
os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"


def write_log_header():
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n\n==============================\n")
        f.write("Pornire VideoDownloader\n")
        f.write(f"Versiune: {VERSION}\n")
        f.write(f"Folder aplicatie: {BASE_DIR}\n")
        f.write(f"Python exe: {sys.executable}\n")
        f.write(f"Frozen: {getattr(sys, 'frozen', False)}\n")
        f.write("==============================\n")


def open_browser_later():
    time.sleep(4)
    webbrowser.open("http://localhost:8501")


if __name__ == "__main__":
    try:
        write_log_header()

        sys.stdout = open(LOG_FILE, "a", encoding="utf-8", buffering=1)
        sys.stderr = sys.stdout

        import streamlit.web.cli as stcli

        app_path = resource_path("app.py")

        print(f"Versiune run_app.py: {VERSION}")
        print(f"app.py path: {app_path}")
        print(f"app.py exists: {app_path.exists()}")

        if not app_path.exists():
            raise FileNotFoundError(f"Nu gasesc app.py la: {app_path}")

        threading.Thread(target=open_browser_later, daemon=True).start()

        sys.argv = [
            "streamlit",
            "run",
            str(app_path),
            "--global.developmentMode=false",
            "--server.headless=true",
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
