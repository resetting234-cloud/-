@echo off
rem MeetionRC modpack installer (Windows)
rem Reads modpack.json and downloads every mod + resource pack from Modrinth
rem into per-version folders: 1.20.1\mods\, 1.20.1\resourcepacks\, etc.
rem
rem Usage:
rem   install.bat                      (install all versions)
rem   install.bat 1.21.8               (install only one version)
rem   install.bat 1.20.1 1.21.5        (install several)

setlocal
pushd "%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1" %*
set ERR=%ERRORLEVEL%

popd
endlocal & exit /b %ERR%
