@echo off
rem SPDX-License-Identifier: MIT
rem dev-skills installer — Windows launcher. One implementation lives in install.sh;
rem this file only finds the bash that ships with Git for Windows and hands every
rem argument through unchanged, so cmd.exe, PowerShell, and a double-click all get
rem exactly the same install/--check/--status/--update/--uninstall behavior.
rem
rem   install.cmd                 same as ./install.sh
rem   install.cmd --status        same flags, same output
rem
rem Needs Git for Windows (https://git-scm.com/download/win) — the bash it installs
rem is the only requirement; no rsync, no WSL, no PowerShell modules.
setlocal
set "BASH="
for /f "delims=" %%G in ('where git.exe 2^>nul') do (
  if not defined BASH if exist "%%~dpG..\bin\bash.exe" set "BASH=%%~dpG..\bin\bash.exe"
)
if not defined BASH if exist "%ProgramFiles%\Git\bin\bash.exe" set "BASH=%ProgramFiles%\Git\bin\bash.exe"
if not defined BASH if exist "%LocalAppData%\Programs\Git\bin\bash.exe" set "BASH=%LocalAppData%\Programs\Git\bin\bash.exe"
if not defined BASH (
  echo Git for Windows was not found. Install it from https://git-scm.com/download/win and re-run.
  exit /b 1
)
"%BASH%" "%~dp0install.sh" %*
exit /b %ERRORLEVEL%
