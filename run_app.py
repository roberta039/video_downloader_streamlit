import os
import sys
from pathlib import Path

# Important pentru Playwright ambalat cu browser local
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path

    return Path(__file__).parent / relative_path


if __name__ == "__main__":
    import streamlit.web.cli as stcli

    app_path = resource_path("app.py")

    sys.argv = [
        "streamlit",
        "run",
        str(app_path),
        "--server.headless=false",
        "--server.port=8501",
        "--browser.gatherUsageStats=false"
    ]

    sys.exit(stcli.main())
