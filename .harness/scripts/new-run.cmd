@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0new-run.ps1" %*
exit /b %ERRORLEVEL%
