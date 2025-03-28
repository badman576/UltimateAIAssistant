@echo off
:: Ultimate AI Assistant - Intelligent Launcher
:: Version 2.1 - Auto-setup, update, and run

title Ultimate AI Assistant Launcher
color 0A
cls

:: ADMIN CHECK
NET SESSION >nul 2>&1
if %errorlevel% == 0 (
    set ADMIN=true
) else (
    set ADMIN=false
)

:: CONFIGURATION
set PY_SCRIPT=UltimateAIAssistant.py
set CONFIG_DIR=config
set DATA_DIR=data
set LOG_DIR=logs
set BACKUP_DIR=backups
set SCREENSHOT_DIR=screenshots
set MODULE_DIR=modules

:: CREATE FOLDER STRUCTURE
for %%d in ("%CONFIG_DIR%" "%DATA_DIR%" "%LOG_DIR%" "%BACKUP_DIR%" "%SCREENSHOT_DIR%" "%MODULE_DIR%") do (
    if not exist %%d mkdir %%d
)

:: CHECK PYTHON
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Installing Python 3.11...
    if "%ADMIN%"=="true" (
        winget install Python.Python.3.11
    ) else (
        echo [ERROR] Run as Administrator to auto-install Python
        pause
        exit /b
    )
)

:: CHECK DEPENDENCIES
echo Checking dependencies...
pip install --upgrade pip >nul
pip list | findstr "pygame pyttsx3 speechrecognition" >nul
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install pygame pyttsx3 speechrecognition wikipedia requests packaging pyautogui psutil python-dotenv
)

:: CHECK CONFIG FILES
if not exist "%CONFIG_DIR%\settings.ini" (
    echo [DEFAULT] > "%CONFIG_DIR%\settings.ini"
    echo voice_speed = 165 >> "%CONFIG_DIR%\settings.ini"
    echo default_location = New York >> "%CONFIG_DIR%\settings.ini"
    echo autoupdate = True >> "%CONFIG_DIR%\settings.ini"
    echo log_level = INFO >> "%CONFIG_DIR%\settings.ini"
)

if not exist "%CONFIG_DIR%\api_keys.ini" (
    echo [API_KEYS] > "%CONFIG_DIR%\api_keys.ini"
    echo weather = d70de62adec8ebd18f3725f26386c3d7 >> "%CONFIG_DIR%\api_keys.ini"
    echo youtube = YOUR_KEY_HERE >> "%CONFIG_DIR%\api_keys.ini"
)

:: AUTO-UPDATE CHECK
for /f "delims=" %%i in ('python -c "import configparser; c=configparser.ConfigParser(); c.read('config/settings.ini'); print(c['DEFAULT'].getboolean('autoupdate'))"') do (
    set AUTOUPDATE=%%i
)

if "%AUTOUPDATE%"=="True" (
    call :UPDATE_CHECK
)

:: RUN ASSISTANT
echo Starting Ultimate AI Assistant...
echo [%date% %time%] Starting >> "%LOG_DIR%\assistant.log"
python "%PY_SCRIPT%" >> "%LOG_DIR%\assistant.log" 2>&1
echo [%date% %time%] Session ended >> "%LOG_DIR%\assistant.log"

pause
exit /b

:UPDATE_CHECK
echo Checking for updates...
python -c "import requests; r=requests.get('https://api.github.com/repos/yourusername/UltimateAIAssistant/releases/latest'); print(r.json()['tag_name'] if r.status_code==200 else '')" > latest_ver.tmp
set /p LATEST_VER=<latest_ver.tmp
del latest_ver.tmp

for /f "delims=" %%i in ('python -c "import UltimateAIAssistant; print(UltimateAIAssistant.__version__)"') do (
    set CURRENT_VER=%%i
)

if "%LATEST_VER%" gtr "%CURRENT_VER%" (
    echo New version %LATEST_VER% available!
    echo Current version: %CURRENT_VER%
    choice /m "Do you want to update now"
    if %errorlevel% equ 1 (
        echo Creating backup...
        if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
        copy "%PY_SCRIPT%" "%BACKUP_DIR%\%PY_SCRIPT%.%CURRENT_VER%.bak"
        
        echo Downloading update...
        curl -L -o "%PY_SCRIPT%.new" https://raw.githubusercontent.com/yourusername/UltimateAIAssistant/main/UltimateAIAssistant.py
        if exist "%PY_SCRIPT%.new" (
            del "%PY_SCRIPT%"
            ren "%PY_SCRIPT%.new" "%PY_SCRIPT%"
            echo Update complete! Please restart the assistant.
            pause
            exit
        )
    )
)
goto :EOF