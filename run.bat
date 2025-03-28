@echo off
:: Ultimate AI Assistant - Smart Launcher v2.2
:: Features: Auto-setup, dependency checks, config management, and seamless updates

title Ultimate AI Assistant Launcher
color 0A
cls

:: ADMIN CHECK (for system-level installs)
NET SESSION >nul 2>&1
if %errorlevel% == 0 (
    set ADMIN=true
) else (
    set ADMIN=false
)

:: CONFIGURATION
set PY_SCRIPT=ULTIMATE_AI_ASSISTANT_ENHANCED.py
set CONFIG_DIR=config
set DATA_DIR=data
set LOG_DIR=logs
set BACKUP_DIR=backups
set SCREENSHOT_DIR=screenshots
set MODULE_DIR=modules
set PLUGIN_DIR=plugins
set GITHUB_REPO=badman576/UltimateAIAssistant

:: CREATE FOLDER STRUCTURE
for %%d in ("%CONFIG_DIR%" "%DATA_DIR%" "%LOG_DIR%" "%BACKUP_DIR%" "%SCREENSHOT_DIR%" "%MODULE_DIR%" "%PLUGIN_DIR%") do (
    if not exist %%d mkdir %%d
)

:: CHECK PYTHON (with version validation)
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Installing Python 3.11...
    if "%ADMIN%"=="true" (
        winget install Python.Python.3.11
        setx PATH "%PATH%;%LOCALAPPDATA%\Programs\Python\Python311" /m
    ) else (
        echo [ERROR] Run as Administrator to auto-install Python
        pause
        exit /b
    )
)

:: ENHANCED DEPENDENCY CHECK
echo Checking dependencies...
pip install --upgrade pip >nul

:: Core dependencies
set DEPENDENCIES=pygame pyttsx3 speechrecognition wikipedia requests packaging pyautogui psutil python-dotenv

for %%p in (%DEPENDENCIES%) do (
    pip show %%p >nul 2>&1
    if %errorlevel% neq 0 (
        echo Installing %%p...
        pip install %%p
    )
)

:: CONFIGURATION MANAGEMENT
if not exist "%CONFIG_DIR%\settings.ini" (
    echo [DEFAULT] > "%CONFIG_DIR%\settings.ini"
    echo voice_speed = 165 >> "%CONFIG_DIR%\settings.ini"
    echo default_location = New York >> "%CONFIG_DIR%\settings.ini"
    echo autoupdate = True >> "%CONFIG_DIR%\settings.ini"
    echo log_level = INFO >> "%CONFIG_DIR%\settings.ini"
    echo user_title = Master >> "%CONFIG_DIR%\settings.ini"
)

if not exist "%CONFIG_DIR%\api_keys.ini" (
    echo [API_KEYS] > "%CONFIG_DIR%\api_keys.ini"
    echo weather = d70de62adec8ebd18f3725f26386c3d7 >> "%CONFIG_DIR%\api_keys.ini"
    echo youtube = YOUR_KEY_HERE >> "%CONFIG_DIR%\api_keys.ini"
)

:: ENHANCED AUTO-UPDATE SYSTEM
for /f "delims=" %%i in ('python -c "import configparser; c=configparser.ConfigParser(); c.read('config/settings.ini'); print(c['DEFAULT'].getboolean('autoupdate'))"') do (
    set AUTOUPDATE=%%i
)

if "%AUTOUPDATE%"=="True" (
    call :UPDATE_CHECK
)

:: RUN ASSISTANT WITH ERROR HANDLING
echo Starting Ultimate AI Assistant v2.0...
echo [%date% %time%] Session started >> "%LOG_DIR%\assistant.log"

:RETRY_LAUNCH
python "%PY_SCRIPT%" >> "%LOG_DIR%\assistant.log" 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Assistant crashed with code %errorlevel%
    choice /m "Retry launch?"
    if %errorlevel% equ 1 (
        goto RETRY_LAUNCH
    )
)

echo [%date% %time%] Session ended >> "%LOG_DIR%\assistant.log"
pause
exit /b

:UPDATE_CHECK
echo Checking for updates from GitHub...
python -c "import requests; r=requests.get('https://api.github.com/repos/%GITHUB_REPO%/releases/latest'); print(r.json()['tag_name'] if r.status_code==200 else '')" > latest_ver.tmp
set /p LATEST_VER=<latest_ver.tmp
del latest_ver.tmp

for /f "delims=" %%i in ('python -c "import ULTIMATE_AI_ASSISTANT_ENHANCED as ua; print(ua.__version__)"') do (
    set CURRENT_VER=%%i
)

if "%LATEST_VER%" gtr "%CURRENT_VER%" (
    echo New version %LATEST_VER% available!
    echo Current version: %CURRENT_VER%
    choice /m "Do you want to update now?"
    if %errorlevel% equ 1 (
        echo Creating backup...
        if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
        copy "%PY_SCRIPT%" "%BACKUP_DIR%\%PY_SCRIPT%.%CURRENT_VER%.bak"
        
        echo Downloading update...
        curl -L -o "%PY_SCRIPT%.new" "https://raw.githubusercontent.com/%GITHUB_REPO%/main/%PY_SCRIPT%"
        if exist "%PY_SCRIPT%.new" (
            :: Verify the download contains Python code
            findstr /i "import class def" "%PY_SCRIPT%.new" >nul
            if %errorlevel% equ 0 (
                del "%PY_SCRIPT%"
                ren "%PY_SCRIPT%.new" "%PY_SCRIPT%"
                echo Update complete! Launching new version...
                timeout /t 2 >nul
                start "" "%PY_SCRIPT%"
                exit
            ) else (
                echo [ERROR] Downloaded file appears corrupted
                del "%PY_SCRIPT%.new"
            )
        )
    )
) else (
    echo You're running the latest version (%CURRENT_VER%)
)
goto :EOF
