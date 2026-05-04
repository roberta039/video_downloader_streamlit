@echo off
title Build VideoDownloader EXE

echo ========================================
echo BUILD VIDEO DOWNLOADER STREAMLIT EXE
echo ========================================
echo.

echo [1/7] Stergere build vechi...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q VideoDownloader.spec 2>nul

echo.
echo [2/7] Creare venv...
python -m venv venv

echo.
echo [3/7] Activare venv...
call venv\Scripts\activate.bat

echo.
echo [4/7] Upgrade pip...
python -m pip install --upgrade pip

echo.
echo [5/7] Instalare dependinte...
pip install -r requirements.txt

echo.
echo [6/7] Instalare Chromium Playwright local...
set PLAYWRIGHT_BROWSERS_PATH=0
python -m playwright install chromium

echo.
echo [7/7] Build EXE cu PyInstaller...
pyinstaller ^
  --noconfirm ^
  --clean ^
  --onedir ^
  --console ^
  --name VideoDownloader ^
  --collect-all streamlit ^
  --collect-all playwright ^
  --add-data "app.py;." ^
  run_app.py

echo.
echo ========================================
echo BUILD TERMINAT
echo Aplicatia este in:
echo dist\VideoDownloader
echo ========================================
pause
