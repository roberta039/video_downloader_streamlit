import os
import sys
import time
import webbrowser
import threading
from pathlib import Path


VERSION = "NO_PORT_FIX_2026_05_04"


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    return Path(__file__).parent / relative_path


os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"
os.environ["STREAMLIT_GLOBAL_DEVELOPMENT_MODE"] = "false"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"


def open_browser_later():
    time.sleep(4)
    webbrowser.open("http://localhost:8501")


if __name__ == "__main__":
    print(f"VideoDownloader launcher version: {VERSION}")

    import streamlit.web.cli as stcli

    app_path = resource_path("app.py")

    print(f"app.py path: {app_path}")
    print(f"app.py exists: {app_path.exists()}")

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
