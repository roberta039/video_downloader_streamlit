@echo off
cd /d "%~dp0"

echo Pornesc VideoDownloader.exe...
echo.

VideoDownloader.exe

echo.
echo Aplicatia s-a inchis.
echo Cod iesire: %ERRORLEVEL%
pause
