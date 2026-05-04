@echo off
title Build VideoDownloader EXE

echo ========================================
echo BUILD VIDEO DOWNLOADER STREAMLIT EXE
echo ========================================
echo.

echo [1/6] Creare venv...
python -m venv venv

echo.
echo [2/6] Activare venv...
call venv\Scripts\activate.bat

echo.
echo [3/6] Upgrade pip...
python -m pip install --upgrade pip

echo.
echo [4/6] Instalare dependinte...
pip install -r requirements.txt

echo.
echo [5/6] Instalare Chromium Playwright in pachet local...
set PLAYWRIGHT_BROWSERS_PATH=0
python -m playwright install chromium

echo.
echo [6/6] Build EXE cu PyInstaller...
pyinstaller ^
  --noconfirm ^
  --clean ^
  --onedir ^
  --name VideoDownloader ^
  --collect-all streamlit ^
  --collect-all playwright ^
  --add-data "app.py;." ^
  run_app.py

echo.
echo ========================================
echo BUILD TERMINAT
echo Aplicatia este in folderul:
echo dist\VideoDownloader
echo ========================================
pause
