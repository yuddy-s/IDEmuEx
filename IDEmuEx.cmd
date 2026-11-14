@echo off
setlocal
pushd "%~dp0" || exit /b 1
where py >nul 2>&1
if errorlevel 1 (
    python -m idemu gui %*
) else (
    py -3 -m idemu gui %*
)
set "IDEMU_EX_EXIT=%errorlevel%"
if not "%IDEMU_EX_EXIT%"=="0" pause
popd
exit /b %IDEMU_EX_EXIT%
