@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo 🤖 Google ADK Tool Helper
echo ==========================================
echo.

:: Detect virtual environment
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment (.venv)...
    call .venv\Scripts\activate.bat
) else (
    echo [WARNING] .venv not found in the current directory.
    echo Make sure you are in the project root containing '.venv'.
    echo.
)

:menu
echo Please pick an ADK action:
echo  [1] Create a new Agent app (adk create)
echo  [2] Run Agent in CLI (adk run)
echo  [3] Start Agent Web UI (adk web)
echo  [4] Run Agent API Server (adk api_server)
echo  [5] Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto create_agent
if "%choice%"=="2" goto run_agent
if "%choice%"=="3" goto web_agent
if "%choice%"=="4" goto api_agent
if "%choice%"=="5" goto end
echo Invalid choice. Try again.
echo.
goto menu

:create_agent
set /p app_name="Enter the name/path of new Agent app (e.g. my_agent_3): "
if "%app_name%"=="" goto menu
echo Running: adk create %app_name%
call adk create %app_name%
echo.
goto menu

:run_agent
set /p app_name="Enter Agent app name to run (e.g. my_agent): "
if "%app_name%"=="" goto menu
echo Running: adk run %app_name%
call adk run %app_name%
echo.
goto menu

:web_agent
set /p app_name="Enter Agent app name for Web UI (e.g. my_agent): "
if "%app_name%"=="" goto menu
echo Running: adk web %app_name%
call adk web %app_name%
echo.
goto menu

:api_agent
set /p app_name="Enter Agent app name for API Server (e.g. my_agent): "
if "%app_name%"=="" goto menu
echo Running: adk api_server %app_name%
call adk api_server %app_name%
echo.
goto menu

:end
echo Goodbye!
pause
