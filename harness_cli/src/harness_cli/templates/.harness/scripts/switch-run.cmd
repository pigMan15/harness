@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0switch-run.ps1" %*
exit /b %ERRORLEVEL%
