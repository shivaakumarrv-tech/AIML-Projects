@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Customer Intelligence and Support Copilot

echo ============================================================
echo  Customer Intelligence ^& Support Copilot - Local startup
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python was not found on PATH.
  echo Install Python 3.10 or newer and select "Add Python to PATH".
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo [1/6] Creating virtual environment...
  python -m venv .venv
  if errorlevel 1 goto failed
) else (
  echo [1/6] Reusing existing virtual environment.
)
set "PY=%CD%\.venv\Scripts\python.exe"

echo.
echo [2/6] Updating pip...
"%PY%" -m pip install --upgrade pip
if errorlevel 1 goto failed

echo.
echo [3/6] Installing project requirements...
if exist "requirements.txt" (
  "%PY%" -m pip install -r requirements.txt
  if errorlevel 1 goto failed
) else (
  echo WARNING: requirements.txt not found; continuing with frontend requirements.
)

echo.
echo [4/6] Installing Streamlit and frontend requirements...
"%PY%" -m pip install -r requirements_frontend.txt
if errorlevel 1 goto failed

if not exist "generate_data.py" (
  echo ERROR: generate_data.py is missing from the project root.
  goto failed
)
if not exist "mock_llm.py" (
  echo ERROR: mock_llm.py is missing from the project root.
  goto failed
)

if not exist "data\raw" mkdir "data\raw"
set "NEED_DATA=0"
for %%F in (customers.csv orders.csv products.csv tickets.csv policy_eval.csv) do (
  if not exist "data\raw\%%F" set "NEED_DATA=1"
)
set "NEED_POLICIES=0"
if not exist "data\policies\*.txt" set "NEED_POLICIES=1"
if not exist "notebooks\data\policies\*.txt" set "NEED_POLICIES=1"
if "%NEED_DATA%"=="1" (
  echo.
  echo [5/6] Raw data missing or incomplete. Generating CSV and policy files...
) else if "%NEED_POLICIES%"=="1" (
  echo.
  echo [5/6] Raw CSV files exist, but one or both policy folders are incomplete.
  echo Running generator to create or mirror policy documents...
) else (
  echo.
  echo [5/6] Raw CSV files and both policy folders are complete; generation skipped.
)
if "%NEED_DATA%"=="1" goto clear_readonly
if "%NEED_POLICIES%"=="1" goto clear_readonly
goto data_ready

:clear_readonly
rem The generator rewrites every CSV when it runs, so clear read-only attributes first.
rem This cannot unlock a file held open by Excel or another program.
attrib -R "data\raw\*.csv" /S /D >nul 2>nul
attrib -R "data\policies\*.txt" /S /D >nul 2>nul
attrib -R "notebooks\data\policies\*.txt" /S /D >nul 2>nul

:run_generator
"%PY%" -u generate_data.py
if errorlevel 1 (
  echo.
  echo DATA GENERATION FAILED.
  echo If PermissionError mentions a CSV, close it in Excel or another program,
  echo check folder permissions, then run START_PROJECT.bat again.
  goto failed
)

:data_ready

if not exist "data\policies\*.txt" (
  echo ERROR: No generated policy documents found in data\policies.
  goto failed
)
if not exist "notebooks\data\policies" mkdir "notebooks\data\policies"

echo.
echo [6/6] Starting Streamlit...
echo Browser address: http://localhost:8501
echo Keep this window open while using the app. Press CTRL+C to stop.
echo.
"%PY%" -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
if errorlevel 1 goto failed
exit /b 0

:failed
echo.
echo Startup stopped. Read the error above and follow README.md troubleshooting.
pause
exit /b 1
