@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0validate-harness.ps1" %*
exit /b %ERRORLEVEL%
